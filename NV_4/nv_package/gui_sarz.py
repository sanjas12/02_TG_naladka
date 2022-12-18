import random
import sys
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from graphs.value_gpk import value_gpk
from graphs.graph_gpk import graph_gpk
from settings import *
from model_NV import ModelNV

class Sarz(object):
    def __init__(self):
        try:
            self.app = QtWidgets.QApplication(sys.argv)
        except RuntimeError:
            self.app = QtWidgets.QApplication.instance()
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout(border=(100,100,100))
       
        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle('SAZR')
        self.view.resize(*RES_IMITATOR)
        self.view.show()

        # First column
        self.l1 = self.layout.addLayout()
        
        # Second column
        self.l2 = self.layout.addLayout()

        self.grath_list = []
        self.value_list = []

        self.data = 0

        self.sensor_name = ('Медиана')
        self.color_name = ('r', 'g', 'b')
        self.number_point_to_grath = NUMBER_POINT_TO_GRATH

        self.font = QtGui.QFont()
        self.font.setPixelSize(FONT_SIZE)

    def plot_init(self):

        # create list graths
        gpk_grath = graph_gpk(title=self.sensor_name, pen=self.color_name[0])
        self.l1.addItem(gpk_grath)
        self.grath_list.append(gpk_grath)
        self.l1.nextRow()

        # create list value
        gpk_value = value_gpk(color=self.color_name[0], font=self.font, name=self.sensor_name, title=self.sensor_name)
        self.l2.addItem(gpk_value)
        self.value_list.append(gpk_value)
        self.l2.nextRow()

    def get_data(self):
        return self.data
   

    def update(self, data):

        self.data = data

        grath = self.grath_list[0]
        grath.update(self.data)

        value = self.value_list[0]
        value.update(self.data)


    def start(self, data):
        self.plot_init()
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(lambda: self.update(data))
        timer.start(TIME_IMITATOR) 
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            self.app.exec_()   

def main():
    ex = Sarz()
    ex.start(random.randint(10,20))

if __name__ == '__main__':
    main()
