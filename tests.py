import logging
import requests

logging.basicConfig(level=logging.INFO)


def test_films_api():
    arr = ['new_films', 'most_watched_films']
    resp = requests.get(
        'http://localhost:5000/api/films/recommendations').json()
    assert all(map(lambda x: x in resp, arr))


test_films_api()
