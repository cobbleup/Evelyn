import asyncio
import os
import random

from telegram.ext import Application, MessageHandler, filters, ContextTypes, \
	CommandHandler, ChatMemberHandler, ChatJoinRequestHandler, PrefixHandler, \
	CallbackContext, ConversationHandler
import logging
from telegram import Update, ChatMemberUpdated, ChatMember, Chat

from info import commands
from test import *

logging.basicConfig(
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = '6913260202:AAFH5gze4voSZsDy-mGSdAu-_p4JNp3_8ck'

db_functions.global_init('db/user_data.db')
db_sess = db_functions.create_session()


# adress the user
def call_user(update: Update):
	if player_custom_name(update.effective_user.username):
		return player_custom_name(update.effective_user.username)
	else:
		return update.effective_user.full_name


async def callback(update: Update, context: CallbackContext):
	print('callback, haha!')


# check if it is time to reset check-ins
def new_day():
	with open('db/checkins.txt', mode='r') as data:
		pr_date = data.readline().rstrip()
	print(pr_date, date.today(), sep='')
	if pr_date != str(date.today()):
		data = open('db/checkins.txt', mode='w')
		print(date.today(), file=data)
		data.close()
		return True
	data.close()
	return False


# starting the conversation
async def start(update, context):
	await update.message.reply_text('Привет! Меня зовут Эвелин. Чтобы увидеть, что я могу, просто напиши /help!')


# help command, gets commands from info.py
async def helper(update, context):
	text = f'Конечно, я помогу тебе, {call_user(update)}!' \
		f'\nВот список команд, которые могут быть полезны!'

	for command in commands:
		text += f'\n/{command["name"]} - {command["desc"]}'
	await update.message.reply_text(text + '.')


# agree with user politely
async def yes(update: Update, context):
	await update.message.reply_text(f'Конечно, {player_custom_name(update.effective_user.username)}!')


# random number gen
def die(value):
	return random.choice(range(1, value + 1))


# self-descriptive
async def throw_die(update, context):
	try:
		text = f'Вам выпало {die(int(context.args[0]))}!'
		await update.message.reply_text(text)
	except (IndexError, ValueError, OverflowError):
		await update.message.reply_text('Упс! Я не могу бросить такой кубик :(')


# changing nickname dialogue
async def get_nickname_1(update: Update, context):
	await update.message.reply_text('Без проблем! Как вас называть?')
	return 1


async def get_nickname_2(update, context):
	context.user_data["nickname"] = update.message.text
	await update.message.reply_text(f'Здорово, значит, Вы - {context.user_data["nickname"]}?')
	return 2


async def get_nickname_confirm(update, context):
	if update.message.text.lower() in ['да', 'yes', 'yeah', 'конечно', 'ага', 'sure', 'мгм', 'так точно',
									'ты прав', 'ты права', 'разумеется', 'угу', 'true', 'ye', 'ok', 'ок', 'окей',
									'okay', 'da',
									'оки', 'дада', 'yeye', 'точно', 'именно', 'определенно', 'так']:
		storage = open('nicknames.txt', 'a', encoding="UTF-8")
		print(update.effective_user.username, context.user_data['nickname'], file=storage)
		storage.close()
		await update.message.reply_text(f'Сделано! Отныне Вы {context.user_data["nickname"]}!')
		edit_name(update.effective_user.username, context.user_data['nickname'])
	else:
		await update.message.reply_text('Как скажете ;(')
	return ConversationHandler.END


# stop dialogue
async def stop(update, context):
	await update.message.reply_text('Конечно, до свидания.')
	return ConversationHandler.END


# transactions
async def pay(update: Update, context):
	sender = update.effective_user.username
	print(context.args)
	if len(context.args) == 2:
		try:
			target = context.args[0]
			amount = int(context.args[1])
			if amount < 1:
				await update.message.reply_text('Никаких краж!')
				return
			if user_can_pay(sender, amount):
				if pay_user(target, amount):
					pay_user(sender, -amount)
					await update.message.reply_text('Сделано!')
				else:
					await update.message.reply_text('Некорректный пользователь!')
			else:
				await update.message.reply_text('Боюсь, у вас не хватает денег(')

		except Exception:
			await update.message.reply_text('Простите, я не могу осуществить трансакцию')

	else:
		await update.message.reply_text('Простите, я не могу осуществить трансакцию')


# check-ins
async def check_in(update: Update, context):
	db = db_sess.query(User).where(User.username == update.effective_user.username)
	await reset_check_ins()
	if db.filter(User.username == update.effective_user.username).first().checked_in == 0:
		db.filter(User.username == update.effective_user.username).first().checked_in = 1
		print(db.filter(User.username == update.effective_user.username).first().checked_in)
		db_sess.commit()
		pay_user(update.effective_user.username, 50)
		money = db.filter(User.username == update.effective_user.username).first().coins
		await update.message.reply_text(f'Рада видеть вас, {call_user(update)}!\n'
										f'Ловите 50 монеток в ваш карман!\n'
										f'\n'
										f'Теперь на вашем счету {money} монет')

	elif db_sess.query(exists(User).where(User.username == update.effective_user.username)).scalar():
		await update.message.reply_text('Вы уже получили сегодняшний приз!')

	else:
		await update.message.reply_text(f'Я не знаю, кто вы, давайте, для начала познакоимимся!')
		await get_nickname_1(update, context)


# trying to reset daily when anyone checks in
async def reset_check_ins():
	if new_day():
		db = db_sess.query(User)
		for user in db:
			user.checked_in = 0


# conversation handler creation
nickname_dialogue = ConversationHandler(
	entry_points=[CommandHandler('changenickname', get_nickname_1)],

	states={
		1: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nickname_2)],
		2: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_nickname_confirm)]
	},

	fallbacks=[CommandHandler('stop', stop)]
)


# start the bot
def run():
	if os.name == 'nt':
		asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

	application = Application.builder().token(TOKEN).build()
	application.add_handler(CommandHandler('help', helper))
	application.add_handler(CommandHandler('start', start))
	application.add_handler(CommandHandler('d', throw_die))
	application.add_handler(CommandHandler('yes', yes))
	application.add_handler(CommandHandler('pay', pay))
	application.add_handler(CommandHandler('checkin', check_in))

	application.add_handler(nickname_dialogue)

	prefixes = ['!', 'Evelyn.', 'evelyn.']
	application.add_handler(PrefixHandler(prefixes, 'help', helper))
	application.add_handler(PrefixHandler(prefixes, 'start', start))
	application.add_handler(PrefixHandler(prefixes, 'd', throw_die))
	application.add_handler(PrefixHandler(prefixes, 'yes', yes))
	application.add_handler(PrefixHandler(prefixes, 'pay', pay))
	application.add_handler(PrefixHandler(prefixes, 'checkin', check_in))

	application.run_polling()


if __name__ == '__main__':
	run()
