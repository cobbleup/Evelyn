from data.questions import DailyQuestion
import data.db_functions as db

db.global_init('../db/user_data.db')

db_sess = db.create_session()


def add_question(line):
	date, text, answer = line.split('%')
	date = int(date)
	q = DailyQuestion(date=date, question=text, answer=answer)
	db_sess.add(q)
	db_sess.commit()


while True:
	print('Введите данные в формате date%question&answer')
	try:
		add_question(input())
	except ValueError:
		print('Попробуйте снова')
		print()
