#!/usr/bin/env python
#
# Yet Another Todo List Application
#
import os

# try to get default YATL_PATH from environment
try:
    YATL_PATH = os.environ['YATL_PATH']
except KeyError:
    YATL_PATH = os.environ['HOME']
finally:
    if os.path.isdir(YATL_PATH):
        YATL_PATH = os.path.join(YATL_PATH, 'yet_another_todo.list')

yatl_description = """
Launcher for Yet Another Todo List (YATL). The default todo list
location (a file or directory path) may be overwritten with the
`YATL_PATH` environment variable. It may be useful to set this
path to a cloud-backed-up location.
"""

#
# Start here
#
if __name__ == '__main__':
    import argparse
    from yatl.todo import Todo

    parser = argparse.ArgumentParser(
        prog='Yet Another Todo List Application',
        description=yatl_description,
    )
    parser.add_argument('yatl_path', metavar='fpath', type=str, nargs='?',
                        default=YATL_PATH,
                        help='Path to YATL todo list [default: {:s}]'.format(YATL_PATH))
    parser.add_argument('--plot', action='store_true',
                        help='Display current tasks on time vs importance plot')
    parser.add_argument('--gui', action='store_true', help='Launch YATL GUI')
    args = parser.parse_args()

    todo = Todo(args.yatl_path)

    if args.plot:
        todo.plot()
    elif args.gui:
        import tkinter as tk
        from yatl.gui import YATLApp
        root = tk.Tk()
        root.title('Yet Another Todo List')
        mygui = YATLApp(root, todo)
        root.mainloop()
    else:
        todo.review()

