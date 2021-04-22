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
    actors = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    producer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    premiere = sqlalchemy.Column(sqlalchemy.DATE, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    poster_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    trailer_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    watchers = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    serialize_rules = ('-images.film', '-comments.film', '-genre.film',
                       '-film_session.film')
    images = orm.relation("Image", back_populates='film')
    film_session = orm.relation('FilmSession', back_populates='film',
                                cascade="all, delete, delete-orphan")
    genre = orm.relation("Genre",
                         secondary="association_film_genres", )

    def __repr__(self):
        return f"Film ID: {self.id}\n" \
               f"title: {self.title}"
