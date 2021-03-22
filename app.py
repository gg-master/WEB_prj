import os

from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok

from data import db_session
from data.films import Film

app = Flask(__name__)
# run_with_ngrok(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/', methods=['GET', "POST"])
def start_page():
    # Инициализация сессии к бд
    # Получение списка фильмов
    print(request.method)
    db_sess = db_session.create_session()
    films = db_sess.query(Film).all()
    filter_dct = {'year': ['2021', '2022', '2023'], 'genre': ['Comedy'],
                  'rating': ['9.1', '2.1'], 'producer': []}
    if request.method == 'POST':
        filter_list = [i for i in request.args]
        print(filter_list)

        print([i for i in request.form])
        print([request.form.get(i) for i in request.form])
        # print(request.args.get(filter_list[0]))
        return render_template('index.html', films=films, filter=filter_dct,
                               filtered=True)

    recommended_films = db_sess.query(Film).filter(Film.rating > 8.0).all()
    return render_template('index.html',
                           films=films, filter=filter_dct,
                           recommended_films=recommended_films, filtered=False)


def main():
    db_session.global_init("db/database.db")

    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()


if __name__ == '__main__':
    main()
