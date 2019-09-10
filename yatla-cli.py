#!/usr/bin/env python
#
# Yet Another Todo List Application
# (command line interface)
#
import os
from yatl.todo import Todo

debug = True

try:
    YATL_PATH = os.environ['YATL_PATH']
except KeyError:
    YATL_PATH = os.environ['HOME']
finally:
    if os.path.isdir(YATL_PATH):
        YATL_PATH = os.path.join(YATL_PATH, 'yet_another_todo.list')
if debug:
    print('todo list:',YATL_PATH)

#
# Start here
#
if __name__ == '__main__':
    todo = Todo(YATL_PATH)
    #todo.add_task('Email Jeff re FY20 AOP', importance=3, cost=1)
    todo.plot()
