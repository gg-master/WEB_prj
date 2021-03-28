from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class FilmForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    rating = FloatField("Рейтинг")
    actors = StringField("Актёры")
    producer = StringField("Режиссёр")
    premiere = DateField("Дата премьеры", format='%Y-%m-%d')
    duration = IntegerField("Длительность")
    description = TextAreaField("Описание")
    poster_url = StringField("Ссылка на постер")
    trailer_url = StringField("Ссылка на трейлер")
    images = StringField("Ссылка на картинки")
    genres = StringField("Жанры")
    submit = SubmitField('Применить')