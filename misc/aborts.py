from flask_restful import abort
from flask import g
from data.films import Film
from data.film_sessions import FilmSession
from datetime import timedelta


def abort_if_film_not_found(film_id):
    # Узнаем есть ли фильм
    films = g.db.query(Film).get(film_id)
    # Если нету, то выбрасываем ошибку 404
    if not films:
        abort(404, message=f"Film {film_id} not found")


def abort_if_film_sess_not_found(film_sess_id):
    # Узнаем есть ли сессия
    films = g.db.query(FilmSession).get(film_sess_id)
    # Если нету, то выбрасываем ошибку 404
    if not films:
        abort(404, message=f"Film session {film_sess_id} not found")


def abort_if_film_sess_not_correct(data):
    film = g.db.query(Film).get(data['film_id'])
    if not film:
        abort(404, message=f'Film {data["film_id"]} not found')
    try:
        start_time = data['start_time']
        end_time = data['end_time']
    except (ValueError, TypeError):
        abort(400, message=f'Time is not correct')
        return None
    duration = timedelta(minutes=film.duration)
    if duration > end_time - start_time:
        abort(400, message=f'The time interval is less '
              f'than the duration of the movie')
    timetable = g.db.query(FilmSession.start_time,
                           FilmSession.end_time).filter(
        FilmSession.hall_id == data['hall_id']).all
    timetable.sort(key=lambda x: x[0])
    i = 0
    while i < len(timetable) and start_time > timetable[i][0]:
        i += 1
    if not (timetable and timetable[i - 1][1] <= start_time and
            i < len(timetable) and end_time <= timetable[i][0] or
            i >= len(timetable) or not i):
        abort(400, message='This time is not available')
