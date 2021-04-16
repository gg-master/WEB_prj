from datetime import datetime, timedelta

from data import db_session
from data.film_sessions import FilmSession


def delete_film_session_every_week():
    db_sess = db_session.create_session()
    current_time_minus_week = datetime.now() - timedelta(weeks=1)
    db_sess.query(FilmSession).filter(FilmSession.end_time <
                                      current_time_minus_week).delete()
    db_sess.commit()
