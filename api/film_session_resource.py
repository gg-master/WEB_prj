from datetime import datetime

from flask import jsonify, g
from flask_restful import Resource, reqparse

from data.film_sessions import FilmSession
from misc.aborts import abort_if_film_sess_not_found

parser = reqparse.RequestParser()
parser.add_argument('film_id', required=True, type=int)
parser.add_argument('hall_id', required=True, type=int)
parser.add_argument('start_time', default=datetime.now())
parser.add_argument('end_time', default=datetime.now())
parser.add_argument('s_places', type=str, default='0' * 120)
parser.add_argument('price', type=int, default=0)


class FilmSessionResource(Resource):
    def get(self, film_sess_id):
        abort_if_film_sess_not_found(film_sess_id)
        film_sess = g.db.query(FilmSession).get(film_sess_id)
        return jsonify({'film_sess': film_sess.to_dict(
            only=('id', 'film_id', 'hall_id', 'start_time', 'end_time',
                  'price', 's_places'))})

    def delete(self, film_sess_id):
        abort_if_film_sess_not_found(film_sess_id)
        film_sess = g.db.query(FilmSession).get(film_sess_id)
        g.db.delete(film_sess)
        g.db.commit()
        return jsonify({'success': 'OK'})

    def put(self, film_sess_id):
        abort_if_film_sess_not_found(film_sess_id)
        args = parser.parse_args()
        film_sess = g.db.query(FilmSession).get(film_sess_id)
        film_sess.film_id = args['film_id']
        film_sess.hall_id = args['hall_id']
        film_sess.start_time = datetime.fromisoformat(args['start_time'])
        film_sess.end_time = datetime.fromisoformat(args['end_time'])
        film_sess.s_places = args['s_places']
        film_sess.price = args['price']
        g.db.commit()
        return jsonify({'success': 'OK'})


class FilmSessionListResource(Resource):
    def get(self):
        film_sesses = g.db.query(FilmSession).all()
        return jsonify({'films': [film_sess.to_dict(
            only=('id', 'film_id', 'hall_id', 'start_time', 'end_time',
                  'price', 's_places')) for film_sess in film_sesses]})

    def post(self):
        args = parser.parse_args()
        film_sess = FilmSession(film_id=args['film_id'],
                                hall_id=args['hall_id'],
                                start_time=args['start_time'],
                                end_time=args['end_time'],
                                price=args['price'],
                                s_places=args['s_places']
        )
        g.db.add(film_sess)
        g.db.commit()
        return jsonify({'success': 'OK'})
