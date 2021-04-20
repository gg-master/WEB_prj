import string
import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
import random
from .db_session import SqlAlchemyBase
from sqlalchemy import orm


class Place(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'place'
    symbols = string.ascii_uppercase + string.digits
    # random.shuffle(symbols)
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    film_session_id = sqlalchemy.Column(sqlalchemy.Integer,
                                        sqlalchemy.ForeignKey("film_sessions"
                                                              ".id"))
    row_id = sqlalchemy.Column(sqlalchemy.Integer)
    seat_id = sqlalchemy.Column(sqlalchemy.Integer)
    # status = sqlalchemy.Column(sqlalchemy.Boolean)
    code = sqlalchemy.Column(sqlalchemy.String,
                             default=''.join(random.sample(symbols, 6)))
    film_session = orm.relation('FilmSession')

    def __repr__(self):
        return f"Place {self.film_session} {self.row_id}" \
               f" {self.seat_id} {self.status}"
