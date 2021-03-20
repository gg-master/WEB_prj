from flask import Flask, render_template

from data import db_session
from data.films import Film

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def start_page():
    # Инициализация сессии к бд
    # Получение списка фильмов
    db_sess = db_session.create_session()
    recommended_films = db_sess.query(Film).filter(Film.rating > 8.0).all()

    return render_template('index.html', films=films)


def main():
    db_session.global_init("db/database.db")
    app.run()


if __name__ == '__main__':
    main()
