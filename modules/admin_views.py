from flask_admin import AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask import Markup, g
from data.film_sessions import FilmSession
from data.images import Image
from data.admins import set_password
from flask_login import current_user
from flask import redirect


class AdminMixin:
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect('/login')


class FilmView(AdminMixin, ModelView):
    can_view_details = True
    column_list = ['id', 'title', 'rating', 'actors', 'producer',
                   'premiere', 'duration', 'description']
    column_sortable_list = ['id', 'title', 'rating', 'actors', 'producer',
                            'premiere', 'duration', 'description']
    column_searchable_list = ['id', 'title', 'rating', 'actors', 'producer',
                              'premiere', 'duration', 'description']
    column_filters = ['id', 'title', 'rating', 'premiere', 'duration']
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


class FilmSessionView(AdminMixin, ModelView):
    can_view_details = True
    column_list = ['id', 'film_id', 'hall_id', 'start_time', 'end_time',
                   'price']
    column_sortable_list = ['id', 'film_id', 'hall_id', 'start_time',
                            'end_time', 'price']
    column_searchable_list = ['id', 'film_id', 'hall_id', 'start_time',
                              'end_time', 'price']
    column_filters = ['id', 'film_id', 'hall_id', 'start_time', 'end_time',
                      'price']
    list_template = 'film_session.html'
    form_excluded_columns = ['places']
    page_size = 213

    def _s_places_formatter(view, context, model, name):
        if len(model.s_places) > 10:
            return model.s_places[:10]

    column_formatters = {
        's_places': _s_places_formatter
    }


class PlaceView(AdminMixin, ModelView):
    can_view_details = True
    column_list = ['id', 'film_session_id', 'row_id', 'seat_id']
    column_sortable_list = ['id', 'film_session_id', 'row_id', 'seat_id']
    column_searchable_list = ['id', 'film_session_id', 'row_id', 'seat_id']
    column_filters = ['film_session_id', 'row_id', 'seat_id']
    page_size = 20

    def on_model_delete(self, model):
        fs = g.db.query(FilmSession).filter(FilmSession.id ==
                                            model.film_session_id).first()
        fs.s_places = fs.s_places[:(model.row_id - 1) * 20 +
                                   model.seat_id - 1] + '0' + \
                      fs.s_places[(model.row_id - 1) * 20 + model.seat_id:]
        g.db.commit()


class AdminRoleView(AdminMixin, ModelView):
    can_edit = False
    can_delete = False

    def on_model_change(self, form, model, is_created):
        model.hashed_password = set_password(model.hashed_password)


class GenreView(AdminMixin, ModelView):
    pass


class ImageView(AdminMixin, ModelView):
    pass


class AdminView(AdminMixin, AdminIndexView):
    def is_visible(self):
        return False
