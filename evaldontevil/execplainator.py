# evaldontevil
#  (eval, don't evil)
#  part of the Pythontutor project
#  https://github.com/vpavlenko/pythontutor-ru


# This is a modified copy of pg_logger.py from the
#   Online Python Tutor (https://github.com/pgbovine/OnlinePythonTutor/)
# It is Python 3 ready, and less restrictive.

# -----------------------------------------------------------------------------

# Online Python Tutor
# https://github.com/pgbovine/OnlinePythonTutor/
# 
# Copyright (C) 2010-2012 Philip J. Guo (philip@pgbovine.net)
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# -----------------------------------------------------------------------------

# This is a execplainator module. It will execute the user code, and then
# give back to the evaldontevil a detailed step-by-step examplanation, how
# code really did work.

# P.S. This code is supposed to be executed in the secure environment (those
# will do by dontevil), so there is not so much security checks and restrictions.


from bdb import Bdb
from io import StringIO
from traceback import print_exc
import sys

from execplainator_encoder import encode


# upper-bound on the number of executed lines, in order to guard against
# infinite loops
MAX_EXECUTED_LINES = 1000


IGNORE_VARS = set(('__stdin__', '__stdout__', '__builtins__', '__name__', '__package__'))


class StopExecution(Exception):
    pass


def get_user_stdout(frame):
    return user_stdout.getvalue()

def get_user_globals(frame):
    d = filter_var_dict(frame.f_globals)
    # also filter out __return__ for globals only, but NOT for locals

    if '__return__' in d:
        del d['__return__']

    return d

def get_user_locals(frame):
    return filter_var_dict(frame.f_locals)

def filter_var_dict(d):
    ret = {}

    for k, v in d.items():
        if k not in IGNORE_VARS and k not in __builtins__ and not (k.startswith('__') and k.endswith('__')):
            ret[k] = v

    return ret


class Execplainator(Bdb):
    def __init__(self, ignore_id=False):
        Bdb.__init__(self)

        self.mainpyfile = ''
        self.filter_var_dict_wait_for_mainpyfile = 0

        # each entry contains a dict with the information for a single
        # executed line
        self.trace = []

        # don't print out a custom ID for each object
        # (for regression testing)
        self.ignore_id = ignore_id


    def reset(self):
        Bdb.reset(self)
        self.forget()

    def forget(self):
        self.lineno = None
        self.stack = []
        self.curindex = 0
        self.curframe = None

    def setup(self, f, t):
        self.forget()
        self.stack, self.curindex = self.get_stack(f, t)
        self.curframe = self.stack[self.curindex][0]


    # Override Bdb methods

    def user_call(self, frame, argument_list):
        """This method is called when there is the remote possibility
        that we ever need to stop in this function."""

        if self._wait_for_mainpyfile:
            return

        if self.stop_here(frame):
            self.interaction(frame, None, 'call')

    def user_line(self, frame):
        """This function is called when we stop or break at this line."""

        if self._wait_for_mainpyfile:
            if (self.canonic(frame.f_code.co_filename) != '<string>' or frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = 0

        self.interaction(frame, None, 'step_line')

    def user_return(self, frame, return_value):
        """This function is called when a return trap is set here."""

        frame.f_locals['__return__'] = return_value
        self.interaction(frame, None, 'return')

    def user_exception(self, frame, exc_info):
        """This function is called if an exception occurs,
        but only if we are to stop at or just below this level."""

        exc_type, exc_value, exc_traceback = exc_info

        frame.f_locals['__exception__'] = exc_type, exc_value
        exc_type_name = exc_type if type(exc_type) == str else exc_type.__name__

        self.interaction(frame, exc_traceback, 'exception')


    # General interaction function

    def interaction(self, frame, traceback, event_type):
        self.setup(frame, traceback)
        tos = self.stack[self.curindex]
        func_name = tos[0].f_code.co_name
        lineno = tos[1]

        if func_name != '<module>':
            return

        # each element is a pair of (function name, ENCODED locals dict)
        encoded_stack_locals = []

        # climb up until you find '<module>', which is (hopefully) the global scope
        i = self.curindex
        while True:
            cur_frame = self.stack[i][0]
            cur_name = cur_frame.f_code.co_name
            if cur_name == '<module>':
                break

            # special case for lambdas - grab their line numbers too
            if cur_name == '<lambda>':
                cur_name = 'lambda on line ' + str(cur_frame.f_code.co_firstlineno)
            elif cur_name == '':
                cur_name = 'unnamed function'

            # encode in a JSON-friendly format now, in order to prevent ill
            # effects of aliasing later down the line ...
            encoded_locals = {}
            for (k, v) in get_user_locals(cur_frame).items():
                # don't display some built-in locals ...
                if k != '__module__':
                    encoded_locals[k] = encode(v, self.ignore_id)

            encoded_stack_locals.append((cur_name, encoded_locals))
            i -= 1

        # encode in a JSON-friendly format now, in order to prevent ill
        # effects of aliasing later down the line ...
        encoded_globals = {}
        for (k, v) in get_user_globals(tos[0]).items():
            encoded_globals[k] = encode(v, self.ignore_id)

        trace_entry = dict(line=lineno,
                           event=event_type,
                           func_name=func_name,
                           globals=encoded_globals,
                           stack_locals=encoded_stack_locals,
                           stdout=get_user_stdout(tos[0]))

        # if there's an exception, then record its info:
        if event_type == 'exception':
            # always check in f_locals
            exc = frame.f_locals['__exception__']
            trace_entry['exception_msg'] = exc[0].__name__ + ': ' + str(exc[1])

        self.trace.append(trace_entry)

        if len(self.trace) >= MAX_EXECUTED_LINES:
            self.trace.append(dict(event='instruction_limit_reached', exception_msg='Stopped after ' + str(MAX_EXECUTED_LINES) + ' steps to prevent possible infinite loop'))
            self.force_terminate()

        self.forget()


    def _runscript(self, script_str, input_data):
        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = 1

        # ok, let's try to sorta 'sandbox' the user script by not
        # allowing certain potentially dangerous operations:
        user_builtins = {}
        for (name, orig_builtin) in __builtins__.items():
            if name in ('reload', 'apply', 'compile', #'__import__',
                        'file', 'eval', 'execfile', 'exec'):
                continue

            if name == '__import__':
                true_import = orig_builtin

                def import__workaround(*args, **kwargs):
                    return true_import(*args, **kwargs)

                user_builtins[name] = import__workaround

            else:
                user_builtins[name] = orig_builtin


        global true_stdin
        global user_stdin
        true_stdin = sys.stdin
        user_stdin = StringIO(input_data)
        sys.stdin = user_stdin

        global true_stdout
        global user_stdout
        true_stdout = sys.stdout
        user_stdout = StringIO()
        sys.stdout = user_stdout


        user_globals = {'__name__': '__main__',
                        '__builtins__': user_builtins,
                        '__stdin__': user_stdin,
                        '__stdout__': user_stdout,
                       }

        try:
            self.run(script_str, user_globals, user_globals)

        except StopExecution:
            pass

        except:
            #print_exc() # uncomment this to see the REAL exception msg

            trace_entry = dict(event='uncaught_exception')

            exc = sys.exc_info()[1]
            if hasattr(exc, 'lineno'):
              trace_entry['line'] = exc.lineno
            if hasattr(exc, 'offset'):
              trace_entry['offset'] = exc.offset

            if hasattr(exc, 'msg'):
                print(('exc has message:\n\t{0}'.format(exc.msg)))
                trace_entry['exception_msg'] = 'Error: ' + exc.msg
            else:
                trace_entry['exception_msg'] = 'Unknown error'

            self.trace.append(trace_entry)

        sys.stdin = true_stdin
        sys.stdout = true_stdout

        return self.finalize()


    def force_terminate(self):
        raise StopExecution()


    def finalize(self):
        # filter all entries after 'return' from '<module>', since they
        # seem extraneous:
        res = []
        for e in self.trace:
            res.append(e)
            if e['event'] == 'return' and e['func_name'] == '<module>':
                break

        # another hack: if the SECOND to last entry is an 'exception'
        # and the last entry is return from <module>, then axe the last
        # entry, for aesthetic reasons :)
        if len(res) >= 2 and \
           res[-2]['event'] == 'exception' and \
           res[-1]['event'] == 'return' and res[-1]['func_name'] == '<module>':
            res.pop()

        self.trace = res

        return self.trace


def exec(script_str, input_data, ignore_id=False):
    execplainator = Execplainator(ignore_id)
    return execplainator._runscript(script_str, str(input_data))
