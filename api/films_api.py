import pprint
from datetime import datetime

import flask
import requests
from flask import jsonify, request

from data import db_session
from data.associations import Genre
from data.films import Film

blueprint = flask.Blueprint(
    'films_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/films/recommendations', methods=['GET'])
def get_films_recommendations():
    db_sess = db_session.create_session()
    new_films = sorted(
        db_sess.query(Film).filter(
            Film.premiere != None).all(),
        key=lambda x: x.premiere.month == datetime.now().month)[:5]
    most_watched_films = sorted(db_sess.query(Film).all(),
                                key=lambda x: x.watchers)[:5]
    return jsonify(
        {
            'new_films': [
                film.to_dict(only=(
                    'id', 'title', 'rating', 'actors', 'producer', 'premiere',
                    'duration', 'description', 'poster_url', 'images',
                    'trailer_url', 'watchers', 'genre')) for film in
                new_films],
            'most_watched_films':
                [film.to_dict(only=(
                    'id', 'title', 'rating', 'actors', 'producer', 'premiere',
                    'duration', 'description', 'poster_url', 'images',
                    'trailer_url', 'watchers', 'genre')) for film in
                    most_watched_films]
        }
    )


@blueprint.route('/api/filter_data', methods=['GET'])
def get_filter_data():
    db_sess = db_session.create_session()
    genres = sorted(set(map(lambda x: x.name, db_sess.query(Genre).all())))
    years = sorted(set(map(lambda x: x.premiere.year,
                         db_sess.query(Film).filter(
                             Film.premiere != None).all())))
    duration = sorted(set(map(lambda x: x.duration, db_sess.query(Film).filter(
        Film.duration != None).all())))
    producer = sorted(set(map(lambda x: x.producer,
                            db_sess.query(Film).filter(
                                Film.producer != None).all())))
    return jsonify(
        {
            'filter_data': {
                'genres': genres,
                'years': years,
                'duration': duration,
                'producer': producer
            }
        }
    )


@blueprint.route('/api/films/filtered', methods=['GET'])
def get_filtered_films():
    db_sess = db_session.create_session()
    filtered_params = {}
    for i in request.form:
        if i == 'title' and request.form.get(i):
            filtered_params['title'] = request.form.get(i)
        if i.endswith('cb'):
            v = request.form.get(i.split('_')[0])
            if v != '#':
                filtered_params[i.split('_')[0]] = v
    req = []
    if 'title' in filtered_params:
        req.append(Film.title.like(f'%{filtered_params["title"]}%'))
    if 'genre' in filtered_params:
        req.append(Film.genre.contains(db_sess.query(Genre).filter(
            Genre.name == filtered_params["genre"]).first()))
    if 'year' in filtered_params:
        req.append(Film.premiere.like(f'%{filtered_params["year"]}%'))
    if 'duration' in filtered_params:
        req.append(Film.duration.like(filtered_params['duration']))
    if 'producer' in filtered_params:
        req.append(Film.producer.like(filtered_params['producer']))
    filtered_films = db_sess.query(Film).filter(*req).all()
    pprint.pprint(filtered_films)
    return jsonify({'films': [film.to_dict(
        only=('id', 'title', 'rating', 'actors', 'producer', 'premiere',
              'duration', 'description', 'poster_url', 'images',
              'trailer_url', 'watchers', 'genre')) for film in
        filtered_films]})
