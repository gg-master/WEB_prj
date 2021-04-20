import threading

from flask import request, session, g

from api.film_session_resource import FilmSessionResource
from api.films_resource import FilmResource
from data.places import Place
from modules import send_email


def make_order():
    # Получение сеанса фильма
    film_session = FilmSessionResource().get(
        session.get('session_id')).json['film_sess']
    # Получение фильма
    film = FilmResource().get(film_session['film_id']).json['film']
    # Узнаем выбранные места из запроса
    places = [i for i in request.form if request.form.get(i) == 'label']
    # Получение всех мест для сессии
    list_places_in_db = g.db.query(Place).filter(
        Place.film_session_id == film_session['id']).all()
    places_dct = {}
    # Перебираем все выбранные места и измением статус места
    for i in places:
        row, col = list(map(int, i.split('-')))
        place = list(filter(lambda place_db:
                            place_db.row_id == row and
                            place_db.seat_id == col, list_places_in_db))[0]
        place.status = True
        places_dct[i] = place.code
    # Коммитим изменения
    g.db.commit()
    params = {
        'places': places_dct,
        'film_title': film['title'],
        'hall_id': film_session['hall_id'],
        'time_start': film_session['start_time'],
        'time_end': film_session['end_time'],
        'phone': '+7 (8442) 93-52-52',
        'msg-text': 'Ваши билеты, заказанные на сайте FilmCenter.'
                    '\nНа это письмо не нужно отвечать.'
    }
    send_thread = threading.Thread(
        target=send_email.send_mail,
        args=(request.form.get('email'), params,))
    send_thread.start()
