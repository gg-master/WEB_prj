import logging

from data import db_session
from api import films_api

if db_session.__factory is None:
    db_session.global_init('connect_to_db_in_db_session_file')


def test_films_api():
    assert films_api.get_films_recommendations() == ''
