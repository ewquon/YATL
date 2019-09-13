#!/usr/bin/env python
import pandas as pd
import tkinter as tk
import tkinter.messagebox as msg

class TaskList(tk.Frame):
    """Based on:
    https://stackoverflow.com/questions/50398649/python-tkinter-tk-support-checklist-box
    """
    def __init__(self, parent, taskdict, **kwargs):
        """Create a checklist, defined as a dictionary of bool"""
        # TODO: implement scrolling frame
        tk.Frame.__init__(self, parent, **kwargs)
        self.checkbuttons = [] # Checkbutton widgets
        self.completed = [] # BooleanVars
        self.description = [] # StringVars
        self.removeme = [] # Button widgets
        self.bg = self.cget("background")
        for irow,(desc,choice) in enumerate(taskdict.items()):
            # Create checkbox and task description
            var = tk.BooleanVar(value=choice)
            text = tk.StringVar(value=desc)
            cb = tk.Checkbutton(self, var=var, textvar=text,
                                onvalue=True, offvalue=False,
                                anchor="w", width=50, background=self.bg,
                                relief="flat", highlightthickness=0,
                                command=lambda i=irow: self.update_complete(i),
                               )
            cb.grid(row=irow,column=0)
            # Create accompanying remove button
            # - note that the command is not evaluated until it is clicked
            xbutton = tk.Button(self, text=' X ',
                                command=lambda i=irow: self.remove_row(i))
            xbutton.grid(row=irow, column=1)
            # save widgets and associated
            self.checkbuttons.append(cb)
            self.completed.append(var)
            self.description.append(text)
            self.removeme.append(xbutton)
        self.orig_description = [ desc for desc,_ in taskdict.items() ]

    def update_complete(self, irow):
        if self.completed[irow].get() is True:
            self.description[irow].set(
                '{:s} (completed {:s})'.format(self.orig_description[irow],
                                               pd.datetime.now().strftime('%Y-%m-%d %H:%M'))
            )
        else:
            self.description[irow].set(self.orig_description[irow])

    def remove_row(self, irow):
        # TODO: add messagebox confirmation
        print('Remove row',irow,':',self.description[irow].get())
        self.checkbuttons[irow].grid_forget()
        self.removeme[irow].grid_forget()
        #self.checkbuttons.pop(irow)
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
    def __init__(self, master):
        self.master = master
        master.title = 'Yet Another Todo List App'
        self.todolist = TaskList(master, {'a':True,'b':True,'d':False})
        self.todolist.pack()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Yet Another Todo List')
    mygui = YATLApp(root)
    root.mainloop()

