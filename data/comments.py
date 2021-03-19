import sqlalchemy
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    comment_text = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    film_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("films.id"))
    film = orm.relation("Film")
