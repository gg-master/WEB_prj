import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Film(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'films'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    rating = sqlalchemy.Column(sqlalchemy.Float, nullable=True)

    # Можно попробовать добавить отдельную таблицу с актерами
    actors = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    producer = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    poster_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    trailer_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    watchers = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    images = orm.relation("Image", back_populates='film')
    comments = orm.relation("Comment", back_populates='film')

    genre = orm.relation("Genre",
                         secondary="association_film_genres",
                         backref="films")

    def __repr__(self):
        return f"Film {self.title} {self.rating}"
