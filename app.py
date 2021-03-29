import locale
import os
import pprint
import pymorphy2
import threading
from datetime import datetime, timedelta

import requests
from flask import Flask, render_template, request, session
from flask_ngrok import run_with_ngrok
from flask_restful import Api

from api import films_resource, films_api, film_session_resource
from api.film_session_resource import FilmSessionResource
from api.films_resource import FilmResource
from data import db_session
from data.film_sessions import FilmSession
from data.films import Film
from modules import send_email

app = Flask(__name__)
api = Api(app)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


# app.config['DEBUG'] = True


@app.route('/', methods=['GET', "POST"])
def start_page():
    # Инициализация сессии к бд
    # Получение списка фильмов
    filter_dct = films_api.get_filter_data().json['filter_data']
    if request.method == 'POST':
        films = films_api.get_filtered_films().json['films']
        return render_template(
            'index.html', films=films, filter=filter_dct, filtered=True)
    films = films_resource.FilmListResource().get().json['films']
    return render_template('index.html',
                           films=films, filter=filter_dct, title='FilmCenter',
                           filtered=False,
                           **films_api.get_films_recommendations().json)


@app.route('/films/<int:film_id>', methods=['GET'])
def film_description(film_id):
    # Отрисовываем экран с описанием фильма
    return render_template('film_description.html', title='Описание фильма',
                           **films_resource.FilmResource().get(film_id).json)


@app.route('/timetable/<int:film_id>', methods=['GET', 'POST'])
def timetable(film_id):
    locale.setlocale(locale.LC_ALL, "ru_Ru")
    btn_day_active = 1
    if request.args:
        btn_day_active = int([i for i in request.args][0])
    today = datetime.now().date()
    days_data = {'today': today, 'day_delta': timedelta(days=1)}
    db_sess = db_session.create_session()
    film = db_sess.query(Film).filter(Film.id == film_id).first()
    # Узнаем выбранный день, прибавив к текущей дате номер кнопки
    current_date = today + timedelta(days=btn_day_active - 1)
    film_sess = list(filter(lambda f: f.start_time.date() == current_date,
                            db_sess.query(FilmSession).filter(
                                FilmSession.film_id == film.id).all()))
    if request.method == "POST":
        make_order()
    return render_template('timetable.html', title='Расписание',
                           today=days_data, film=film,
                           btn_day_active=btn_day_active,
                           film_session=film_sess,
                           special_mess=(request.method == 'POST'))


@app.route('/order/hallplan/<int:session_id>', methods=["GET", 'POST'])
def hallplan(session_id):
    locale.setlocale(locale.LC_ALL, "ru_Ru")
    db_sess = db_session.create_session()
    # Получение объекта сеанса и фильма для более удобной работы с объектами
    sess = db_sess.query(FilmSession).filter(
        FilmSession.id == session_id).first()
    film = db_sess.query(Film).filter(Film.id == sess.film_id).first()
    # Установка некоторых кукки
    session['session_id'] = sess.id
    # Создание словаря с параметрами для шаблона
    params = {'session': sess, 'film': film}
    if request.method == 'POST' and request.form:
        # Узнаем какие номера билетов имеются
        arr = [i for i in request.form
               if request.form.get(i) in ('label', 'on')]
        # Удаляем билеты, на которые пользователь нажал кнопкой мыши
        deleted_item = [i for i in request.form if request.form.get(i) == i]
        arr = list(filter(lambda x: x not in deleted_item, arr))
        # Если билетов больше нет, то открываем экран с выбором мест
        if not arr:
            return render_template('hallplan.html', navbar_title='Выбор мест',
                                   prev_win=f'/timetable/{film.id}',
                                   modal_alert=False, params=params)
        # Склоняем слово "билет"
        morph = pymorphy2.MorphAnalyzer()
        params['ticket_w'] = morph.parse('билет')[
            0].make_agree_with_number(len(arr)).word
        # Отрисовываем экран с отображением
        # всех билетов и их итоговой стоимости
        return render_template('last_order_stage.html',
                               navbar_title='Подтверждение покупки',
                               prev_win=f'/order/hallplan/{sess.id}',
                               selected_places=arr, params=params)
    # Отрисовка экрана с выбором места в зале
    return render_template('hallplan.html', navbar_title='Выбор мест',
                           prev_win=f'/timetable/{film.id}', params=params,
                           modal_alert=(request.method == 'POST'))


def make_order():
    film_session = FilmSessionResource().get(
        session.get('session_id')).json['film_sess']
    film = FilmResource().get(film_session['film_id']).json['film']
    places = [i for i in request.form if request.form.get(i) == 'label']
    list_places_in_db = list(film_session['places'])
    for i in places:
        row, col = i.split('-')
        number_place = ((int(row) - 1) * 20) + (int(col) - 1)
        list_places_in_db[number_place] = '1'
    db_threading = threading.Thread(
        target=requests.put,
        args=(f'http://localhost:5000/api/film_sessions/{film_session["id"]}',
              {'film_id': film_session["film_id"],
               'hall_id': film_session['hall_id'],
               'start_time': film_session['start_time'],
               'end_time': film_session['end_time'],
               'places': ''.join(list_places_in_db),
               'price': film_session['price']}))
    db_threading.start()
    params = {
        'number_places': places,
        'film_title': film['title'],
        'hall_id': film_session['hall_id'],
        'time_start': film_session['start_time'],
        'time_end': film_session['end_time'],
        'phone': '+7 (8442) 93-52-52',
        'msg-text': 'Ваши билеты, заказанные на сайте FilmCenter.'
                    '\nНа это письмо не нужно отвечать.'
    }
    send_thread = threading.Thread(
        target=send_email.send_mail,
        args=(request.form.get('email'), params,))
    send_thread.start()


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(films_api.blueprint)
    api.add_resource(films_resource.FilmResource,
                     '/api/films/<int:film_id>')
    api.add_resource(films_resource.FilmListResource, '/api/films')
    api.add_resource(film_session_resource.FilmSessionResource,
                     '/api/film_sessions/<int:film_sess_id>')
    api.add_resource(film_session_resource.FilmSessionListResource,
                     '/api/film_sessions')
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()


if __name__ == '__main__':
    main()
