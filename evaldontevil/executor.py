# evaldontevil
#  (eval, don't evil)
#  part of the Pythontutor project
#  https://github.com/vpavlenko/pythontutor-ru


from json import dumps
from os.path import dirname

from codejail.jail_code import configure, jail_code, set_limit

from evaldontevil.config import *


configure('python', VENV_PYTHON + '/bin/python', user=USER)

set_limit('CPU', CPUTIME_LIMIT)
set_limit('REALTIME', REALTIME_LIMIT)
set_limit('MEM', MEM_LIMIT)
set_limit('FSIZE', FSIZE_LIMIT)


def execute_python(code, stdin=''):
	info = {
		'code': code,
		'stdin': stdin,
	}

	this_dir = dirname(__file__)

	script = open(this_dir + '/script.py', 'rb').read()
	return jail_code(
		'python', script,

		files = [this_dir + '/execplainator.py', this_dir + '/execplainator_encoder.py'],
		extra_files = [
			('code.py', bytes(code, 'utf-8')),
			('stdin.txt', bytes(stdin, 'utf-8')),
		]
	)
