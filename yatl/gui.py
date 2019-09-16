#!/usr/bin/env python
import pandas as pd
import tkinter as tk
import tkinter.messagebox as msg

# to avoid NSException when initializing Tkinter gui
# (see https://github.com/MTG/sms-tools/issues/29)
# - matplotlib.use() should come before the matplotlib.pyplot import
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

default_task_charlen = 50

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

    def __init__(self, parent, todo, **kwargs):
        """Create a checklist from a dataframe of tasks"""
        # TODO: implement scrolling frame
        tk.Frame.__init__(self, parent, **kwargs)
        self.todo = todo
        df = self.todo.df
        self.orig_description = df['description']
        self.checkbutton = [] # Checkbutton widgets
        self.completed = [] # BooleanVars
        self.description = [] # StringVars
        self.removeme = [] # Button widgets
        for irow,(idx,task) in enumerate(df.iterrows()):
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
                                anchor="w", width=default_task_charlen,
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
        """Callback function for when a task is checked or unchecked

        Only callable for tasks that were not previously completed and
        saved. Note that each time the checkbox is checked, the task
        completion time will be updated.
        """
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
        """Remove task from list"""
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


class TaskCreator(tk.Frame):
    default_description = 'Enter new task description here...'

    def __init__(self, parent, todo, **kwargs):
        """Create a series of controls for adding new tasks"""
        tk.Frame.__init__(self, parent, **kwargs)
        self.todo = todo
        value_minmax = todo.value_minmax
        print(id(self.todo.df))
        # variables
        self.task_description = tk.StringVar(value=self.default_description)
        self.importance = tk.DoubleVar(value=value_minmax[1])
        self.cost = tk.DoubleVar(value=value_minmax[0])
        # controls
        self.description_entry = tk.Entry(self,
                                          width=default_task_charlen,
                                          textvariable=self.task_description)
        label0 = tk.Label(self, text='importance', anchor='s')
        self.importance_ctrl = tk.Scale(self,
                                        orient='horizontal', length=200,
                                        variable=self.importance,
                                        from_=value_minmax[0],
                                        to=value_minmax[1],
                                        resolution=1.0)
        label1 = tk.Label(self, text='cost', anchor='s')
        self.cost_ctrl = tk.Scale(self,
                                  orient='horizontal', length=200,
                                  variable=self.cost,
                                  from_=value_minmax[0],
                                  to=value_minmax[1],
                                  resolution=1.0)
        bg = self.cget("background") # system-specific
        spacer = tk.Frame(self, height=10, bg=bg)
        self.add_task_button = tk.Button(self,
                                         text='add task',
                                         fg='blue',
                                         padx=20, pady=5,
                                         command=self.add_task)
        # create layout
        self.description_entry.pack()
        label0.pack()
        self.importance_ctrl.pack()
        label1.pack()
        self.cost_ctrl.pack()
        spacer.pack()
        self.add_task_button.pack()

    def add_task(self):
        """Add a new task to the todo list"""
        description = self.description_entry.get()
        importance = self.importance.get()
        cost = self.cost.get()
        priority = importance / cost
        print(description, importance, cost, priority)
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, self.default_description)


class TaskPlot(tk.Frame):
    """Based on:
    https://matplotlib.org/3.1.0/gallery/user_interfaces/embedding_in_tk_sgskip.html
    """

    def __init__(self, parent, todo, figsize=(2,2), **kwargs):
        """Create canvas for time vs importance plot"""
        tk.Frame.__init__(self, parent, **kwargs)
        self.todo = todo
        # Make the plot
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.todo.plot(fig=self.fig, ax=self.ax, legend=False)
        # Create the canvas, a tk.DrawingArea
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
 

class YATLApp(object):
    def __init__(self, master, todo):
        """Container for the YATL application

        Parameters
        ----------
        master : Tk object
        todo : yatl.todo object
        """
        self.master = master
        self.todo = todo
        tasklist = TaskList(master, self.todo)
        taskplot = TaskPlot(master, self.todo)
        taskctrl = TaskCreator(master, self.todo)
        tasklist.pack()
        taskplot.pack()
        taskctrl.pack()
        # catch closing event
        self.master.protocol('WM_DELETE_WINDOW', self.onclose)

    def onclose(self):
        if self.todo.changed is True:
            action = msg.askyesnocancel("Quit", "Save todo list?")
            if action is True:
                self.todo.save(overwrite=True)
            elif action is False:
                self.todo.remove_temp()
        else:
            action = True
        if action is not None:
            # clean exit
            self.master.quit()      # stops mainloop
            self.master.destroy()   # this is necessary on Windows to prevent
                                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


if __name__ == '__main__':
    from yatla import YATL_PATH
    from yatl.todo import Todo

    todo = Todo(YATL_PATH)
    print(id(todo.df))

    root = tk.Tk()
    root.title('Yet Another Todo List')
    mygui = YATLApp(root, todo)
    root.mainloop()

