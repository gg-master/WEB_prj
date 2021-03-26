import os
import pprint

from flask import Flask, render_template, request
# from flask_ngrok import run_with_ngrok
from flask_restful import Api

from api import films_resource, films_api
from data import db_session
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
    print(request.method)
    filter_dct = films_api.get_filter_data().json['filter_data']
    if request.method == 'POST':
        films = films_api.get_filtered_films().json['films']
        return render_template(
            'index.html', films=films, filter=filter_dct, filtered=True)
    films = films_resource.FilmListResource().get().json['films']
    return render_template('index.html',
                           films=films, filter=filter_dct, filtered=False,
                           **films_api.get_films_recommendations().json)


def main():
    db_session.global_init("db/database.db")
    app.register_blueprint(films_api.blueprint)
    api.add_resource(films_resource.FilmResource,
                     '/api/films/<int:film_id>')
    api.add_resource(films_resource.FilmListResource, '/api/films')
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run()


if __name__ == '__main__':
    main()
