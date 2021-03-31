from datetime import datetime

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class FilmSession(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'film_sessions'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    film_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("films.id"))
    hall_id = sqlalchemy.Column(sqlalchemy.Integer)
    start_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    end_time = sqlalchemy.Column(sqlalchemy.DateTime, nullable=True)
    # places = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='0' * 120)
    price = sqlalchemy.Column(sqlalchemy.Integer)
    film = orm.relation('Film')

    def __repr__(self):
        return f"Film session {self.id} {self.film_id} {self.start_time}" \
               f" {self.price}"
