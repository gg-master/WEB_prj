from datetime import datetime

from flask import jsonify
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
parser.add_argument('images', action='append', type=list, default=[])
parser.add_argument('genres', action='append', type=list, default=[])


class FilmResource(Resource):
    def get(self, film_id):
        abort_if_film_not_found(film_id)
        session = db_session.create_session()
        film = session.query(Film).get(film_id)
        return jsonify({'film': film.to_dict(
            only=(
                'id', 'title', 'rating', 'actors', 'producer', 'premiere',
                'duration', 'description', 'poster_url', 'images',
                'trailer_url', 'watchers', 'genre'))})

    def delete(self, film_id):
        abort_if_film_not_found(film_id)
        session = db_session.create_session()
        film = session.query(Film).get(film_id)
        session.delete(film)
        session.commit()
        return jsonify({'success': 'OK'})


class FilmListResource(Resource):
    def get(self):
        session = db_session.create_session()
        films = session.query(Film).all()
        return jsonify({'films': [film.to_dict(
            only=('id', 'title', 'rating', 'actors', 'producer', 'premiere',
                  'duration', 'description', 'poster_url', 'images',
                  'trailer_url', 'watchers', 'genre')) for film in films]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

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
            genre = session.query(Genre).filter(
                Genre.name == genre_name).first()
            if genre is None:
                genre = Genre()
                genre.name = genre_name
            film.genre.append(genre)
        for image_url in args['images']:
            image = session.query(Image).filter(
                Image.image_url == image_url).first()
            if image is None:
                image = Image()
                image.image_url = image_url
            film.images.append(image)

        session.add(film)
        session.commit()
        return jsonify({'success': 'OK'})
