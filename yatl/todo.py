import os
import numpy as np
import pandas as pd

# to avoid NSException when initializing Tkinter gui
# (see https://github.com/MTG/sms-tools/issues/29)
# - matplotlib.use() should come before the matplotlib.pyplot import
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


class Todo(object):
    """Object to contain a dataframe with tasks as rows"""

    todo_columns = [
        'datetime',
        'description',
        'importance',
        'cost',
        'priority',
        'completed',
    ]
    complete_mark='✔'
    incomplete_mark='✘'

    def __init__(self, fpath, value_minmax=(1,4)):
        """Create a new todo list from the specified file

        Parameters
        ----------
        fpath : str
            Path to todo list, stored as a dataframe
        value_minmax : list or tuple, optional
            Minimum/maximum values for importance and cost
        """
        self.fpath = fpath
        self.value_minmax = value_minmax
        self.changed = False
        self._read_list()

    def _read_list(self):
        # make sure temp file doesn't exist
        print('Todo list:',self.fpath)
        pathsplit = os.path.split(self.fpath)
        self.fpath_tmp = os.path.join(pathsplit[0], '.'+pathsplit[1])
        assert (not os.path.isfile(self.fpath_tmp)), \
                self.fpath_tmp+' exists, todo list was not properly saved'
        # load todo list
        try:
            self.df = pd.read_csv(self.fpath)
        except FileNotFoundError: 
            self.df = pd.DataFrame(columns=self.todo_columns)
        else:
            self.sort_list()

    def sort_list(self):
        self.df.sort_values(by=['priority','importance','datetime'],
                            ascending=[False,False,True],
                            inplace=True)

    def save(self,overwrite=False):
        """Save the todo list (to the temporary file, by default)"""
        if overwrite:
            self.df.to_csv(self.fpath, index=False)
            print('Saved',self.fpath)
            self.remove_temp()
        else:
            self.changed = True
            self.df.to_csv(self.fpath_tmp, index=False)

    def remove_temp(self):
        try:
            os.remove(self.fpath_tmp)
        except IOError:
            print('No changes')
        else:
            print('Cleaned up',self.fpath_tmp)

    def add_task(self, description, importance, cost):
        """Add a new task at the current time with the specified
        importance and cost values, calculating priority as the ratio
        of importance to cost

        Parameters
        ----------
            description : str
            importance : float
                In the range of value_minmax, with higher being more
                important
            cost : float
                In the range of value_minmax, with higher being more
                time consuming
        """
        newtask = pd.Series({
            'datetime': pd.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # task creation timestamp
            'description': description,
            'importance': importance,
            'cost': cost,
            'priority': importance / cost,
            'completed': False,
        })
        # this will create a new dataframe, and lose the index ordering in the process:
        #self.df = self.df.append(newtask, ignore_index=True)
        self.df.loc[len(self.df)] = newtask
        self.sort_list()
        self.save()

    def get_completion_datetime(self, i):
        try:
            return pd.to_datetime(self.df.loc[i,'completed'])
        except (ValueError, TypeError):
            return None

    def delete_task(self, i):
        """Delete task"""
        self.df.drop(labels=i, axis=0, inplace=True)
        self.save()

    def mark_complete(self, i):
        """Mark task as completed with the current datetime"""
        completed_on = self.get_completion_datetime(i)
        if completed_on is None:
            self.df.loc[i,'completed'] = pd.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.save()
        else:
            print('Task',i,'already completed:')
            print(self.df.loc[i])

    def _plot_offset(self, frac=0.025):
        maxdisp = frac * (self.value_minmax[1] - self.value_minmax[0])
        return maxdisp * (2*np.random.random_sample() - 1)

    def review(self):
        """Print the current todo list, sorted by priority and
        importance. 
        """
        for i,task in self.df.iterrows():
            completed_on = self.get_completion_datetime(i)
            if completed_on is None:
                # task incomplete
                labelcolor = 'r'
                labelstr = '{:d} : {:s}'.format(i, task['description'])
                style = dict(marker=r'${:s}$'.format(self.incomplete_mark),
                             color=labelcolor, label=labelstr)
                print('[ ] {:s}'.format(labelstr))
            else:
                # task completed
                labelcolor = 'g'
                labelstr = '{:d} : {:s}, completed {:s}'.format(
                        i, task['description'], str(completed_on))
                style = dict(marker=r'${:s}$'.format(self.complete_mark),
                             color=labelcolor, label=labelstr)
                print('[{:s}] {:s}'.format(self.complete_mark,labelstr))

    def plot(self,fig=None,ax=None,legend=True):
        """Make a scatterplot of the current tasks on time vs
        importance axes.
        """
        showplot = False
        if (fig is None) or (ax is None):
            showplot = True
            fig,ax = plt.subplots(figsize=(10,4))
        # loop over tasks, checking for completion
        for i,task in self.df.iterrows():
            completed_on = self.get_completion_datetime(i)
            if completed_on is None:
                # task incomplete
                labelcolor = 'r'
                labelstr = '{:d} : {:s}'.format(i, task['description'])
                style = dict(marker=r'${:s}$'.format(self.incomplete_mark),
                             color=labelcolor, label=labelstr)
            else:
                # task completed
                labelcolor = 'g'
                labelstr = '{:d} : {:s}, completed {:s}'.format(
                        i, task['description'], str(completed_on))
                style = dict(marker=r'${:s}$'.format(self.complete_mark),
                             color=labelcolor, label=labelstr)
            # add offset to prevent tasks from perfectly overlapping on plot
            xloc = task['cost'] + self._plot_offset()
            yloc = task['importance'] + self._plot_offset()
            ax.plot(xloc, yloc, ls='none', **style)
        # update formatting
        expanded_range = (self.value_minmax[0] - 0.25,
                          self.value_minmax[1] + 0.25)
        value_split = np.mean(self.value_minmax)
        ax.axhline(value_split, ls='-', color='k')
        ax.axvline(value_split, ls='-', color='k')
        bkg_props = {
            'color': '0.7',
            'fontfamily': 'sans-serif',
            'fontsize': 'xx-large',
            'horizontalalignment': 'left',
            'verticalalignment': 'top',
            'transform': ax.transAxes,
        }
        ax.text(0.05, 0.95, '1', **bkg_props)
        ax.text(0.55, 0.95, '2', **bkg_props)
        ax.text(0.05, 0.45, '3', **bkg_props)
        ax.text(0.55, 0.45, '4', **bkg_props)
        ax.set_xlim(expanded_range)
        ax.set_ylim(expanded_range)
        ax.set_xticks(self.value_minmax, minor=False)
        ax.set_yticks(self.value_minmax, minor=False)
        ax.set_xticklabels(['-','+'])
        ax.set_yticklabels(['-','+'])
        ax.set_xlabel('time commitment')
        ax.set_ylabel('importance')
        if legend:
            ax.legend(loc='upper left', bbox_to_anchor=(1.05,1))
        fig.tight_layout()
        if showplot:
            plt.show()

