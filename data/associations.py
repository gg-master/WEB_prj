import sqlalchemy
from .db_session import SqlAlchemyBase

assoc_film_genre = sqlalchemy.Table(
    'association_film_genres',
    SqlAlchemyBase.metadata,
    sqlalchemy.Column('films', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('films.id')),
    sqlalchemy.Column('genres', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('genres.id'))
)


class Genre(SqlAlchemyBase):
    __tablename__ = 'genres'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
