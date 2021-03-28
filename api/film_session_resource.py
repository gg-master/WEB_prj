from datetime import datetime

from flask import jsonify
from flask_restful import Resource, reqparse

from data import db_session
from data.film_sessions import FilmSession
from misc.aborts import abort_if_film_sess_not_found

parser = reqparse.RequestParser()
parser.add_argument('film_id', required=True, type=int)
parser.add_argument('hall_id', required=True, type=int)
parser.add_argument('start_time', default=datetime.now())
parser.add_argument('end_time', default=datetime.now())
parser.add_argument('places', default='0' * 50)
parser.add_argument('price', type=int, default=0)


class FilmSessionResource(Resource):
    def get(self, film_sess_id):
        abort_if_film_sess_not_found(film_sess_id)
        session = db_session.create_session()
        film_sess = session.query(FilmSession).get(film_sess_id)
        return jsonify({'film_sess': film_sess.to_dict(
            only=('film_id', 'hall_id', 'start_time', 'end_time', 'places',
                  'price'))})

    def delete(self, film_sess_id):
        abort_if_film_sess_not_found(film_sess_id)
        session = db_session.create_session()
        film_sess = session.query(FilmSession).get(film_sess_id)
        session.delete(film_sess)
        session.commit()
        return jsonify({'success': 'OK'})

    def put(self, film_sess_id):
        abort_if_film_sess_not_found(film_sess_id)
        args = parser.parse_args()
        session = db_session.create_session()
        film_sess = session.query(FilmSession).get(film_sess_id)
        film_sess.film_id = args['film_id']
        film_sess.hall_id = args['hall_id']
        film_sess.start_time = datetime.fromisoformat(args['start_time'])
        film_sess.end_time = datetime.fromisoformat(args['end_time'])
        film_sess.places = args['places']
        film_sess.price = args['price']
        session.commit()
        return jsonify({'success': 'OK'})


class FilmSessionListResource(Resource):
    def get(self):
        session = db_session.create_session()
        film_sesses = session.query(FilmSession).all()
        return jsonify({'films': [film_sess.to_dict(
            only=('film_id', 'hall_id', 'start_time', 'end_time', 'places',
                  'price')) for film_sess in film_sesses]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        film_sess = FilmSession(film_id=args['film_id'],
                                hall_id=args['hall_id'],
                                start_time=args['start_time'],
                                end_time=args['end_time'],
                                places=args['places'],
                                price=args['price']
        )
        session.add(film_sess)
        session.commit()
        return jsonify({'success': 'OK'})
