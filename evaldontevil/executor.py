# evaldontevil
#  (eval, don't evil)
#  part of the Pythontutor project
#  https://github.com/vpavlenko/pythontutor-ru


from json import loads
from os.path import dirname

from codejail.jail_code import configure, jail_code, set_limit

from evaldontevil.config import *


configure('python', VENV_PYTHON + '/bin/python', user=USER)

set_limit('CPU', CPUTIME_LIMIT)
set_limit('REALTIME', REALTIME_LIMIT)
set_limit('MEM', MEM_LIMIT)
set_limit('FSIZE', FSIZE_LIMIT)


class ExecuteResult:
	def __init__(self, jailres):
		self.retcode = jailres.status
		self.result = 'ok' if self.retcode == 0 else 'retcode'

		self.stdout = str(jailres.stdout, 'utf-8')
		self.stderr = str(jailres.stderr, 'utf-8')

		if self.retcode & 128 != 0:
			self.result = 'time_limited'
			return

		if self.stderr != '':
			self.result = 'stderr'
			return


class ExecuteExplainedResult(ExecuteResult):
	def __init__(self, jailres):
		super().__init__(jailres)

		try:
			execplainator_res = loads(str(jailres.stdout, 'utf-8'))
		except:
			self.stdout = ''
			self.stderr = ''
			self.result = 'internal_error'
			return

		self.stdout = execplainator_res['stdout']
		self.stderr = execplainator_res['stderr']

		if self.stderr != '':
			self.result = 'stderr'

		self.trace = execplainator_res['trace']
		if len(self.trace) < 1:
			self.result = 'empty'
			return

		if self.trace[-1]['event'] == 'instruction_limit_reached':
			self.result = 'instructions_limited'
			return


def execute_python(code, stdin=''):
	code = bytes(code, 'utf-8')
	stdin = bytes(stdin, 'utf-8')

	jail_res = jail_code('python', code, stdin=stdin)
	return ExecuteResult(jail_res)


def execute_python_explain(code, stdin=''):
	code = bytes(code, 'utf-8')
	stdin = bytes(stdin, 'utf-8')

	this_dir = dirname(__file__)

	script = open(this_dir + '/script.py', 'rb').read()
	jail_res = jail_code(
		'python', script,

		files = [this_dir + '/execplainator.py', this_dir + '/execplainator_encoder.py'],
		extra_files = [
			('code.py', code),
			('stdin.txt', stdin),
		]
	)

	return ExecuteExplainedResult(jail_res)
