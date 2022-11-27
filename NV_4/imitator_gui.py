import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMainWindow
from graths.grath_gpk import graph_gpk
from graths.grath_time import graph_time
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from data_base import data_base

# class ImitatorGui(QMainWindow):
class ImitatorGui(QWidget):

    def __init__(self):
        super().__init__()
        self.width = 640
        self.height = 400
        self.setup_ui()

    def setup_ui(self):
        # self.setGeometry(10, 10, self.width, self.height)
        self.setWindowTitle(__file__)

        pg.setConfigOption('background', (33, 33, 33))
        pg.setConfigOption('foreground', (197, 198, 199))
        # Interface variables
        view = pg.GraphicsView()
        Layout = pg.GraphicsLayout()
        view.setCentralItem(Layout)
        view.show()
        
        view.setWindowTitle('Flight monitoring')
        view.resize(1200//2, 700//2)
        

        # Fonts for text items
        font = QtGui.QFont()
        font.setPixelSize(90)
        
        # declare random data
        data_ran = data_base()

        # buttons style
        style = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"

        # Declare graphs
        # Button 1
        proxy = QtWidgets.QGraphicsProxyWidget()
        save_button = QtWidgets.QPushButton('Start')
        save_button.setStyleSheet(style)
        save_button.clicked.connect(data_ran.start)
        proxy.setWidget(save_button)

        # Button 2
        proxy2 = QtWidgets.QGraphicsProxyWidget()
        end_save_button = QtWidgets.QPushButton('Stop')
        end_save_button.setStyleSheet(style)
        end_save_button.clicked.connect(data_ran.stop)
        proxy2.setWidget(end_save_button)
            
        # GPK grath
        self.gpk = graph_gpk()
        self.time = graph_time(font=font)
        
        ## Setting the graphs in the layout 
        # Title at top
        text = """
        My imitator
        """

        Layout.addLabel(text, col=1, colspan=21)
        Layout.nextRow()

        # Put vertical label on left side
        Layout.addLabel('LIDER - ATL research hotbed', angle=-90, rowspan=3)
                        
        Layout.nextRow()

        lb = Layout.addLayout(colspan=21)
        lb.addItem(proxy)
        lb.nextCol()
        lb.addItem(proxy2)

        Layout.nextRow()

        l1 = Layout.addLayout(colspan=20, rowspan=2)
        l11 = l1.addLayout(rowspan=1, border=(83, 83, 83))

        # Altitude, speed
        l11.addItem(self.gpk)
        l1.nextRow()

        # Acceleration, gyro, pressure, temperature
        l12 = l1.addLayout(rowspan=1, border=(83, 83, 83))

        # Time, battery and free fall graphs
        l2 = Layout.addLayout(border=(83, 83, 83))
        l2.addItem(self.time)
        l2.nextRow()
        

        if  True:
            timer = pg.QtCore.QTimer()
            timer.timeout.connect(self.update)
            timer.start(500)
        else:
            print("something is wrong with the update call")


        self.show()

    # you have to put the position of the CSV stored in the value_chain list
    # that represent the date you want to visualize
    def update(self):
        try:
            value_chain = [0, 0]
            self.gpk.update(value_chain[1])
            self.time.update(value_chain[0])
            data_base.guardar(value_chain)
        except IndexError:
            print('starting, please wait a moment')

def main():
    app = QApplication(sys.argv)
    ex = ImitatorGui()
    ex.show
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
