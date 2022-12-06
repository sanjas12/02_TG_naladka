import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
# from communication import Communication
from data_base import data_base
# from PyQt5.QtWidgets import QPushButton
from graphs.graph_gpk import graph_gpk
from graphs.graph_time import graph_time
from graphs.graph_value import graph_value
from connect_to_PLC import ConnectPLC
from model_NV import ModelNV

pg.setConfigOption('background', (33, 33, 33))
pg.setConfigOption('foreground', (197, 198, 199))
# Interface variables
app = QtWidgets.QApplication(sys.argv)
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
view.show()
# view.setWinowTitle('Imitator')
view.resize(900//2, 700//2)

# declare object for serial Communication
# ser = Communication()
# declare object for storage in CSV
data_base = data_base()
# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(40)

# buttons style
style = "background-color:rgb(29, 185, 84);color:rgb(0,0,0);font-size:14px;"


# Declare graphs
# Button 1
proxy = QtWidgets.QGraphicsProxyWidget()
save_button = QtWidgets.QPushButton('Start storage')
save_button.setStyleSheet(style)
save_button.clicked.connect(data_base.start)
proxy.setWidget(save_button)

# Button 2
proxy2 = QtWidgets.QGraphicsProxyWidget()
end_save_button = QtWidgets.QPushButton('Stop storage')
end_save_button.setStyleSheet(style)
end_save_button.clicked.connect(data_base.stop)
proxy2.setWidget(end_save_button)

# Graphs
gpk_0 = graph_gpk(title='Первый датчик', pen='r')
gpk_1 = graph_gpk(title='Второй датчик', pen='b')
gpk_2 = graph_gpk(title='Третий датчик', pen='g')
gpk_value_0 = graph_value(color='r', font=font)
gpk_value_1 = graph_value(color='b', font=font)
gpk_value_2 = graph_value(color='g', font=font)
time = graph_time(font=font)


## Setting the graphs in the layout 
# Title at top
text = """My Imitator"""
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

l1 = Layout.addLayout(colspan=20, rowspan=2)
# l11 = l1.addLayout(rowspan=2, border=(83, 83, 83))

# First column
l1.addItem(gpk_0)
l1.nextRow()
l1.addItem(gpk_1)
l1.nextRow()
l1.addItem(gpk_2)

# Second column
l2 = Layout.addLayout(border=(83, 83, 83))
# print(gpk_0.get_data)
l2.addItem(gpk_value_0)
l2.nextRow()
l2.addItem(gpk_value_1)
l2.nextRow()
l2.addItem(gpk_value_2)

# Time
# l2 = Layout.addLayout(border=(83, 83, 83))
# l2.addItem(time)


# you have to put the position of the CSV stored in the value_chain list
# that represent the date you want to visualize
def update():
    try:
        # init value imitator
        value_chain = [40, 40, 40, 0]
        gpk_0.update(value_chain[0])
        gpk_1.update(value_chain[1])
        gpk_2.update(value_chain[2])
        # print(gpk_0.get_data())       
        gpk_value_0.update(gpk_0.get_data())
        gpk_value_1.update(gpk_1.get_data())
        gpk_value_2.update(gpk_2.get_data())
        
        time.update(value_chain[3])
    except IndexError:
        print('starting, please wait a moment')

c = ConnectPLC()
model = ModelNV()
# while:


# if(ser.isOpen()) or (ser.dummyMode()):
if True:
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(1000)
    print(model.get_data_to_PLC()[:4])
    c.data_transfer(model.get_data_to_PLC()[:4])
else:
    print("something is wrong with the update call")
# Start Qt event loop unless running in interactive mode.

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
