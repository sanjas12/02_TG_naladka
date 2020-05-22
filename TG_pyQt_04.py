import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import SpanSelector
from tkinter.filedialog import *                # для askopenfilename
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from tkinter.ttk import *  # для combobox
import csv
from tkinter import filedialog as fd
import pandas as pd
from memory_profiler import profile
from grath_from_tg_static_7_class import TG_naladka
from numpy import arange, sin, pi
import random

# класс для Главного окна
class Window_Main(QDialog):

    def __init__(self):
        super(Window_Main, self).__init__()

        self.setup_UI()

    def setup_UI(self):
        self.setWindowTitle('Всякая ересь...Qt')

        # для передачи чила между классами (вывод числа точек)
        self.value = QLineEdit()

        # первый Frame Главного окна
        self.horizontalGroupBox = QGroupBox('Тут тук')
        layout = QGridLayout()
        button_step = QPushButton('Шаги')
        button_step.clicked.connect(self.number_point)
        layout.addWidget(button_step, 0, 0)
        layout.addWidget(QPushButton('Скорости'), 0, 1)
        layout.addWidget(QPushButton('ОЗ одного канала'), 1, 0)
        layout.addWidget(QPushButton('ОЗ одной стороны'), 1, 1)

        self.horizontalGroupBox.setLayout(layout)

        # не надо отображать self.value = QLineEdit() он используется
        # только для предачи переменной между классами
        # layout.addWidget(self.value, 2, 0)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()

    # поиска числа отображаемых точек графика
    def number_point(self):
        print('start_number_point')

        time_data = self.create_time()

        # print('number_point', time_data[1], type(time_data[1]))

        # self.point_f = 10
        # для передачи чила между классами (вывод числа точек)
        self.value_div = QLineEdit()
        self.value_div.setText('100')

        print(int(self.value_div.text()))

        # point_view = int(time_data[1] / self.point_f)
        point_view = int(time_data[1] / int(self.value_div.text()))

        # self.value.text(self.point_view)

        self.value.setText(str(point_view))

        print('точек отрисовки point_view :', point_view)

        # отрисовка Second окна (ШАГИ)
        self.open_new_window()

        print('end number_point')

    # создание колонки Время
    def create_time(self):
        print('start_create_timre')

        # поиск количества строк
        # global df
        num_rows = int(self.open_files())

        # num_rows = len(df.index)

        self.time_data = []
        summa = 0
        for z in range(num_rows):
            self.time_data.append(float('%.2f' % summa))
            summa = summa + 0.01

        print('длина времени self.time_data :', len(self.time_data))

        print('end_create_timre')

        return self.time_data, len(self.time_data)

    # метод считывания данных из файла
    def open_files(self):
        print('start_openFiles')
        # self.files = QFileDialog.getOpenFileNames(self, 'Открыть шаги')
        files = QFileDialog.getOpenFileName(self, 'Открыть шаги', 'csv', '*.csv')

        GSM_A_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
        GSM_B_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
        Zadanie_column = 'Значение развертки. Положение ГСМ'  # Значение развертки. Положение ГСМ
        Time_column = 'миллисекунды'  # время

        fields = [GSM_A_column, GSM_B_column, Zadanie_column, Time_column]

        # for file_ in my_csv:
        self.df = pd.read_csv(open(files[0], 'r'), header=0, delimiter=';', usecols=fields)

        # print(df.info())

        # self.number_point()

        print('end_openFiles')

        return len(self.df.index)

    # метод открытия нового окна
    def open_new_window(self):
        print('start_open_new_window')

        dialog = Window_Steps()
        # print('11')
        dialog.label_step.setText(self.value.text())
        # print('12')
        dialog.exec_()
        print('end_open_new_window')

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
        self.button = QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        # combobox для изменения точек графика
        list_dot = ['10', '100', '1000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(1)

        self.label_step = QLabel(self)

        # set the Layout
        vertical = QVBoxLayout()
        vertical.addWidget(self.canvas)
        vertical.addWidget(self.toolbar)

        grid = QGridLayout()
        grid.addWidget(QLabel('Число отображаемых точек: '), 0, 0)
        grid.addWidget(QLabel('Число для деления данных:'), 1, 0)
        grid.addWidget(self.combobox_dot, 0, 1)
        grid.addWidget(self.label_step, 1, 1)
        grid.addWidget(self.button, 2, 0)


        self.horizontalGroupBox = QGroupBox()
        self.horizontalGroupBox.setLayout(vertical)

        self.horizontalGroupBox_2 = QGroupBox()
        self.horizontalGroupBox_2.setLayout(grid)

        windowLayout = QHBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.horizontalGroupBox_2)
        self.setLayout(windowLayout)

        # self.show()

    def plot(self):
        # random data
        data = [random.random() for i in range(10)]

        # instead of ax.hold(False)
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        # ax.hold(False) # deprecated, see above

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    ex = Window_Main()
    ex.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Каряво закрыли")

if __name__ == '__main__':
    main()