import sjmanager.cache_directory
import inspect
import os

_log_file = open(
	str(sjmanager.cache_directory.cache_directory() / 'log'),
	mode='a',
	encoding='utf8')

def log(
	message):

	newlines = message.count('\n')
	padding = 3*(50*'-'+'\n') if newlines else ''

	message = inspect.stack()[1][3]+': '+message

	_log_file.write(
			'{pad}{msg}\n{pad}'.format(
				pad=padding,
				msg=message))
	_log_file.flush()
