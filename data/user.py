import sqlalchemy
from .db_functions import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'userinfo'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)

    username = sqlalchemy.Column(sqlalchemy.String, unique=True)

    customname = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    coins = sqlalchemy.Column(sqlalchemy.Integer, default=100)

    checked_in = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    sacrificed = sqlalchemy.Column(sqlalchemy.Integer, default=0)

