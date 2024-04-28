def command(name, description, function_name):
	return {
		'name': name,
		'desc': description,
		'func_name': function_name
	}


commands = [
	command('help', 'список команд', 'helper'),
	command('start', 'начало работы', 'start'),
	command('d <целое число>', 'бросок кубика', 'throw_die'),
	command('changenickname', 'изменение вашего имени', 'editname')

]
