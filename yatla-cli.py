#!/usr/bin/env python
import os
from yatla.todo import Todo

debug = True

try:
    YATLA_PATH = os.environ['YATLA_PATH']
except KeyError:
    YATLA_PATH = os.environ['HOME']
finally:
    if os.path.isdir(YATLA_PATH):
        YATLA_PATH = os.path.join(YATLA_PATH, 'yet_another_todo.list')
if debug:
    print('todo list:',YATLA_PATH)

#
# Start here
#
if __name__ == '__main__':
    todo = Todo(YATLA_PATH)
    #todo.add_task('Email Jeff re FY20 AOP', importance=3, cost=1)
    todo.plot()
