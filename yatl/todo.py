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
            self.df.sort_values(by='priority', ascending=False, inplace=True)

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
        self.df.sort_values(by='priority', ascending=False, inplace=True)
        self.df.to_csv(self.fpath, index=False)

    def plot(self):
        fig,ax = plt.subplots(figsize=(10,4))
        for i,(idx,task) in enumerate(self.df.iterrows()):
            try:
                completed_on = pd.to_datetime(task['completed']).strftime('%Y-%m-%d %H:%M')
            except ValueError:
                # task incomplete
                labelcolor = 'r'
                labelstr = '{:d} : {:s}'.format(i+1, task['description'])
                style = dict(marker=r'${:s}$'.format(self.incomplete_mark),
                             color=labelcolor, label=labelstr)
            else:
                # task completed
                labelcolor = 'g'
                labelstr = '{:d} : {:s}, completed {:s}'.format(
                        i+1, task['description'], completed_on)
                style = dict(marker=r'${:s}$'.format(self.complete_mark),
                             color=labelcolor, label=labelstr)
            print(labelstr)
            #ax.text(self.df['cost'], self.df['importance'], str(i+1),
            #        horizontalalignment='left', verticalalignment='bottom',
            #        fontsize=12, color=labelcolor,
            #        transform=ax.transAxes)
            ax.plot(task['cost'], task['importance'], ls='none', **style)
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

