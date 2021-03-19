from flask import Flask, render_template

from data import db_session
from data.films import Film

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def start_page():
    # Инициализация сессии к бд
    # Получение списка фильмов
    # db_sess = db_session.create_session()
    # films = db_sess.query(Film).all()
    # print(films)
    films = []
    return render_template('index.html', films=films)


def main():
    db_session.global_init("db/database.db")
    db_sess = db_session.create_session()
    films = db_sess.query(Film).all()
    print(films)
    app.run()


if __name__ == '__main__':
    main()
