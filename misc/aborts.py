from flask_restful import abort

from data import db_session
from data.films import Film
from data.film_sessions import FilmSession


def abort_if_film_not_found(film_id):
    session = db_session.create_session()
    films = session.query(Film).get(film_id)
    if not films:
        abort(404, message=f"Film {film_id} not found")


def abort_if_film_sess_not_found(film_sess_id):
    session = db_session.create_session()
    films = session.query(FilmSession).get(film_sess_id)
    if not films:
        abort(404, message=f"Film session {film_sess_id} not found")


def abort_if_film_sess_not_correct(data):
    pass
