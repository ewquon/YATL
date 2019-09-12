import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class Todo(object):
    """Object to contain a dataframe with tasks as rows"""

    todo_columns = ['datetime','description','importance','cost','priority','completed']
    complete_mark='✔'
    incomplete_mark='✘'

    def __init__(self, fpath, value_minmax=(1,4)):
        self.fpath = fpath
        self.value_minmax = value_minmax
        self.value_split = np.mean(value_minmax)
        self._read_list()

    def _read_list(self):
        try:
            self.df = pd.read_csv(self.fpath)
        except FileNotFoundError: 
            self.df = pd.DataFrame(columns=self.todo_columns)
        else:
            self._sort_list()

    def _sort_list(self):
        self.df.sort_values(by=['priority','importance','datetime'],
                            ascending=[False,False,True],
                            inplace=True)

    def _save(self):
        self.df.to_csv(self.fpath, index=False)

    def add_task(self, description, importance, cost):
        newtask = pd.Series({
            'datetime': pd.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), # task creation timestamp
            'description': description,
            'importance': importance,
            'cost': cost,
            'priority': importance / cost,
            'completed': False,
        })
        self.df = self.df.append(newtask, ignore_index=True)
        self._sort_list()
        self._save()

    def mark_complete(self, i):
        """Mark task as completed with the current datetime"""
        try:
            completed_on = pd.to_datetime(self.df.loc[i,'completed'])
        except (ValueError, TypeError):
            self.df.loc[i,'completed'] = pd.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._save()
        else:
            print('Task',i,'already completed:')
            print(self.df.loc[i])

    def _plot_offset(self, frac=0.025):
        maxdisp = frac * (self.value_minmax[1] - self.value_minmax[0])
        return maxdisp * (2*np.random.random_sample() - 1)

    def review(self,plot=False):
        """Print the current todo list, sorted by priority and
        importance. Optionally, make a scatterplot of the current tasks
        on time-importance axes.
        """
        if plot:
            fig,ax = plt.subplots(figsize=(10,4))
        for i,task in self.df.iterrows():
            try:
                completed_on = pd.to_datetime(task['completed']).strftime('%Y-%m-%d %H:%M')
            except (ValueError, TypeError):
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
                        i, task['description'], completed_on)
                style = dict(marker=r'${:s}$'.format(self.complete_mark),
                             color=labelcolor, label=labelstr)
                print('[{:s}] {:s}'.format(self.complete_mark,labelstr))
            if plot:
                xloc = task['cost'] + self._plot_offset()
                yloc = task['importance'] + self._plot_offset()
                ax.plot(xloc, yloc, ls='none', **style)

        if plot:
            # update formatting
            expanded_range = (self.value_minmax[0] - 0.25,
                              self.value_minmax[1] + 0.25)
            ax.axhline(self.value_split, ls='-', color='k')
            ax.axvline(self.value_split, ls='-', color='k')
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
            ax.legend(loc='upper left', bbox_to_anchor=(1.05,1))
            fig.tight_layout()
            plt.show()

    def plot(self):
        """Convenience function for review(plot=True)"""
        self.review(plot=True)
