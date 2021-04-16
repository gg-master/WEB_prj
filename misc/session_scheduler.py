import logging
from datetime import datetime, timedelta

from data import db_session
from data.film_sessions import FilmSession
from data.places import Place


def delete_film_session_every_week():
    logging.info('Starting delete_film_session_every_week')
    db_sess = db_session.create_session()
    current_time_minus_week = datetime.now() - timedelta(weeks=1)
    for i in db_sess.query(FilmSession).filter(
            FilmSession.end_time < current_time_minus_week).all():
        db_sess.query(Place).filter(Place.film_session_id == i.id).delete()
        db_sess.delete(i)
    db_sess.commit()
    db_sess.close()
    logging.info('Items successfully deleted')
