import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from graphs.value_gpk import value_gpk
from graphs.graph_gpk import graph_gpk
from settings import *
from connect_to_PLC import ConnectPLC
from model_NV import ModelNV

class Imitator(object):
    def __init__(self, model, connect):
        # try:
        # self.app = QtWidgets.QApplication(sys.argv)
        self.app = QtWidgets.QApplication(sys.argv)
        # except RuntimeError:
        #     self.app = QtWidgets.QApplication.instance()
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout(border=(100,100,100))
       
        self.font = QtGui.QFont()
        self.font.setPixelSize(FONT_SIZE)

        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle('Imitator')
        self.view.resize(*RES_IMITATOR)
        self.view.show()


        # te = pg.TextItem("Давление в ГПК(кг/см²).")
        # # te.setText()
        # # te.setFont(self.font)
        # # self.layout.addLabel(te, angle=-90, rowspan=3)
        # self.layout.addItem(te)
        # self.layout.nextRow()


        # First column
        self.l1 = self.layout.addLayout()
        
        # Second column
        self.l2 = self.layout.addLayout()

        self.model = model
        self.c = connect
        
        self.grath_list = []
        self.value_list = []

        self.title = 'Давление в ГПК'
        self.sensor_name = ('Первый датчик', 'Второй датчик', 'Третий датчик')
        self.color_name = ('r', 'g', 'b')
        self.number_point_to_grath = NUMBER_POINT_TO_GRATH


    def plot_init(self):
        for c, name in zip(self.color_name, self.sensor_name):
            # create list graths
            gpk = graph_gpk(pen=c, name=name)
            self.l1.addItem(gpk)
            self.grath_list.append(gpk)
            self.l1.nextRow()

            # create list value
            gpk_value = value_gpk(color=c, font=self.font, name=name)
            self.l2.addItem(gpk_value)
            self.value_list.append(gpk_value)
            self.l2.nextRow()

    def get_data(self):
        return self.data_pressure
    
    def update(self):
        self.data_pressure = self.model.get_data_to_PLC()[:3]
        self.c.write_to_PLC(self.data_pressure)
        self.c.read_PLC()
        # print("data_pressure", data_pressure)
        for data, _line, _value in zip(self.data_pressure, self.grath_list, self.value_list):
            line = _line
            line.update(data/100)
            value = _value
            value.update(data/100)

            # value = self.value_list[0]
            # value.informViewBoundsChanged()
            # value.update(data)


    def start(self):
        self.plot_init()
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(TIME_IMITATOR) 
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            # self.app.exec_() 
            QtWidgets.QApplication.instance().exec_()  

def main():
    ex = Imitator(ModelNV(), ConnectPLC())
    ex.start()


if __name__ == '__main__':
    main()
