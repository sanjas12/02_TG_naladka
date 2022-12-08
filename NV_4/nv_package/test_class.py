import random
import signal
import socket
import sys

import numpy as np
import pyqtgraph as pg
# import serial
# from pyqtgraph.Qt import QtCore, QtGui
# from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from graphs.graph_gpk import graph_gpk
from graphs.graph_time import graph_time
from graphs.graph_value import graph_value
from connect_to_PLC import ConnectPLC
from model_NV import ModelNV

class BasePlot(object):
    # def __init__(self, stream, **kwargs):
    def __init__(self):
        # self.stream = stream
        try:
            # self.app = QtGui.QApplication([])          # - ORIGINAL
            self.app = QtWidgets.QApplication(sys.argv)
        except RuntimeError:
            # self.app = QtGui.QApplication.instance()   # - ORIGINAL
            self.app = QtWidgets.QApplication.instance()
        self.view = pg.GraphicsView()
        # self.layout = pg.GraphicsLayout(border=(100,100,100))
        self.layout = pg.GraphicsLayout()
        # self.view.closeEvent = self.handle_close_event
        # self.layout.closeEvent = self.handle_close_event
        self.view.setCentralItem(self.layout)
        self.view.show()
        self.view.setWindowTitle('Software Oscilloscope')
        self.view.resize(800,600)
        self.plot_list = []
        self.gpk_0 = graph_gpk(title='Первый датчик', pen='r')
        self.gpk_1 = graph_gpk(title='Второй датчик', pen='b')
        self.gpk_2 = graph_gpk(title='Третий датчик', pen='g')
        self.time = graph_time()
        # self.c = ConnectPLC()
        self.model = ModelNV()
        self.number_point_to_grath = 10
        print("end _init_")

    # def open_stream(self):
    #     print("Opening Stream")
    #     self.stream.open()
        
    # def close_stream(self):
    #     if hasattr(self.stream, 'flushInput'):
    #         self.stream.flushInput()
    #     if hasattr(self.stream, 'flushOutput'):
    #         self.stream.flushOutput()
    #     self.stream.close()
    #     print("Stream closed")
        
    def handle_close_event(self, event):
        # self.close_stream()
        self.app.exit()

    def plot_init(self):
        # for i in range(3):
        new_plot = self.layout.addPlot()
        new_plot.plot(np.zeros(self.number_point_to_grath))
        self.plot_list.append(new_plot.listDataItems()[0])
        self.layout.nextRow()
    
    def update(self):
        # try:
        # init start value imitator
        value_chain = [40, 40, 40, 0]
        self.gpk_0.update(value_chain[0])
        self.gpk_1.update(value_chain[1])
        self.gpk_2.update(value_chain[2])
        # print(gpk_0.get_data())       
        # self.gpk_0.update(self.gpk_0.get_data())
        # self.gpk_1.update(self.gpk_1.get_data())
        # self.gpk_2.update(self.gpk_2.get_data())
        
        self.time.update(value_chain[3])

        # print(self.gpk_0.get_data(), self.gpk_1.get_data(), self.gpk_2.get_data())
        stream_data = (self.gpk_0.get_data(), self.gpk_1.get_data(), self.gpk_2.get_data())
        print("stream_data_",stream_data)
        # for data, line in zip(stream_data, self.plot_list):
            # print(data, line)
        line = self.plot_list[0]
        line.informViewBoundsChanged()


        # line.xData = np.arange(len(line.yData))
        line.xData = line.xData._replace(np.arange(len(line.yData)))
        print("x - ", line.xData)
        line.yData = np.roll(line.yData, -1)
        print("y - ", line.yData)
        line.yData[-1] = stream_data[0]
        line.xClean = line.yClean = None
        line.xDisp = None
        line.yDisp = None
        line.updateItems()
        line.sigPlotChanged.emit(line)

        # except IndexError:
        #     print('starting, please wait a moment')


    def start(self):
        # self.open_stream()
        self.plot_init()
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(1000)
        pressure_dates = self.model.get_data_to_PLC()[:4]
        print(pressure_dates)
        # self.c.data_transfer(self.model.get_data_to_PLC()[:4])   
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            self.app.exec_()   

# class SerialPlot(BasePlot):
#     def __init__(self, com_port, baud_rate, **kwargs):
#         self.serial_port = serial.Serial()
#         self.serial_port.baudrate = baud_rate
#         self.serial_port.port = com_port
#         super(SerialPlot, self).__init__(self.serial_port, **kwargs)

# class SocketClientPlot(BasePlot):
#     def __init__(self, address, port, **kwargs):
#         self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.socket_params = (address, port)
#         self.socket.connect((address, port))
#         self.stream = self.socket.makefile()  
#         super(SocketClientPlot, self).__init__(self.stream, **kwargs)
        
#     def open_stream(self):
#         pass
        
#     def close_stream(self):
#         self.socket.close()
#         self.stream.close()

# class GenericPlot(BasePlot):
#     def __init__(self, stream, **kwargs):
#         if hasattr(stream, 'open') \
#         and hasattr(stream, 'close') \
#         and hasattr(stream, 'readline'):
#             super(GenericPlot, self).__init__(stream, **kwargs)
#         else:
#             raise BadAttributeError("One of the open/close/readline attributes is missing")  



def main():
    # app = QtWidgets.QApplication(sys.argv)
    ex = BasePlot()
    ex.start()


if __name__ == '__main__':
    main()
