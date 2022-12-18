import sys
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
import pyqtgraph as pg
# from communication import Communication
from data_base import data_base
# from PyQt5.QtWidgets import QPushButton
from graphs.graph_gpk import graph_gpk
from graphs.value_gpk import value_gpk
from connect_to_PLC import ConnectPLC
from model_NV import ModelNV
from settings import *

pg.setConfigOption('background', (33, 33, 33))
pg.setConfigOption('foreground', (197, 198, 199))
# Interface variables
app = QtWidgets.QApplication(sys.argv)
view = pg.GraphicsView()
Layout = pg.GraphicsLayout()
view.setCentralItem(Layout)
view.show()
# view.setWinowTitle('Imitator')
view.resize(*RES_IMITATOR)

# declare object for serial Communication
# ser = Communication()
# declare object for storage in CSV
data_base = data_base()
# Fonts for text items
font = QtGui.QFont()
font.setPixelSize(FONT_SIZE)

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
prs_cur_grath = graph_gpk(title='Медиана', pen='g')
gpk_value_0 = value_gpk(color='r', font=font, title='Первый датчик')
gpk_value_1 = value_gpk(color='b', font=font, title='Второй датчик')
gpk_value_2 = value_gpk(color='g', font=font, title='Третий датчик')
prs_cur = graph_gpk(color='g', font=font, title='Медиана из PLC')

## Setting the graphs in the layout 
# Title at top
text = """My Imitator"""
# Layout.addLabel(text, col=1, colspan=21, font=font)
Layout.addLabel(text, colspan=100, font=font)
Layout.nextRow()

# Put vertical label on left side
Layout.addLabel('Давление в ГПК(кг/см²).', angle=-90, rowspan=3)
Layout.nextRow()

# lb = Layout.addLayout(colspan=21)
# lb.addItem(proxy)
# lb.nextCol()
# lb.addItem(proxy2)

# Layout.nextRow()

# First column
l1 = Layout.addLayout(colspan=20, rowspan=2)
l1.addItem(gpk_0)
l1.nextRow()
l1.addItem(gpk_1)
l1.nextRow()
l1.addItem(gpk_2)

# Second column
l2 = Layout.addLayout(border=(83, 83, 83))
l2.addItem(gpk_value_0)
l2.nextRow()
l2.addItem(gpk_value_1)
l2.nextRow()
l2.addItem(gpk_value_2)

# Third column
l3 = Layout.addLayout(colspan=20, rowspan=2)
l3.addItem(prs_cur_grath)
l3.nextRow()

# Fourth column
l4 = Layout.addLayout()
l4.addItem(prs_cur)
l4.nextRow()

# Time
# l2 = Layout.addLayout(border=(83, 83, 83))
# l2.addItem(time)

model = ModelNV()

# you have to put the position of the CSV stored in the value_chain list
# that represent the date you want to visualize
def update():
    try:
        # init value imitator
        data = model.get_data_to_PLC()
        pressure = data[:3]
        data_to_PLC = data[:4]
        for i in range(3):
            data_to_PLC[i] = data_to_PLC[i] * 100
        print(pressure, "to grath")
        
        c.write_to_PLC(data_to_PLC)
        pr= c.read_PLC()
        
        gpk_0.update(pressure[0])
        gpk_1.update(pressure[1])
        gpk_2.update(pressure[2])
        prs_cur_grath.update(pr)
        gpk_value_0.update(pressure[0])
        gpk_value_1.update(pressure[1])
        gpk_value_2.update(pressure[2])
        prs_cur.update(pr)
        
    except IndexError:
        print('starting, please wait a moment')

c = ConnectPLC()

# if(ser.isOpen()) or (ser.dummyMode()):
# if True:
if True:
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(TIME_MAIN)

else:
    print("something is wrong with the update call")
# Start Qt event loop unless running in interactive mode.

if __name__ == '__main__':
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
