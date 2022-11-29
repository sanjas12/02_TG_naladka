import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
from graphs.graph_value import graph_value
from PyQt5.QtWidgets import QApplication, QWidget
from data_base import data_base
from model_NV import ModelNV
import time 
from connect_to_PLC import ConnectPLC

class ImitarorWindow(QWidget):

    def __init__(self):
        
        self.data = None
        
        # Fonts for text items
        font = QtGui.QFont()
        font.setPixelSize(40)
        
        self.gpk = graph_gpk(title='Давление в ГПК(кг/см²). Медианна', pen='r')
        self.setup_ui()

    def setup_ui(self):
        pg.setConfigOption('background', (33, 33, 33))
        pg.setConfigOption('foreground', (197, 198, 199))

        # Interface variables
        # app = QtWidgets.QApplication(sys.argv)
        view = pg.GraphicsView()
        Layout = pg.GraphicsLayout()
        view.setCentralItem(Layout)
        view.show()
        view.setWindowTitle('SAZR')
        view.resize(1200//2, 700//2)

        # buttons style
        style = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"

        ## Setting the graphs in the layout 
        # Title at top
        text = """SARZ"""
        Layout.addLabel(text, col=1, colspan=21)
        Layout.nextRow()

        # Put vertical label on left side
        Layout.addLabel('Давление в ГПК(кг/см²).', angle=-90, rowspan=3)
        Layout.nextRow()

        lb = Layout.addLayout(colspan=21)
        lb.addItem(proxy)
        lb.nextCol()
        lb.addItem(proxy2)

        Layout.nextRow()

        # First column
        l1 = Layout.addLayout(colspan=20, rowspan=2)
        l1.addItem(self.gpk_0)
        l1.nextRow()
        l1.addItem(self.gpk_1)
        l1.nextRow()
        l1.addItem(self.gpk_2)

        # Second column
        l2 = Layout.addLayout(border=(83, 83, 83))
        l2.addItem(self.gpk_value_0)
        l2.nextRow()
        l2.addItem(self.gpk_value_1)
        l2.nextRow()
        l2.addItem(self.gpk_value_2)

        # Time
        l2 = Layout.addLayout(border=(83, 83, 83))
        l2.addItem(self.time)

    def update(self):
        try:
            # init value imitator
            value_chain = [40, 40, 40, 1]
            
            self.gpk_0.update(value_chain[0])
            self.gpk_1.update(value_chain[1])
            self.gpk_2.update(value_chain[2])
            self.gpk_value_0.update(self.gpk_0.get_data())
            self.gpk_value_1.update(self.gpk_1.get_data())
            self.gpk_value_2.update(self.gpk_2.get_data())
            
            self.time.update(value_chain[3])
        except IndexError:
            print('starting, please wait a moment')

        if True:
            timer = pg.QtCore.QTimer()
            timer.timeout.connect(self.update)
            timer.start(1000)

    def set_data(self, data):
        self.data = data
   
def main():
    app = QApplication(sys.argv)
    model = ModelNV()
    ex = ImitarorWindow()
    while True:
        model.update_data()
        new_data = model.get_data()
        print(new_data)
        ex.set_data(new_data)
        time.sleep(1)
    ex.show()
    # if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        # QtWidgets.QApplication.instance().exec_()
    app.exec_()


if __name__ == '__main__':
    main()