from datetime import datetime

from flask import jsonify, g
from flask_restful import Resource, reqparse

from data import db_session
from data.associations import Genre
from data.films import Film
from data.images import Image
from misc.aborts import abort_if_film_not_found

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('duration', required=True, type=int)
parser.add_argument('rating', type=float, default=0.0)
parser.add_argument('actors', default='', type=str)
parser.add_argument('premiere', default='')
parser.add_argument('producer', default='')
parser.add_argument('description', default='')
parser.add_argument('poster_url', default=None)
parser.add_argument('trailer_url', default=None)
parser.add_argument('watchers', type=int, default=0)
parser.add_argument('images', action='append', default=[])
parser.add_argument('genres', action='append', default=[])


class FilmResource(Resource):
    def get(self, film_id):
        with db_session.create_session() as db_sess:
            # Проверка наличия фильма
            abort_if_film_not_found(film_id)
            # Получение фильма
            film = db_sess.query(Film).get(film_id)
            # Увеличение количества просмотров
            film.watchers += 1
            db_sess.commit()
            # Возвращаение словаря с выбранным фильмом
            return jsonify({'film': film.to_dict(
                only=(
                    'id', 'title', 'rating', 'actors', 'producer', 'premiere',
                    'duration', 'description', 'poster_url', 'images',
                    'trailer_url', 'watchers', 'genre'))})

    def delete(self, film_id):
        with db_session.create_session() as db_sess:
            # Проверка наличия фильма
            abort_if_film_not_found(film_id)
            # Получение фильма
            film = db_sess.query(Film).get(film_id)
            # Удаление фильма
            db_sess.delete(film)
            db_sess.commit()
            return jsonify({'success': 'OK'})

    def put(self, film_id):
        with db_session.create_session() as db_sess:
            abort_if_film_not_found(film_id)
            args = parser.parse_args()
            film = db_sess.query(Film).get(film_id)
            film.title = args['title']
            film.rating = args['rating']
            film.actors = args['actors']
            film.producer = args['producer']
            film.duration = args['duration']
            film.description = args['description']
            film.poster_url = args['poster_url']
            film.trailer_url = args['trailer_url']
            film.watchers = args['watchers']
            if args['premiere']:
                film.premiere = datetime.fromisoformat(args['premiere'])
            genres = list(map(lambda x: x.lower(), args['genres']))
            for genre_name in genres:
                genre = db_sess.query(Genre).filter(
                    Genre.name == genre_name).first()
                if genre is None:
                    genre = Genre()
                    genre.name = genre_name
                film.genre.append(genre)
            for image_url in args['images']:
                image = db_sess.query(Image).filter(
                    Image.image_url == image_url).first()
                if image is None:
                    image = Image()
                    image.image_url = image_url
                film.images.append(image)
            db_sess.commit()
            return jsonify({'success': 'OK'})


class FilmListResource(Resource):
    def get(self):
        with db_session.create_session() as db_sess:
            films = db_sess.query(Film).all()
            return jsonify({'films': [film.to_dict(
                only=('id', 'title', 'rating', 'actors', 'producer',
                      'premiere', 'duration', 'description', 'poster_url',
                      'images', 'trailer_url', 'watchers',
                      'genre')) for film in films]})

    def post(self):
        with db_session.create_session() as db_sess:
            args = parser.parse_args()
            film = Film(
                title=args['title'],
                rating=args['rating'],
                actors=args['actors'],
                producer=args['producer'],
                duration=args['duration'],
                description=args['description'],
                poster_url=args['poster_url'],
                trailer_url=args['trailer_url'],
                watchers=args['watchers']
            )
            if args['premiere']:
                film.premiere = datetime.fromisoformat(args['premiere'])
            genres = list(map(lambda x: x.lower(), args['genres']))
            for genre_name in genres:
                genre = db_sess.query(Genre).filter(
                    Genre.name == genre_name).first()
                if genre is None:
                    genre = Genre()
                    genre.name = genre_name
                film.genre.append(genre)
            for image_url in args['images']:
                image = db_sess.query(Image).filter(
                    Image.image_url == image_url).first()
                if image is None:
                    image = Image()
                    image.image_url = image_url
                film.images.append(image)
            db_sess.add(film)
            db_sess.commit()
            return jsonify({'success': 'OK'})
