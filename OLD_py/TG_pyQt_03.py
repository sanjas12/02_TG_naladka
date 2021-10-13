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
from matplotlib.figure import Figure
from tkinter.ttk import *  # для combobox
import csv
from tkinter import filedialog as fd
import pandas as pd
from memory_profiler import profile
from grath_from_tg_static_7_class import TG_naladka
from numpy import arange, sin, pi

# класс для Главного окна
class Window_Main(QDialog):

    def __init__(self):
        super().__init__()
        self.setup_UI()

    def setup_UI(self):
        self.setWindowTitle('Всякая ересь...Qt')

        # для передачи чила между классами (вывод числа точек)
        self.value = QLineEdit()

        # первый Frame Главного окна
        self.horizontalGroupBox = QGroupBox('Тут тук')
        layout = QGridLayout()
        button_step = QPushButton('Шаги')
        layout.addWidget(button_step, 0, 0)
        button_step.clicked.connect(self.number_point)
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
        print('start_openDialog')

        dialog = Window_Steps(self)
        # print('11')
        dialog.label_step.setText(self.value.text())
        # print('12')
        dialog.exec_()
        print('end_openDialog')

    def compute_initial_figure(self):
        pass

# класс для Second окна (Шаги)
class Window_Steps(QDialog):

    def __init__(self, parent=None):
        super(Window_Steps, self).__init__(parent)
        self.initUI('Шаги')

    def initUI(self, name_window):
        self.setWindowTitle(name_window)

        # первый Frame
        layout_step = QGridLayout()

        layout_step.addWidget(QLabel('Число для деления данных:'), 0, 0)

        list_dot = ['10', '100', '1000']
        combobox_dot = QComboBox()
        combobox_dot.addItems(list_dot)
        combobox_dot.setCurrentIndex(1)
        layout_step.addWidget(combobox_dot, 0, 1)

        layout_step.addWidget(QPushButton('Обновить'), 0, 2)

        layout_step.addWidget(QLabel('Число отображаемых точек: '), 1, 0)

        self.label_step = QLabel(self)
        layout_step.addWidget(self.label_step, 1, 1)

        self.setLayout(layout_step)

    def re_open(self):
        # Window_Main.openDialog.s
        Window_Main.number_point()

def main():
    app = QApplication(sys.argv)
    ex = Window_Main()
    ex.show()
    # sys.exit(app.exec_())
    try:
        sys.exit(app.exec_())
    except:
        print("Каряво закрыли")

if __name__ == '__main__':
    main()
