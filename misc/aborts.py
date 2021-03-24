from flask_restful import abort

from data import db_session
from data.films import Film


def abort_if_film_not_found(film_id):
    session = db_session.create_session()
    news = session.query(Film).get(film_id)
    if not news:
        abort(404, message=f"Film {film_id} not found")
