from datetime import datetime
from flask import jsonify, g
from flask_restful import Resource, reqparse, abort
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
        # Проверка наличия фильма
        abort_if_film_not_found(film_id)
        # Получение фильма
        film = g.db.query(Film).get(film_id)
        # Увеличение количества просмотров
        film.watchers += 1
        g.db.commit()
        # Возвращаение словаря с выбранным фильмом
        return jsonify({'film': film.to_dict(
            only=(
                'id', 'title', 'rating', 'actors', 'producer', 'premiere',
                'duration', 'description', 'poster_url', 'images',
                'trailer_url', 'watchers', 'genre'))})

    def delete(self, film_id):
        # Проверка наличия фильма
        abort_if_film_not_found(film_id)
        # Получение фильма
        film = g.db.query(Film).get(film_id)
        # Удаление фильма
        g.db.delete(film)
        g.db.commit()
        return jsonify({'success': 'OK'})

    def put(self, film_id):
        abort_if_film_not_found(film_id)
        args = parser.parse_args()
        film = g.db.query(Film).get(film_id)
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
            try:
                # Если дата премьеры введено неправильно, то вызываем аборт
                film.premiere = datetime.fromisoformat(args['premiere'])
            except Exception as ex:
                abort(400, message='The premiere date was entered '
                                   'incorrectly. Required format '
                                   'year-month-day')
        genres = list(map(lambda x: x.lower(), args['genres']))
        for genre_name in genres:
            # Узнаем есть ли жанр в бд
            genre = g.db.query(Genre).filter(
                Genre.name == genre_name).first()
            # Если жанра нет, то создаем его
            if genre is None:
                genre = Genre()
                genre.name = genre_name
            film.genre.append(genre)
        for image_url in args['images']:
            # Узнаем есть ли картинка в бд
            image = g.db.query(Image).filter(
                Image.image_url == image_url).first()
            # Если картинки нет, то создаем ее
            if image is None:
                image = Image()
                image.image_url = image_url
            film.images.append(image)
        g.db.commit()
        return jsonify({'success': 'OK'})


class FilmListResource(Resource):
    def get(self):
        films = g.db.query(Film).all()
        return jsonify({'films': [film.to_dict(
            only=('id', 'title', 'rating', 'actors', 'producer',
                  'premiere', 'duration', 'description', 'poster_url',
                  'images', 'trailer_url', 'watchers',
                  'genre')) for film in films]})

    def post(self):
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
            try:
                # Если дата премьеры введено неправильно, то вызываем аборт
                film.premiere = datetime.fromisoformat(args['premiere'])
            except Exception as ex:
                abort(400, message='The premiere date was entered '
                                   'incorrectly. Required format '
                                   'year-month-day')
        genres = list(map(lambda x: x.lower(), args['genres']))
        for genre_name in genres:
            # Узнаем есть ли жанр в бд
            genre = g.db.query(Genre).filter(
                Genre.name == genre_name).first()
            # Если жанра нет, то создаем его
            if genre is None:
                genre = Genre()
                genre.name = genre_name
            film.genre.append(genre)
        for image_url in args['images']:
            # Узнаем есть ли картинка в бд
            image = g.db.query(Image).filter(
                Image.image_url == image_url).first()
            # Если картинки нет, то создаем ее
            if image is None:
                image = Image()
                image.image_url = image_url
            film.images.append(image)
        g.db.add(film)
        g.db.commit()
        return jsonify({'success': 'OK'})
