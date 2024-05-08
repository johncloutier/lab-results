'''
Created on May 5, 2024

@author: John Cloutier
'''

import matplotlib.pyplot as plt
import matplotlib.dates as dts
import pandas as pd


from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

class ScrollableWindow(QtWidgets.QMainWindow):
    def __init__(self, fig):
        self.qapp = QtWidgets.QApplication([])

        QtWidgets.QMainWindow.__init__(self)
        self.widget = QtWidgets.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(QtWidgets.QVBoxLayout())
        self.widget.layout().setContentsMargins(0,0,0,0)
        self.widget.layout().setSpacing(0)
        
        self.fig = fig
        self.canvas = FigureCanvas(self.fig)
        self.canvas.draw()
        self.scroll = QtWidgets.QScrollArea(self.widget)
        self.scroll.setWidget(self.canvas)

        self.nav = NavigationToolbar(self.canvas, self.widget)
        self.widget.layout().addWidget(self.nav)
        self.widget.layout().addWidget(self.scroll)
        self.resize(1600, 900)
        self.show()
        exit(self.qapp.exec_()) 


def plotLabSet(labset):      
    
    dates = []
    values = []
    for lab in labset.results:
        dates.append(lab.time)
        values.append(lab.numvalue)
    
    df = pd.DataFrame({'Dates': dates, labset.name: values})
    df['Dates'] = pd.to_datetime(df['Dates'])
    df = df.sort_values('Dates', ascending=True)
    df[labset.name] = pd.to_numeric(df[labset.name], errors='coerce')

    fig, ax = plt.subplots()
    plt.plot(df['Dates'], df[labset.name])
    #ax.set_xticks(df['Dates'])
    ax.xaxis.set_major_formatter(dts.DateFormatter("%m-%d-%Y"))
    plt.xticks(rotation=90) 

    plt.xlabel("Date")
    plt.ylabel("Value")
    plt.title(labset.name)
    plt.legend()
    fig.suptitle('Laboratory Results')
    plt.show()

def plotResults(results): 
    count = len(results.data)
    rows = int(count / 3) if count % 3 == 0 else int(count // 3 + 1)
    cols = 3
    chartno = 0
    fig, ax = plt.subplots(nrows=rows, ncols=cols, figsize=(12, 120))
    fig.suptitle('Laboratory Results', y=0.999)
            
    for labset in results.data:
        dates = []
        values = []
        for lab in labset.results:
            dates.append(lab.time)
            values.append(lab.numvalue)
        
        # Make numeric and sort data
        df = pd.DataFrame({'Dates': dates, labset.name: values})
        df['Dates'] = pd.to_datetime(df['Dates'])
        df = df.sort_values('Dates', ascending=True)
        df[labset.name] = pd.to_numeric(df[labset.name], errors='coerce')
        
        # Locate chart position
        rowpos = chartno // 3
        colpos = chartno % 3

        ax[rowpos, colpos].plot(df['Dates'], df[labset.name])
        ax[rowpos, colpos].xaxis.set_major_formatter(dts.DateFormatter("%m/%Y"))
        ax[rowpos, colpos].tick_params(axis='x', labelsize=4)
        ax[rowpos, colpos].tick_params(axis='y', labelsize=6)
        ax[rowpos, colpos].set_ylabel(labset.results[0].ref, fontsize=6)
        ax[rowpos, colpos].set_title(labset.name, fontsize=8, y=1.0, pad=-12)
        chartno += 1
    
    # Hide unused subplots
    while chartno < rows * cols:
        rowpos = chartno // 3
        colpos = chartno % 3
        ax[rowpos, colpos].remove()
        chartno += 1
    
    fig.tight_layout()
    ScrollableWindow(fig)