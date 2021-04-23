import logging
import pprint

import requests

logging.basicConfig(level=logging.INFO)

# domain = 'localhost:5000'
domain = 'film-center-prj.herokuapp.com'


def test_films_api():
    arr = ['new_films', 'most_watched_films']
    resp = requests.get(
        f'http://{domain}/api/films/recommendations').json()
    assert all(map(lambda x: x in resp, arr))


def test_film_abort():
    resp = requests.get(
        f'http://{domain}/api/films/199').json()
    assert 'message' in resp and 'not found' in resp['message']


def test_filter_data_api():
    arr = ['filter_data']
    resp = requests.get(
        f'http://{domain}/api/filter_data').json()
    assert all(map(lambda x: x in resp, arr))


def test_filtered_films():
    arr = ['films']
    resp = requests.get(
        f'http://{domain}/api/films/filtered').json()
    assert all(map(lambda x: x in resp, arr))


def test_film_search():
    # TODO функция не для теста. Нужно переписать для работы с pytest
    data = {
        'genre_cb': 'on',
        'genre': 'биография'
    }
    resp = requests.get(
        f'http://{domain}/api/films/filtered', data=data).json()
    pprint.pprint(resp)


# TODO убрать вызов после корректировки функции
test_film_search()
