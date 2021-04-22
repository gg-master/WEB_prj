import logging
import requests

logging.basicConfig(level=logging.INFO)

# domain = 'localhost:5000'
domain = 'film-center-prj.herokuapp.com'


def test_films_api():
    arr = ['new_films', 'most_watched_films']
    resp = requests.get(
        f'http://{domain}/api/films/recommendations').json()
    assert all(map(lambda x: x in resp, arr))


