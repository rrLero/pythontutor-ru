# evaldontevil
#  (eval, don't evil)
#  part of the Pythontutor project
#  https://github.com/vpavlenko/pythontutor-ru

# Script, which will be executed in the virtual jailed environment.


from json import dumps

from execplainator import exec


code = open('code.py', 'r', encoding='utf-8').read()
stdin = open('stdin.txt', 'r', encoding='utf-8').read()

print(dumps(exec(code, stdin)))
