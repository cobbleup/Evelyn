from sqlalchemy import exists
from data import db_functions
from data.user import User
from datetime import *


db_functions.global_init('db/user_data.db')


db_sess = db_functions.create_session()


def edit_name(username: str, newname):
	db = db_sess.query(User)
	if db_sess.query(exists().where(User.username == username)).scalar():
		db.filter(User.username == username).first().customname = newname
	else:
		user = User(username=username, customname=newname)
		db_sess.add(user)
	db_sess.commit()


def player_custom_name(username: str):
	db = db_sess.query(User)
	if db_sess.query(exists().where(User.username == username)).scalar():
		return db.filter(User.username == username).first().customname
	else:
		return False


def pay_user(user: str, amount):
	db = db_sess.query(User)
	if db_sess.query(exists().where(User.username == user)).scalar():
		db.filter(User.username == user).first().coins += amount
		db_sess.commit()
	else:
		return False


def user_can_pay(user: str, amount):
	db = db_sess.query(User)
	if db.filter(User.username == user).first().coins >= amount:
		return True
	return False


if __name__ == '__main__':
	edit_name('helpe', 'help is here')
	edit_name('pipi', 'pipipi')
	print(player_custom_name('helpe'))
	print(player_custom_name('pipi'))
	pay_user('Coffielya', 100)



