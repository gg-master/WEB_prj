import math
import random

from flask_ngrok import run_with_ngrok
from flask_login import login_user, LoginManager, login_required, \
    logout_user, current_user
import os
import logging
import pymorphy2
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, session, redirect, g
from flask_restful import Api
from data.places import Place
from forms.admin import LoginForm
from api import films_resource, films_api, film_session_resource
from data import db_session
from data.films import Film
from data.images import Image
from data.associations import Genre
from data.admins import AdminRole
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from data.film_sessions import FilmSession
from flask_babelex import Babel
from babel.dates import format_datetime

from modules.admin_views import FilmSessionView, PlaceView, FilmView, \
    AdminRoleView, AdminView
from modules.make_order import make_order

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

app = Flask(__name__)
api = Api(app)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
# app.config['DEBUG'] = True

login_manager = LoginManager()
login_manager.init_app(app)

babel = Babel(app)


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
    btn_day_active = 1
    if request.args:
        btn_day_active = int([i for i in request.args][0])
    today = datetime.now()
    days_data = {'today': today, 'day_delta': timedelta(days=1)}
    film = g.db.query(Film).filter(Film.id == film_id).first()
    # Узнаем выбранный день, прибавив к текущей дате номер кнопки
    current_date = today.date() + timedelta(days=btn_day_active - 1)
    film_sess = list(filter(lambda f: f.start_time.date() == current_date,
                            g.db.query(FilmSession).filter(
                                FilmSession.film_id == film.id).all()))
    if request.method == "POST":
        make_order()
    return render_template('timetable.html', title='Расписание',
                           today=days_data, film=film,
                           btn_day_active=btn_day_active,
                           film_session=film_sess, locate=format_datetime,
                           special_mess=(request.method == 'POST'))


@app.route('/order/hallplan/<int:session_id>', methods=["GET", 'POST'])
def hallplan(session_id):
    # Получение объекта сеанса и фильма для более удобной работы с объектами
    sess = g.db.query(FilmSession).filter(
        FilmSession.id == session_id).first()
    film = g.db.query(Film).filter(Film.id == sess.film_id).first()
    # Установка некоторых кукки
    session['session_id'] = sess.id
    # Создание словаря с параметрами для шаблона
    params = {'session': sess, 'film': film, 'places': sess.s_places,
              'locate': format_datetime}
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
    current_day = datetime.combine(date.today(), datetime.min.time())
    day = timedelta(days=1)
    current_time = timedelta(hours=10, minutes=0)
    while g.db.query(FilmSession).filter(FilmSession.start_time >=
                                         current_day).first():
        current_day += day
    for day in range(7):
        for hall in range(1, 5):
            while current_time < timedelta(hours=22):
                film_id = random.randrange(1, 24)
                film = g.db.query(Film).filter(Film.id ==
                                               film_id).first()
                if not film:
                    continue
                # print(film_id)
                # print(film.duration)
                hours, minutes = divmod(math.ceil(film.duration / 30) * 30, 60)
                sess_duration = timedelta(hours=hours, minutes=minutes)
                fs = FilmSession()
                fs.film_id = film.id
                fs.hall_id = hall
                fs.start_time = current_day + current_time
                fs.end_time = current_day + current_time + sess_duration
                fs.price = 250
                g.db.add(fs)
                # print('Current time before:  ', current_time)
                current_time += sess_duration
                # print('Current time after:  ', current_time)
            current_time = timedelta(hours=10, minutes=0)
        current_day.replace(hour=0, minute=0)
        current_day += timedelta(days=1)
        g.db.commit()
    return redirect('/admin/filmsession/')


@app.route('/continue_schedule', methods=['POST'])
def continue_schedule():
    current_day = datetime.combine(date.today(), datetime.min.time())
    day = timedelta(days=1)
    while g.db.query(FilmSession).filter(FilmSession.start_time >=
                                         current_day).first():
        current_day += day
    f = False
    for i in g.db.query(FilmSession).all():
        if not f:
            delta = current_day - i.start_time
            delta = timedelta(days=delta.days + 1)
            # print('delta:  ', delta)
            f = True
        fs = FilmSession()
        fs.film_id = i.film_id
        fs.hall_id = i.hall_id
        # print('cr:  ', current_day)
        fs.start_time = i.start_time + delta
        # print('i: ', i.start_time)
        # print('fs: ', fs.start_time)
        fs.end_time = i.end_time + delta
        fs.price = i.price
        g.db.add(fs)
    g.db.commit()
    return redirect('/admin/filmsession/')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = g.db.query(AdminRole).filter(
            AdminRole.login == form.login.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/admin/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@login_manager.user_loader
def load_user(user_id):
    with db_session.create_session() as db_sess:
        return db_sess.query(AdminRole).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@babel.localeselector
def get_locale():
    # Put your logic here. Application can store locale in
    # user profile, cookie, session, etc.
    return 'ru'


@app.before_request
def before_request():
    # print('opening connection')
    g.db = db_session.create_session()
    if all(map(lambda x: x not in request.path,
           ['admin', 'login', 'logout'])) and current_user.is_authenticated:
        logout_user()


@app.after_request
def after_request(response):
    if g.db is not None:
        # print('closing connection')
        g.db.close()
    return response


def create_app():
    path = os.path.join(os.path.dirname(__file__), 'static')
    db_session.global_init('connect_to_db_in_db_session_file')
    admin = Admin(app, 'FlaskApp', index_view=AdminView(name='Home'))
    db_sess = db_session.create_session()
    admin.add_view(FilmSessionView(FilmSession, db_sess, category='Sessions'))
    admin.add_view(PlaceView(Place, db_sess, category='Sessions'))
    admin.add_view(FilmView(Film, db_sess, category='Film'))
    admin.add_view(ModelView(Genre, db_sess, category='Film'))
    admin.add_view(ModelView(Image, db_sess, category='Film'))
    admin.add_view(AdminRoleView(AdminRole, db_sess))
    admin.add_view(FileAdmin(path, '/static/', name='Static Files'))
    app.register_blueprint(films_api.blueprint)
    api.add_resource(films_resource.FilmResource,
                     '/api/films/<int:film_id>')
    api.add_resource(films_resource.FilmListResource, '/api/films')
    api.add_resource(film_session_resource.FilmSessionResource,
                     '/api/film_sessions/<int:film_sess_id>')
    api.add_resource(film_session_resource.FilmSessionListResource,
                     '/api/film_sessions')
    db_sess.close()
    return app


if __name__ == '__main__':
    import background_clock

    create_app()
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()
