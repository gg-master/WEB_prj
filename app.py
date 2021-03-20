import os

from flask import Flask, render_template
# from flask_ngrok import run_with_ngrok

from data import db_session
from data.films import Film

app = Flask(__name__)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
def start_page():
    # Инициализация сессии к бд
    # Получение списка фильмов
    db_sess = db_session.create_session()
    recommended_films = db_sess.query(Film).filter(Film.rating > 8.0).all()
    films = db_sess.query(Film).all()
    return render_template('index.html', films=films)


def main():
    db_session.global_init("db/database.db")

    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()


if __name__ == '__main__':
    main()
