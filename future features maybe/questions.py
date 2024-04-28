import sqlalchemy as sql
from data.db_functions import SqlAlchemyBase


class DailyQuestion(SqlAlchemyBase):
	__tablename__ = 'questions'

	id = sql.Column(sql.Integer, primary_key=True, autoincrement=True, unique=True)

	date = sql.Column(sql.Integer, unique=True)

	question = sql.Column(sql.String, unique=True)

	answer = sql.Column(sql.String)




