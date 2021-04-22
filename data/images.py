import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Image(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'images'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    image_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    film_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("films.id"))
    film = orm.relation("Film")
    serialize_only = ('image_url',)

    def __repr__(self):
        return f'Image id: {self.id}; {self.film}'
