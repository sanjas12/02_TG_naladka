import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from graphs.value_gpk import value_gpk
from graphs.graph_gpk import graph_gpk
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSlider
from settings import *
from connect_to_PLC import ConnectPLC
from model_NV import ModelNV

class Imitator(object):
    def __init__(self, tg_name, model, connect):
        try:
            self.app = QtWidgets.QApplication(sys.argv)
        except RuntimeError:
            self.app = QtWidgets.QApplication.instance()
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout(border=(100,100,100))
       
        self.font = QtGui.QFont()
        self.font.setPixelSize(FONT_SIZE)

        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle('Imitator ' + tg_name)
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
        
        # Third column
        # self.l3 = self.layout.addLayout()
        # self.slider = QSlider(self)
        # self.slider.setOrientation(Qt.Vertical)
        # self.l3.addItem(self.slider)
        # self.l3.nextRow()

        # self.minimum = 45
        # self.maximum = 48
        # self.laben_l3 = '5'
        # self.slider.valueChanged.connect(self.setLabelValue)
        # self.x = None
        # self.setLabelValue(self.slider.value())


        self.model = model
        self.c = connect
        
        self.grath_list = []
        self.value_list = []

        self.title = 'Давление в ГПК'
        self.sensor_name = ('Первый датчик', 'Второй датчик', 'Третий датчик')
        self.color_name = ('r', 'g', 'b')
        self.number_point_to_grath = NUMBER_POINT_TO_GRATH


    def setLabelValue(self, value):
        self.x = self.minimum + (float(value) / (self.slider.maximum() - self.slider.minimum())) * (
        self.maximum - self.minimum)
        self.label2.setText("{0:.4g}".format(self.x))

        
    def plot_init(self):
        for c, name in zip(self.color_name, self.sensor_name):
            # create list graths
            gpk = graph_gpk(pen=c, name=name)
            self.l1.addItem(gpk)
            self.grath_list.append(gpk)
            self.l1.nextRow()

            # create list value
            # gpk_value = value_gpk(color=c, font=self.font, name=name)
            # self.l2.addItem(gpk_value)
            # self.value_list.append(gpk_value)
            # self.l2.nextRow()


    def get_data(self):
        return self.data_pressure
    

    def update(self):
        self.data = self.model.get_data_to_PLC()
        self.c.write_to_PLC(self.data)
        self.c.read_PLC()
        # print("data_pressure", data_pressure)
        for data, _line, _value in zip(self.data, self.grath_list, self.value_list):
            line = _line
            line.update(data/100)
            # value = _value
            # value.update(data/100)


    def start(self):
        self.plot_init()
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(TIME_IMITATOR) 
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtWidgets.QApplication.instance().exec_()  

def main():
    model = ModelNV()
    # model2 = ModelNV()
    tg1 = ConnectPLC(TG1_CABINET_NUMBER)
    # tg2 = ConnectPLC(TG2_CABINET_NUMBER)
    ex = Imitator("ТГ-1", model, tg1)
    # ex2 = Imitator("ТГ-2", model2, tg2)
    ex.start()
    # ex2.start()


if __name__ == '__main__':
    main()
