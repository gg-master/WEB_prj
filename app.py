import locale
import os
import pprint
import pymorphy2
import threading
from waitress import serve
from datetime import datetime, timedelta
from requests import get, put, post, delete
from flask import Flask, render_template, request, redirect
# from flask_ngrok import run_with_ngrok
import random
import string
import requests
from flask import Flask, render_template, request, session
from flask_ngrok import run_with_ngrok
from flask_restful import Api
from wtforms.validators import DataRequired
from data.places import Place
from api.film_session_resource import FilmSessionResource
from api.films_resource import FilmResource
from forms.film import FilmForm
from api import films_resource, films_api, film_session_resource
from data import db_session
from data.films import Film
from data.associations import Genre
from data.images import Image
from sqlalchemy.orm import Session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from data.db_session import SqlAlchemyBase
from data.film_sessions import FilmSession
from flask_babelex import Babel
from flask_admin.contrib.fileadmin import FileAdmin
from flask import Markup

from modules import send_email

app = Flask(__name__)
api = Api(app)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
babel = Babel(app)


# app.config['DEBUG'] = True


@app.route('/add_film', methods=['GET', 'POST'])
def add_film():
    form = FilmForm()
    if form.validate_on_submit():
        data = {'title': form.title.data, 'rating': form.rating.data,
                'actors': form.actors.data, 'producer': form.producer.data,
                'premiere': form.premiere.data.strftime('%Y-%m-%d'),
                'duration': form.duration.data,
                'description': form.description.data,
                'poster_url': form.poster_url.data,
                'trailer_url': form.trailer_url.data, 'watchers': 0,
                'images': form.images.data.split(', '),
                'genres': form.genres.data.split(', ')}
        print(form.genres.data.split(', '))
        post('http://localhost:5000/api/films', json=data)
        return redirect("/")
    return render_template("film_form.html", title="Добавление фильма",
                           form=form)


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
    places = db_sess.query(Place).filter(
        Place.film_session_id == sess.id).all()
    film = db_sess.query(Film).filter(Film.id == sess.film_id).first()
    # Установка некоторых кукки
    session['session_id'] = sess.id
    # Создание словаря с параметрами для шаблона
    params = {'session': sess, 'film': film, 'places': places}
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


@app.route('/make_schedule', methods=['POST'])
def create_schedule():
    print('Yahoo')
    print([i for i in request.values])
    return redirect('/admin/filmsession/')


def make_order():
    db_sess = db_session.create_session()
    # Получение сеанса фильма
    film_session = FilmSessionResource().get(
        session.get('session_id')).json['film_sess']
    # Получение фильма
    film = FilmResource().get(film_session['film_id']).json['film']
    # Узнаем выбранные места из запроса
    places = [i for i in request.form if request.form.get(i) == 'label']
    # Получение всех мест для сессии
    list_places_in_db = db_sess.query(Place).filter(
        Place.film_session_id == film_session['id']).all()
    places_dct = {}
    # Перебираем все выбранные места и измением статус места
    for i in places:
        row, col = list(map(int, i.split('-')))
        place = list(filter(lambda place_db:
                            place_db.row_id == row and place_db.seat_id == col,
                            list_places_in_db))[0]
        place.status = True
        places_dct[i] = place.code
    # Коммитим изменения
    db_sess.commit()
    params = {
        'places': places_dct,
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


class FilmView(ModelView):
    can_view_details = True
    column_searchable_list = ['title', 'rating', 'actors', 'producer',
                              'premiere', 'duration', 'description']
    column_filters = ['title', 'rating', 'premiere', 'duration']
    form_excluded_columns = ['film_session']
    inline_models = [(Image, dict(form_columns=['id', 'image_url']))]


    def _description_formatter(view, context, model, name):
        return model.description[:20]

    def _actors_formatter(view, context, model, name):
        return model.actors.split(', ')[0]

    def _poster_url_formatter(view, context, model, name):
        if model.poster_url:
            markupstring = f"<a href='{model.poster_url}'>link</a>"
            return Markup(markupstring)
        else:
            return ""

    def _trailer_url_formatter(view, context, model, name):
        if model.trailer_url:
            markupstring = f"<a href='{model.trailer_url}'>link</a>"
            return Markup(markupstring)
        else:
            return ""


    column_formatters = {
        'actors': _actors_formatter,
        'description': _description_formatter,
        'poster_url': _poster_url_formatter,
        'trailer_url': _trailer_url_formatter
    }


class FilmSessionView(ModelView):
    can_view_details = True
    column_searchable_list = ['film_id', 'hall_id', 'start_time', 'end_time',
                              'price']
    column_filters = ['film_id', 'hall_id', 'start_time', 'end_time', 'price']
    list_template = 'film_session.html'

    def after_model_change(self, form, model, is_created):
        db_sess = db_session.create_session()
        symbols = list(string.ascii_uppercase + string.digits)
        for i in range(1, 7):
            for j in range(1, 21):
                place = Place(
                    film_session_id=model.id,
                    row_id=i,
                    seat_id=j,
                    status=False,
                    code=''.join(random.sample(symbols, 6))
                )
                db_sess.add(place)
                db_sess.commit()


class PlaceView(ModelView):
    can_view_details = True
    column_searchable_list = ['film_session_id', 'row_id', 'seat_id',
                              'status']
    column_filters = ['film_session_id', 'row_id', 'seat_id', 'status']
    page_size = 20


def main():
    path = os.path.join(os.path.dirname(__file__), 'static')
    db_session.global_init("db/database.db")
    admin = Admin(app)
    db_sess = db_session.create_session()
    admin.add_view(FilmSessionView(FilmSession, db_sess, category='Sessions'))
    admin.add_view(PlaceView(Place, db_sess, category='Sessions'))
    admin.add_view(FilmView(Film, db_sess, category='Film'))
    admin.add_view(ModelView(Genre, db_sess, category='Film'))
    admin.add_view(ModelView(Image, db_sess, category='Film'))
    admin.add_view(FileAdmin(path, '/static/', name='Static Files'))
    app.register_blueprint(films_api.blueprint)
    api.add_resource(films_resource.FilmResource,
                     '/api/films/<int:film_id>')
    api.add_resource(films_resource.FilmListResource, '/api/films')
    api.add_resource(film_session_resource.FilmSessionResource,
                     '/api/film_sessions/<int:film_sess_id>')
    api.add_resource(film_session_resource.FilmSessionListResource,
                     '/api/film_sessions')
    port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    # app.run()
    serve(app, host='0.0.0.0', port=port)


@babel.localeselector
def get_locale():
    # Put your logic here. Application can store locale in
    # user profile, cookie, session, etc.
    return 'ru'


if __name__ == '__main__':
    main()
