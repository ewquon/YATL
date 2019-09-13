#!/usr/bin/env python
import pandas as pd
import tkinter as tk
import tkinter.messagebox as msg

class TaskList(tk.Frame):
    """Based on:
    https://stackoverflow.com/questions/50398649/python-tkinter-tk-support-checklist-box
    """
    active_text_color = 'blue'
    inactive_text_color = 'black'
    row_color_cycle = [
        '#cbd7e9',
        '#e7ecf4',
    ]
    datetime_format = '%a %m/%d %H:%M'

    def __init__(self, parent, df, **kwargs):
        """Create a checklist, defined as a dictionary of bool"""
        # TODO: implement scrolling frame
        tk.Frame.__init__(self, parent, **kwargs)
        self.df = df
        print(id(self.df))
        self.orig_description = df['description']
        self.checkbutton = [] # Checkbutton widgets
        self.completed = [] # BooleanVars
        self.description = [] # StringVars
        self.removeme = [] # Button widgets
        self.bg = self.cget("background") # system-specific
        for irow,(idx,task) in enumerate(self.df.iterrows()):
            rowcolor = self.row_color_cycle[irow % len(self.row_color_cycle)]
            description = task['description']
            try:
                description += ' (completed {:s})'.format(
                        pd.to_datetime(task['completed']).strftime(self.datetime_format))
            except ValueError:
                completed = False
                state = 'normal'
                textcolor = self.active_text_color
            else:
                completed = True
                state = 'disabled'
                textcolor = self.inactive_text_color
            # Create checkbox and task description
            var = tk.BooleanVar(value=completed)
            text = tk.StringVar(value=description)
            cb = tk.Checkbutton(self, var=var, textvar=text,
                                onvalue=True, offvalue=False, state=state,
                                anchor="w", width=50,
                                fg=textcolor, background=rowcolor,
                                relief="flat", highlightthickness=0,
                                command=lambda i=irow: self.update_complete(i),
                               )
            cb.grid(row=irow,column=0)
            # Create accompanying remove button
            # - note that the command is not evaluated until it is clicked
            xbutton = tk.Button(self, text=' X ',
                                command=lambda i=irow: self.remove_row(i))
            xbutton.grid(row=irow, column=1)
            # save widgets and associated variables
            self.checkbutton.append(cb)
            self.completed.append(var)
            self.description.append(text)
            self.removeme.append(xbutton)

    def update_complete(self, irow):
        if self.completed[irow].get() is True:
            self.description[irow].set(
                '{:s} (completed {:s})'.format(self.orig_description[irow],
                                               pd.datetime.now().strftime(self.datetime_format))
            )
            self.checkbutton[irow].config(fg=self.inactive_text_color)
        else:
            self.description[irow].set(self.orig_description[irow])
            self.checkbutton[irow].config(fg=self.active_text_color)

    def remove_row(self, irow):
        # TODO: add messagebox confirmation
        print('Remove row',irow,':',self.description[irow].get())
        self.checkbutton[irow].grid_forget()
        self.removeme[irow].grid_forget()
        #self.checkbutton.pop(irow)
        #self.removeme.pop(irow)
        # TODO: update tasks, completed,removeme

    #def update(self):
        # TODO: update checkbox states and text

    def update_plot(self):
        # TODO: figure out how to reference plot in separate canvas
        print('Update plot')

    def getCheckedItems(self):
        values = []
        for var in self.vars:
            value =  var.get()
            if value:
                values.append(value)
        return values


class YATLApp(object):
    def __init__(self, master, df):
        self.master = master
        master.title = 'Yet Another Todo List App'
        self.todolist = TaskList(master, df)
        self.todolist.pack()


if __name__ == '__main__':
    import os
    from yatl.todo import Todo
    try:
        YATL_PATH = os.environ['YATL_PATH']
    except KeyError:
        YATL_PATH = os.environ['HOME']
    finally:
        if os.path.isdir(YATL_PATH):
            YATL_PATH = os.path.join(YATL_PATH, 'yet_another_todo.list')

    #df = pd.DataFrame({
    #    'description': ['a','b','d'],
    #    'completed': [True,True,False],
    #})
    todo = Todo(YATL_PATH)
    print(id(todo.df))

    root = tk.Tk()
    root.title('Yet Another Todo List')
    mygui = YATLApp(root, todo.df)
    root.mainloop()

