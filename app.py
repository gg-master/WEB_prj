import os
import pprint
from datetime import datetime, timedelta
from requests import get, put, post, delete
from flask import Flask, render_template, request, redirect
# from flask_ngrok import run_with_ngrok
from flask_restful import Api
from forms.film import FilmForm
from api import films_resource, films_api, film_session_resource
from data import db_session
from data.films import Film
from sqlalchemy.orm import Session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from data.db_session import SqlAlchemyBase
from data.film_sessions import FilmSession

app = Flask(__name__)
api = Api(app)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


app.config['DEBUG'] = True


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
                           films=films, filter=filter_dct, filtered=False,
                           **films_api.get_films_recommendations().json)


@app.route('/films/<int:film_id>', methods=['GET'])
def film_description(film_id):
    return render_template('film_description.html',
                           **films_resource.FilmResource().get(film_id).json)


@app.route('/timetable/<int:film_id>', methods=['GET'])
def timetable(film_id):
    print()
    btn_day_active = 1
    if request.args:
        btn_day_active = int([i for i in request.args][0])
    today = datetime.now().date()
    weekdays = {
        1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота',
        6: 'Воскресенье', 0: 'Понедельник'}
    today = {'today': today, 'weekdays': weekdays,
             'day_delta': timedelta(days=1)}
    db_sess = db_session.create_session()
    film = db_sess.query(Film).filter(Film.id == film_id).first()
    return render_template('timetable.html', today=today, film=film,
                           btn_day_active=btn_day_active)


def main():
    db_session.global_init("db/database.db")
    admin = Admin(app)
    db_sess = db_session.create_session()
    admin.add_view(ModelView(FilmSession, db_sess))
    admin.add_view(ModelView(Film, db_sess))
    app.register_blueprint(films_api.blueprint)
    api.add_resource(films_resource.FilmResource,
                     '/api/films/<int:film_id>')
    api.add_resource(films_resource.FilmListResource, '/api/films')
    api.add_resource(film_session_resource.FilmSessionResource, '/api/film_sessions/<int:film_sess_id>')
    api.add_resource(film_session_resource.FilmSessionListResource, '/api/film_sessions')
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()


if __name__ == '__main__':
    main()
