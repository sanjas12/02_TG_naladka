import pyqtgraph as pg
import numpy as np
import random
from settings import *

class graph_gpk(pg.PlotItem):
     
    def __init__(self, pen, parent=None, name=None, labels=None, title='Давление в ГПК(кг/см²)',
     viewBox=None, axisItems=None, number=NUMBER_POINT_TO_GRATH, enableMenu=True, **kargs):
        super().__init__(parent, name, labels, title, viewBox, axisItems, enableMenu, **kargs)
        
        self.addLegend()
        self.hideAxis('bottom')
        self.number_point_to_grath = number

        self.sensor_plot = self.plot(pen=pen)

        # self.sensor_data = np.linspace(0, 0)
        self.sensor_data = np.zeros(self.number_point_to_grath)

        self.ptr = 0


    def update(self, value):
        self.sensor_data[:-1] = self.sensor_data[1:]
        self.sensor_data[-1] = float(value)
        self.ptr += 1
        # print(self.sensor_data)
        self.sensor_plot.setData(self.sensor_data)

        self.sensor_plot.setPos(self.ptr, 0)

    def get_data(self):
        return self.sensor_data[-1]
