import sqlalchemy
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class AdminRole(SqlAlchemyBase, UserMixin):
    __tablename__ = 'admins'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    login = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


def set_password(password):
    return generate_password_hash(password)