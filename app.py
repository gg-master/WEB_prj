import locale
import os
import pprint
from datetime import datetime, timedelta

from flask import Flask, render_template, request
# from flask_ngrok import run_with_ngrok
from flask_restful import Api

from api import films_resource, films_api, film_session_resource
from data import db_session
from data.film_sessions import FilmSession
from data.films import Film

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
    return render_template('film_description.html', title='Описание фильма',
                           **films_resource.FilmResource().get(film_id).json)


@app.route('/timetable/<int:film_id>', methods=['GET'])
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
    return render_template('timetable.html', title='Расписание',
                           today=days_data, film=film,
                           btn_day_active=btn_day_active,
                           film_session=film_sess)


@app.route('/order/hallplan/<int:session_id>', methods=["GET", 'POST'])
def hallplan(session_id):
    locale.setlocale(locale.LC_ALL, "ru_Ru")
    db_sess = db_session.create_session()
    sess = db_sess.query(FilmSession).filter(
        FilmSession.id == session_id).first()
    film = db_sess.query(Film).filter(Film.id == sess.film_id).first()
    if request.method == 'POST':
        print([i for i in request.form])
        print([i for i in request.args])
        return render_template('last_order_stage.html',
                               navbar_title='Подтверждение покупки',
                               session=sess, film=film,
                               prev_win=f'/order/hallplan/{sess.id}')
    return render_template('hallplan.html', session=sess, film=film,
                           navbar_title='Выбор мест',
                           prev_win=f'/timetable/{film.id}')


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
