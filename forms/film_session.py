from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import DateField


class FilmSessionForm(FlaskForm):
    film_id = StringField('Название', validators=[DataRequired()])
    hall_id = FloatField("Рейтинг")
    start_time = StringField("Актёры")
    end_time = StringField("Режиссёр")
    places = DateField("Дата премьеры", format='%Y-%m-%d')
    price = IntegerField("Длительность")
    submit = SubmitField('Применить')