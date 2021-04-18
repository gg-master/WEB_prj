import random
import string

from flask_admin.contrib.sqla import ModelView
from flask import Markup, g

from data import db_session
from data.images import Image
from data.places import Place


class FilmView(ModelView):
    can_view_details = True
    column_searchable_list = ['title', 'rating', 'actors', 'producer',
                              'premiere', 'duration', 'description']
    column_filters = ['title', 'rating', 'premiere', 'duration']
    form_excluded_columns = ['film_session']
    inline_models = [(Image, dict(form_columns=['id', 'image_url']))]

    def _description_formatter(view, context, model, name):
        if model.description is None:
            return ''
        return model.description[:20]

    def _actors_formatter(view, context, model, name):
        if model.actors is None:
            return ''
        return model.actors.split(', ')[0]

    def _poster_url_formatter(view, context, model, name):
        if model.poster_url:
            markupstring = f"<a href='{model.poster_url}'>link</a>"
            return Markup(markupstring)
        else:
            return ""

    def _trailer_url_formatter(view, context, model, name):
        if model.trailer_url:
            markupstring = f"<a href='{model.trailer_url}'>link</a>"
            return Markup(markupstring)
        else:
            return ""

    column_formatters = {
        'actors': _actors_formatter,
        'description': _description_formatter,
        'poster_url': _poster_url_formatter,
        'trailer_url': _trailer_url_formatter
    }


class FilmSessionView(ModelView):
    can_view_details = True
    column_searchable_list = ['film_id', 'hall_id', 'start_time', 'end_time',
                              'price']
    column_filters = ['film_id', 'hall_id', 'start_time', 'end_time', 'price']
    list_template = 'film_session.html'
    form_excluded_columns = ['places']

    def after_model_change(self, form, model, is_created):
        symbols = list(string.ascii_uppercase + string.digits)
        with db_session.create_session() as db_sess:
            for i in range(1, 7):
                for j in range(1, 21):
                    place = Place(
                        film_session_id=model.id,
                        row_id=i,
                        seat_id=j,
                        status=False,
                        code=''.join(random.sample(symbols, 6))
                    )
                    db_sess.add(place)
                    db_sess.commit()


class PlaceView(ModelView):
    can_view_details = True
    column_searchable_list = ['film_session_id', 'row_id', 'seat_id',
                              'status']
    column_filters = ['film_session_id', 'row_id', 'seat_id', 'status']
    page_size = 20
