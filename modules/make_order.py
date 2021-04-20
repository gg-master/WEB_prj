import threading

import requests
from flask import request, session, g

from api.film_session_resource import FilmSessionResource
from api.films_resource import FilmResource
from data.places import Place, generate_code
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
    places_dct, list_places_in_db = create_places(
        places, list(film_session['s_places']), film_session['id'])
    db_threading = threading.Thread(
        target=requests.put,
        args=(f'http://localhost:5000/api/film_sessions/{film_session["id"]}',
              {'film_id': film_session["film_id"],
               'hall_id': film_session['hall_id'],
               'start_time': film_session['start_time'],
               'end_time': film_session['end_time'],
               's_places': ''.join(list_places_in_db),
               'price': film_session['price']}))
    db_threading.start()
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


def create_places(places, list_places_in_db, f_s_id):
    places_dct = {}
    # Перебираем все выбранные места и измением статус места
    for i in places:
        row, col = list(map(int, i.split('-')))
        number_place = ((int(row) - 1) * 20) + (int(col) - 1)
        list_places_in_db[number_place] = '1'
        place = Place(
            film_session_id=f_s_id,
            row_id=row,
            seat_id=col
        )
        place.code = generate_code()
        places_dct[i] = place.code
        g.db.add(place)
    # Коммитим изменения
    g.db.commit()
    return places_dct, list_places_in_db
