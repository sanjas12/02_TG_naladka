import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PyQt5 import QtGui, QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random


class mainWindow(QtGui.QTabWidget):
    def __init__(self, parent=None):
        super(mainWindow, self).__init__(parent)

        # GUI configuration
        self.tab1 = QtGui.QWidget()
        self.addTab(self.tab1, "Tab 1")
        self.figure = plt.figure(figsize=(10, 5))
        self.resize(800, 480)
        self.canvas = FigureCanvas(self.figure)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.plot()

    def plot(self):
        data = [random.random() for i in range(10)]
        ax = self.figure.add_subplot(111)
        ax.hold(False)
        ax.plot(data, '*-')
        self.canvas.draw()


def main():
    app = QtGui.QApplication(sys.argv)
    main = mainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()