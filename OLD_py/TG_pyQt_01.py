import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow
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

# class MyMplCanvas(FigureCanvas):
#     """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
#
#     def __init__(self, parent=None, width=5, height=4, dpi=100):
#         fig = Figure(figsize=(width, height), dpi=dpi)
#         self.axes = fig.add_subplot(111)
#
#         self.compute_initial_figure()
#
#         FigureCanvas.__init__(self, fig)
#         self.setParent(parent)
#
#         FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
#         FigureCanvas.updateGeometry(self)
#
#     def compute_initial_figure(self):
#         pass
#
# class MyStaticMplCanvas(MyMplCanvas):
#     """Simple canvas with a sine plot."""
#
#     def compute_initial_figure(self):
#         t = arange(0.0, 3.0, 0.01)
#         s = sin(2*pi*t)
#         self.axes.plot(t, s)

# класс наладка ТГ
class TG_naladka():

    # "Скачки/Шаги"
    # @profile
    def grath_stepper(self, event):

        GSM_A_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
        GSM_B_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
        Zadanie_column = 'Значение развертки. Положение ГСМ'   # Значение развертки. Положение ГСМ
        time_column = 'миллисекунды'   # время

        fields = [GSM_A_column, GSM_B_column, Zadanie_column, time_column]

        opened_csv_files = fd.askopenfiles(title='Открыть CSV файл с ШАГАМИ', filetypes=[('CSV files', '*.csv'), ], initialdir='')

        # определение номера канала из названия файла
        name_ch = str(opened_csv_files)
        name_temp = name_ch = name_ch.split('/')
        if int(name_ch[len(name_ch) - 1][3]) == 1:
            name_ch = '1 канал'
        else:
            name_ch = '2 канал'

        # определение номера ТГ из названия файла
        name_TG = int(name_temp[len(name_temp) - 1][2])

        time_data = []

        for file_ in opened_csv_files:
            df = pd.read_csv(file_, header=0, delimiter=';', usecols=fields)

        # поиск количества строк
        num_rows = len(df.index)

        # создание пустого DataFrames
        df_1 = pd.DataFrame(None, index=range(num_rows), columns=['time'])
        # print(df_1.shape)

        summa = 0
        for z in range(num_rows):
            time_data.append(float('%.2f' % summa))
            summa = summa + 0.01

        # print(df.shape)
        # print(len(time_data))
        # print(time_data)
        # print(type(time_data[3]))

        # отрисовка окна для графиков
        point_f = 10

        self.point_view_2 = int(len(time_data) / point_f)

        print('точек отрисовки:', int(len(time_data)/point_f))

        fig = plt.figure(figsize=(6, 6))
        fig.canvas.set_window_title('Скачки/Шаги')
        ax = fig.add_subplot(211, facecolor='#FFFFCC')
        line, = ax.plot(time_data[1::point_f], df[GSM_A_column][1::point_f],
                        linewidth=1, color='b', label="ГСМ-А")  # ГСМ-А
        line1, = ax.plot(time_data[1::point_f], df[GSM_B_column][1::point_f],
                         linewidth=1, color='r', label="ГСМ-Б")  # ГСМ-Б
        line2, = ax.plot(time_data[1::point_f], df[Zadanie_column][1::point_f],
                         lw=1, color='black', label="Задание")  # Задание

        ax.set_xlabel('Время, c')
        ax.set_ylabel('ГСМ, мм')
        ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
        plt.title('ТГ-' + str(name_TG) +', ' + str(name_ch), fontsize='large')

        # отрисовка легенды
        ax.legend((line, line1, line2), ('ГСМ-А', 'ГСМ-Б', 'Задание'))

        # отрисовка 2 графика
        ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
        line02, = ax2.plot(time_data[1::point_f], df[GSM_A_column][1::point_f], lw=1, color='b', label="ГСМ-А")  # ГСМ-А
        line12, = ax2.plot(time_data[1::point_f], df[GSM_B_column][1::point_f], lw=1, color='r', label="ГСМ-Б")  # ГСМ-Б
        line22, = ax2.plot(time_data[1::point_f], df[Zadanie_column][1::point_f], lw=1, color='black', label="Задание")  # задание
        ax2.set_xlabel('Время, c')
        ax2.set_ylabel('ГСМ, мм')
        ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)

        # функция выделения_старая
        def onselect(xmin, xmax):
            print('*'*20)
            print('от курсора', xmin, xmax)
            indmin, indmax = np.searchsorted(time_data,
                                             (float(xmin), float(xmax)))  # получение минимального и максимального
            print('min_max', indmin, indmax)
            # indmax = min(len(time_data) - 1, indmax)
            print(indmin, indmax)

            thisx = time_data[indmin:indmax]  # новые данные для значений "время"
            thisx_new = []  # формирование нового массива значений "время"
            for zz in range(len(thisx)):
                thisx_new.append(zz * 0.01)
            thisy0 = np.array(df[GSM_A_column][indmin:indmax])  # новые данные для значений "ГСМ-А")
            thisy1 = np.array(df[GSM_B_column][indmin:indmax])  # новые данные для значений "ГСМ-Б"
            thisy2 = np.array(df[Zadanie_column][indmin:indmax])  # новые данные для значений "Задание"
            line02.set_data(thisx_new, thisy0)  # перерисовка графика "ГСМ-А"
            line12.set_data(thisx_new, thisy1)               # перерисовка графика "ГСМ-Б"
            line22.set_data(thisx_new, thisy2)               # перерисовка графика Задание
            print(thisx_new[0], thisx_new[-1])
            ax2.set_xlim(thisx_new[0], thisx_new[-1])  # перерисовка масштаба осей X
            ax2.set_ylim(thisy2.min() - 1, thisy2.max() + 1)  # перерисовка масштаба осей Y от Задания
            print('*' * 20)
            fig.canvas.draw()

        # set useblit True on gtkagg for enhanced performance
        span = SpanSelector(ax, onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))

        # функция - отображения графиков 1 чек-бокс
        def func(label):
            if label == 'ГСМ-А':
                line.set_visible(not line.get_visible())
            elif label == 'ГСМ-Б':
                line1.set_visible(not line1.get_visible())
            elif label == 'Задание':
                line2.set_visible(not line2.get_visible())
            plt.draw()

        # работа со списком чек-боксов отображающих графики 1
        rax = plt.axes([0.0, 0.5, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
        check = CheckButtons(rax, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
        check.on_clicked(func)

        # функция - отображения графиков 2 чек-бокс
        def func_2(label):
            if label == 'ГСМ-А':
                line02.set_visible(not line02.get_visible())
            elif label == 'ГСМ-Б':
                line12.set_visible(not line12.get_visible())
            elif label == 'Задание':
                line22.set_visible(not line22.get_visible())
            plt.draw()

        # работа со списком чек-боксов отображающих графики 2
        rax_2 = plt.axes([0.0, 0.01, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
        check_2 = CheckButtons(rax_2, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
        check_2.on_clicked(func_2)

        plt.show()

class Second(QDialog):
    def __init__(self, parent=None):
        super(Second, self).__init__(parent)
        # self.title_2 = '2'
        # self.setWindowTitle('fhgfh')

# класс для окна Шаги
class Step_Win(QDialog):
    def __init__(self, parent=None):
        super(Step_Win, self).__init__(parent)
        # self.title_2 = '2'
        # self.setWindowTitle('fhgfh')

class Main_Window(QDialog):

    global df, num_rr

    df = pd.DataFrame()

    num_rr = ''

    def __init__(self):
        super().__init__()
        self.title = 'Всякая ересь...'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 100
        self.initUI()

        self.dialog = Step_Win(self)
        self.dialog.setWindowTitle('Шаги')

        # # для доп_окна Смещение
        # layout_2_0 = QGridLayout()
        # layout_2_0.addWidget((self.combobox), 0, 1)
        # layout_2_0.addWidget(QLabel('Число усредняемых отсчетов:'), 0, 0)
        # layout_2_0.addWidget(QPushButton('Обновить'), 1, 0)
        # self.dialog.setLayout(layout_2_0)

        # для доп_окна Шагов
        layout_STEP = QGridLayout()
        self.combobox_dot = QComboBox()
        list_dot = ['10', '100', '1000']
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(2)
        layout_STEP.addWidget((self.combobox_dot), 0, 1)
        layout_STEP.addWidget(QLabel('Число для деления данных:'), 0, 0)
        # print(self.open_files.point_view)
        # num_point = str(self.number_point)
        # print('укук', num_point)
        layout_STEP.addWidget(QLabel('Число точек: ' + num_rr), 1, 0)
        layout_STEP.addWidget(QPushButton('Обновить'), 0, 2)
        self.dialog.setLayout(layout_STEP)

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.first_frame("Тук_тук")
        # self.createGridLayout_2("Смещение")

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        # windowLayout.addWidget(self.horizontalGroupBox_2)
        self.setLayout(windowLayout)

        self.show()

    def first_frame(self, name_frame):
        self.horizontalGroupBox = QGroupBox(name_frame)
        layout = QGridLayout()
        button_step = QPushButton('Шаги')
        layout.addWidget(button_step, 0, 0)
        # button_step.clicked.connect(TG_naladka.grath_stepper)
        button_step.clicked.connect(self.number_point)

        layout.addWidget(QPushButton('Скорости'), 0, 1)
        layout.addWidget(QPushButton('ОЗ одного канала'), 1, 0)
        layout.addWidget(QPushButton('ОЗ одной стороны'), 1, 1)
        self.horizontalGroupBox.setLayout(layout)

    # def createGridLayout_2(self, name_frame_2):
    #     self.horizontalGroupBox_2 = QGroupBox(name_frame_2)
    #
    #     layout_2 = QGridLayout()
    #
    #     layout_2.addWidget(QLabel('Число усредняемых отсчетов:'), 0, 0)
    #
    #     self.combobox = QComboBox()
    #     list_avarage = ['50', '100', '1000', '4000', '8000']
    #     self.combobox.addItems(list_avarage)
    #     self.combobox.setCurrentIndex(3)
    #
    #     layout_2.addWidget(self.combobox, 0, 1)
    #
    #     layout_2.addWidget(QPushButton('Смещение'), 1, 1)
    #
    #     self.horizontalGroupBox_2.setLayout(layout_2)

    # метод считывания данных из файла
    def open_files(self):
        # self.files = QFileDialog.getOpenFileNames(self, 'Открыть шаги')
        files = QFileDialog.getOpenFileName(self, 'Открыть шаги', '~', '*.csv')

        GSM_A_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
        GSM_B_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
        Zadanie_column = 'Значение развертки. Положение ГСМ'  # Значение развертки. Положение ГСМ
        Time_column = 'миллисекунды'  # время

        fields = [GSM_A_column, GSM_B_column, Zadanie_column, Time_column]

        # for file_ in my_csv:
        df = pd.read_csv(open(files[0], 'r'), header=0, delimiter=';', usecols=fields)

        print(df.info())

        # self.number_point()

        return len(df.index)

        # метод создание колонки Время

    def create_time(self):
        # поиск количества строк
        # global df
        num_rows = int(self.open_files())

        # num_rows = len(df.index)

        self.time_data = []
        summa = 0
        for z in range(num_rows):
            self.time_data.append(float('%.2f' % summa))
            summa = summa + 0.01

        print('длина времени:', len(self.time_data))

        return self.time_data, len(self.time_data)

    # метод для поиска числа точек отрисовки
    def number_point(self):

        time_data = self.create_time()

        print(time_data[1], type(time_data[1]))

        point_f = 10
        self.point_view = int(time_data[1] / point_f)

        global num_rr

        num_rr = self.point_view


        print('точек отрисовки:', self.point_view)

        print('точек отрисовки:', num_rr)

        # отрисовка дополнительноо окна ШАГИ
        self.dialog.show()

        return self.point_view

        # self.fig = Figure(figsize=(5, 4), dpi=100)
        #
        # # self.axes = fig.add_subplot(111)
        #
        # self.compute_initial_figure()
        #
        # FigureCanvas.__init__(self, fig)
        # self.setParent(None)
        #
        # FigureCanvas.setSizePolicy(self,
        #                            QSizePolicy.Expanding,
        #                            QSizePolicy.Expanding)
        # FigureCanvas.updateGeometry(self)

        return point_view

    def compute_initial_figure(self):
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main_Window()
    sys.exit(app.exec_())