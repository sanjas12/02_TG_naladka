from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random


# класс для Second окна (Шаги)
class Window_Steps(QDialog):

    def __init__(self, parent=None):
        super(Window_Steps, self).__init__(parent)
        self.setWindowTitle('Шаги')
        # self.setupPlot

        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QPushButton('Обновить')
        self.button.clicked.connect(self.plot)

        # combobox для изменения точек графика
        list_dot = ['10', '100', '1000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(0)

        self.label_step = QLabel(self)

        # set the Layout
        vertical = QVBoxLayout()
        vertical.addWidget(self.canvas)
        vertical.addWidget(self.toolbar)

        grid = QGridLayout()
        grid.addWidget(QLabel('Число отображаемых точек: '), 1, 0)
        grid.addWidget(QLabel('Число для деления данных:'), 0, 0)
        grid.addWidget(self.combobox_dot, 0, 1)
        grid.addWidget(self.label_step, 1, 1)
        grid.addWidget(self.button, 2, 0)


        self.horizontalGroupBox = QGroupBox()
        self.horizontalGroupBox.setLayout(vertical)

        self.horizontalGroupBox_2 = QGroupBox()
        self.horizontalGroupBox_2.setLayout(grid)

        windowLayout = QGridLayout()
        windowLayout.addWidget(self.horizontalGroupBox, 0, 0)
        windowLayout.addWidget(self.horizontalGroupBox_2, 0, 1)
        self.setLayout(windowLayout)

        # self.show()

    def update_label(self):
        pass

    def plot(self):

        self.update_label()

        # random data
        data = [random.random() for i in range(10)]

        # instead of ax.hold(False)
        self.figure.clear()

        # self.figure.legends('sdsdad')

        # create an axis
        ax = self.figure.add_subplot(111)

        step = int(self.combobox_dot.currentText())

        # view_pot = int(self.label_step.text())

        view_pot = int(int(self.label_step.text())/step)

        # self.label_step.setText(view_pot)

        print(step, view_pot)




        # ex

        # self..label_step.setText(self.value.text())

        # data_2 = Window_Main.df
        # print(print(data_2.info()))

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()
