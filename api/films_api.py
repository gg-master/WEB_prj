from datetime import datetime, date
import flask
from flask import jsonify, request, g
from sqlalchemy import func
from sqlalchemy.sql.expression import and_
from data.associations import Genre
from data.films import Film

blueprint = flask.Blueprint(
    'films_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/films/recommendations', methods=['GET'])
def get_films_recommendations():
    # Получение фильмов, премьера которых была за последний месяц
    new_films = list(filter(lambda x:
                            x.premiere.month == datetime.now().month
                            and x.premiere.year == datetime.now().year,
                            g.db.query(Film).filter(
                                Film.premiere != None).all()))[:5]
    # Получем первые 5 самых просматриваемых фильмов
    most_watched_films = sorted(g.db.query(Film).all(),
                                key=lambda x: x.watchers, reverse=True)[:5]
    # Возвращаем словарь с найденными фильмами
    return jsonify(
        {
            'new_films': [
                film.to_dict(only=(
                    'id', 'title', 'rating', 'actors', 'producer',
                    'premiere', 'duration', 'description', 'poster_url',
                    'images', 'trailer_url', 'watchers',
                    'genre')) for film in
                new_films],
            'most_watched_films':
                [film.to_dict(only=(
                    'id', 'title', 'rating', 'actors', 'producer',
                    'premiere', 'duration', 'description', 'poster_url',
                    'images', 'trailer_url', 'watchers',
                    'genre')) for film in
                    most_watched_films]
        }
    )


@blueprint.route('/api/filter_data', methods=['GET'])
def get_filter_data():
    # Получение всех доступных жанров
    genres = sorted(set(map(lambda x: x.name, g.db.query(Genre).all())))
    # Получение всех доступных годов премьеры
    years = sorted(set(map(lambda x: x.premiere.year,
                           g.db.query(Film).filter(
                               Film.premiere != None).all())))
    # Получение всех доступных вариантов длительности фильмов
    duration = sorted(
        set(map(lambda x: x.duration, g.db.query(Film).filter(
            Film.duration != None).all())))
    # Получение всех доступных режиссёров
    producer = sorted(set(map(lambda x: x.producer,
                              g.db.query(Film).filter(
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
    # Перебираем указанные параметры в форме и составляем
    # словарь параметров, по которым требуется найти фильм
    filtered_params = {}
    for i in request.form:
        if i == 'title' and request.form.get(i):
            filtered_params['title'] = request.form.get(i)
        if i.endswith('cb'):
            v = request.form.get(i.split('_')[0])
            if v != '#':
                filtered_params[i.split('_')[0]] = v
    # Составляем запрос для бд, перебирая параметры
    req = []
    if 'title' in filtered_params:
        req.append(Film.title.ilike(f'%{filtered_params["title"]}%'))
    if 'genre' in filtered_params:
        req.append(Film.genre.contains(g.db.query(Genre).filter(
            Genre.name == filtered_params["genre"]).first()))
    if 'year' in filtered_params:
        st_date = date(int(filtered_params['year']), 1, 1)
        end_date = date(int(filtered_params['year']), 12, 31)
        req.append(and_(func.date(Film.premiere) <= end_date))
        req.append(and_(func.date(Film.premiere) >= st_date))
    if 'duration' in filtered_params:
        req.append(Film.duration == int(filtered_params['duration']))
    if 'producer' in filtered_params:
        req.append(Film.producer.like(filtered_params['producer']))
    # Получаем все фильмы, которые подходят по запросу
    filtered_films = g.db.query(Film).filter(*req).all()
    return jsonify({'films': [film.to_dict(
        only=('id', 'title', 'rating', 'actors', 'producer', 'premiere',
              'duration', 'description', 'poster_url', 'images',
              'trailer_url', 'watchers', 'genre')) for film in
        filtered_films]})
