import sys
from graphs.graph_value import graph_value
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from model_NV import ModelNV

class BasePlot(object):
    def __init__(self):
        try:
            self.app = QtWidgets.QApplication(sys.argv)
        except RuntimeError:
            self.app = QtWidgets.QApplication.instance()
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout(border=(100,100,100))
       
        # First column
        # self.l1 = self.layout.addLayout()
        self.l1 = self.layout.addLayout(colspan=20, rowspan=2)
        
        # Second column
        self.l2 = self.layout.addLayout()
        self.view.setCentralItem(self.layout)
        self.view.setWindowTitle('Imitator')
        self.view.resize(900//2, 700//2)
        self.view.show()

        self.model = ModelNV()
        
        self.plot_list = []
        self.value_list = []

        self.sensor_name = ('Первый датчик', 'Второй датчик', 'Третий датчик')
        self.color_name = ('r', 'g', 'b')
        self.number_point_to_grath = 10
        self.y_Data = np.zeros(self.number_point_to_grath)


        # self.text_to_value = pg.TextItem("Start" , anchor=(0.5, 0.5))
        self.text_to_value = "Start"
        self.font = QtGui.QFont()
        self.font.setPixelSize(40)

    def plot_init(self):
        for c, name in zip(self.color_name, self.sensor_name):
            
            # create list graths
            new_plot = self.l1.addPlot()
            new_plot.plot(np.zeros(self.number_point_to_grath))
            new_plot.setTitle(name)
            self.plot_list.append(new_plot.listDataItems()[0])
            self.l1.nextRow()
            
            # create list value
            # # new_value = self.l2.addLabel(self.text_to_value, font=self.font)
            # new_value = self.l2.addItem()
            # # pg.TextItem("test", anchor=(0.5, 0.5), color=c)
            # new_value.setFont(self.font)
            # self.value_list.append(new_value)
            # # self.value_list.append(new_value)
            # self.l2.nextRow()

            gpk_value = graph_value(color=c, font=self.font, name=name, title=name)
            new_value = self.l2.addItem(gpk_value)
            self.value_list.append(gpk_value)
            self.l2.nextRow()

    def update_data(self, data):
        self.data_pressure = data
    
    def update(self):
        data_pressure = self.model.get_data_to_PLC()[:3]
        # self.update_data()
        # self.data_pressure = data
        print("data_pressure", data_pressure)
        # for data, _line, _plot in zip(data_pressure, self.plot_list, self.value_list):
        # print(data, _line, _plot)
        line = self.plot_list[0]
        # line = _line
        line.informViewBoundsChanged()
        # x_data = np.arange(len(line.yData))
        self.y_Data = np.roll(self.y_Data, -1)
        
        self.y_Data[-1] = data_pressure[0]
        # self.y_Data[-1] = data
        
        line.setData(self.y_Data)
        line.xClean = line.yClean = None
        line.xDisp = None
        line.yDisp = None
        line.updateItems()
        line.sigPlotChanged.emit(line)

        value = self.value_list[0]
        # value = _plot
        value.update(data_pressure[0])
        # value.update(data)

    def start(self):
        # print('start', data)
        self.plot_init()
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1000) 
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            self.app.exec_()   

def main():
    from model_NV import ModelNV
    model = ModelNV()
    ex = BasePlot()
    ex.start()


if __name__ == '__main__':
    main()
