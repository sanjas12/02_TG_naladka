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

class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    print('start_myCANVAS')
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

    print('end_myCANVAS')

class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    print('start_myStatic')
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = sin(2*pi*t)
        self.axes.plot(t, s)

    print('end_myStatic')

# # класс наладка ТГ
# class TG_naladka():
#
#     # "Скачки/Шаги"
#     # @profile
#     def grath_stepper(self, event):
#
#         GSM_A_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
#         GSM_B_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
#         Zadanie_column = 'Значение развертки. Положение ГСМ'   # Значение развертки. Положение ГСМ
#         time_column = 'миллисекунды'   # время
#
#         fields = [GSM_A_column, GSM_B_column, Zadanie_column, time_column]
#
#         opened_csv_files = fd.askopenfiles(title='Открыть CSV файл с ШАГАМИ', filetypes=[('CSV files', '*.csv'), ], initialdir='')
#
#         # определение номера канала из названия файла
#         name_ch = str(opened_csv_files)
#         name_temp = name_ch = name_ch.split('/')
#         if int(name_ch[len(name_ch) - 1][3]) == 1:
#             name_ch = '1 канал'
#         else:
#             name_ch = '2 канал'
#
#         # определение номера ТГ из названия файла
#         name_TG = int(name_temp[len(name_temp) - 1][2])
#
#         time_data = []
#
#         for file_ in opened_csv_files:
#             df = pd.read_csv(file_, header=0, delimiter=';', usecols=fields)
#
#         # поиск количества строк
#         num_rows = len(df.index)
#
#         # создание пустого DataFrames
#         df_1 = pd.DataFrame(None, index=range(num_rows), columns=['time'])
#         # print(df_1.shape)
#
#         summa = 0
#         for z in range(num_rows):
#             time_data.append(float('%.2f' % summa))
#             summa = summa + 0.01
#
#         # print(df.shape)
#         # print(len(time_data))
#         # print(time_data)
#         # print(type(time_data[3]))
#
#         # отрисовка окна для графиков
#         point_f = 10
#
#         self.point_view_2 = int(len(time_data) / point_f)
#
#         print('точек отрисовки:', int(len(time_data)/point_f))
#
#         fig = plt.figure(figsize=(6, 6))
#         fig.canvas.set_window_title('Скачки/Шаги')
#         ax = fig.add_subplot(211, facecolor='#FFFFCC')
#         line, = ax.plot(time_data[1::point_f], df[GSM_A_column][1::point_f],
#                         linewidth=1, color='b', label="ГСМ-А")  # ГСМ-А
#         line1, = ax.plot(time_data[1::point_f], df[GSM_B_column][1::point_f],
#                          linewidth=1, color='r', label="ГСМ-Б")  # ГСМ-Б
#         line2, = ax.plot(time_data[1::point_f], df[Zadanie_column][1::point_f],
#                          lw=1, color='black', label="Задание")  # Задание
#
#         ax.set_xlabel('Время, c')
#         ax.set_ylabel('ГСМ, мм')
#         ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
#         plt.title('ТГ-' + str(name_TG) +', ' + str(name_ch), fontsize='large')
#
#         # отрисовка легенды
#         ax.legend((line, line1, line2), ('ГСМ-А', 'ГСМ-Б', 'Задание'))
#
#         # отрисовка 2 графика
#         ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
#         line02, = ax2.plot(time_data[1::point_f], df[GSM_A_column][1::point_f], lw=1, color='b', label="ГСМ-А")  # ГСМ-А
#         line12, = ax2.plot(time_data[1::point_f], df[GSM_B_column][1::point_f], lw=1, color='r', label="ГСМ-Б")  # ГСМ-Б
#         line22, = ax2.plot(time_data[1::point_f], df[Zadanie_column][1::point_f], lw=1, color='black', label="Задание")  # задание
#         ax2.set_xlabel('Время, c')
#         ax2.set_ylabel('ГСМ, мм')
#         ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)
#
#         # функция выделения_старая
#         def onselect(xmin, xmax):
#             print('*'*20)
#             print('от курсора', xmin, xmax)
#             indmin, indmax = np.searchsorted(time_data,
#                                              (float(xmin), float(xmax)))  # получение минимального и максимального
#             print('min_max', indmin, indmax)
#             # indmax = min(len(time_data) - 1, indmax)
#             print(indmin, indmax)
#
#             thisx = time_data[indmin:indmax]  # новые данные для значений "время"
#             thisx_new = []  # формирование нового массива значений "время"
#             for zz in range(len(thisx)):
#                 thisx_new.append(zz * 0.01)
#             thisy0 = np.array(df[GSM_A_column][indmin:indmax])  # новые данные для значений "ГСМ-А")
#             thisy1 = np.array(df[GSM_B_column][indmin:indmax])  # новые данные для значений "ГСМ-Б"
#             thisy2 = np.array(df[Zadanie_column][indmin:indmax])  # новые данные для значений "Задание"
#             line02.set_data(thisx_new, thisy0)  # перерисовка графика "ГСМ-А"
#             line12.set_data(thisx_new, thisy1)               # перерисовка графика "ГСМ-Б"
#             line22.set_data(thisx_new, thisy2)               # перерисовка графика Задание
#             print(thisx_new[0], thisx_new[-1])
#             ax2.set_xlim(thisx_new[0], thisx_new[-1])  # перерисовка масштаба осей X
#             ax2.set_ylim(thisy2.min() - 1, thisy2.max() + 1)  # перерисовка масштаба осей Y от Задания
#             print('*' * 20)
#             fig.canvas.draw()
#
#         # set useblit True on gtkagg for enhanced performance
#         span = SpanSelector(ax, onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))
#
#         # функция - отображения графиков 1 чек-бокс
#         def func(label):
#             if label == 'ГСМ-А':
#                 line.set_visible(not line.get_visible())
#             elif label == 'ГСМ-Б':
#                 line1.set_visible(not line1.get_visible())
#             elif label == 'Задание':
#                 line2.set_visible(not line2.get_visible())
#             plt.draw()
#
#         # работа со списком чек-боксов отображающих графики 1
#         rax = plt.axes([0.0, 0.5, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
#         check = CheckButtons(rax, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
#         check.on_clicked(func)
#
#         # функция - отображения графиков 2 чек-бокс
#         def func_2(label):
#             if label == 'ГСМ-А':
#                 line02.set_visible(not line02.get_visible())
#             elif label == 'ГСМ-Б':
#                 line12.set_visible(not line12.get_visible())
#             elif label == 'Задание':
#                 line22.set_visible(not line22.get_visible())
#             plt.draw()
#
#         # работа со списком чек-боксов отображающих графики 2
#         rax_2 = plt.axes([0.0, 0.01, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
#         check_2 = CheckButtons(rax_2, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
#         check_2.on_clicked(func_2)
#
#         plt.show()

# класс для Главного окна
class Main_Window(QDialog):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Всякая ересь...')
        # для передачи чиcла между классами
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

        # не надо отображать self.value = QLineEdit() он используется
        # только для предачи переменной между классами
        # layout.addWidget(self.value, 2, 0)

        self.horizontalGroupBox.setLayout(layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

        self.show()

    def first_frame(self, name_frame):
        self.horizontalGroupBox = QGroupBox(name_frame)
        layout = QGridLayout()
        button_step = QPushButton('Шаги')
        layout.addWidget(button_step, 0, 0)
        button_step.clicked.connect(self.number_point)

        layout.addWidget(QPushButton('Скорости'), 0, 1)
        layout.addWidget(QPushButton('ОЗ одного канала'), 1, 0)
        layout.addWidget(QPushButton('ОЗ одной стороны'), 1, 1)
        self.horizontalGroupBox.setLayout(layout)

    # метод считывания данных из файла
    def open_files(self):
        print('start_openFiles')
        # self.files = QFileDialog.getOpenFileNames(self, 'Открыть шаги')
        files = QFileDialog.getOpenFileName(self, 'Открыть шаги', '~', '*.csv')

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
    def openDialog(self):
        print('start_openDialog')
        dialog = Window_Step(self)
        dialog.label_step.setText(self.value.text())
        dialog.exec_()
        print('end_openDialog')

    # метод создание колонки Время
    def create_time(self):
        print('start_create_time')

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

    # метод для поиска числа точек отрисовки
    def number_point(self):
        print('start_number_point')

        time_data = self.create_time()

        # print('number_point', time_data[1], type(time_data[1]))

        point_f = 10
        point_view = int(time_data[1] / point_f)
        # self.value.text(self.point_view)

        self.value.setText(str(point_view))

        print('точек отрисовки self.point_view :', point_view)

        # отрисовка дополнительноо окна ШАГИ
        self.openDialog()

        print('end number_point')

    def compute_initial_figure(self):
        pass

# класс для окна Шаги
class Window_Step(QDialog):
    def __init__(self, parent=None):
        super(Window_Step, self).__init__(parent)
        layout_STEP = QGridLayout()
        layout_STEP.addWidget(QLabel('Число для деления данных:'), 0, 0)
        layout_STEP.addWidget(QPushButton('Обновить'), 0, 2)
        layout_STEP.addWidget(QLabel('Число отображаемых точек: '), 1, 0)
        self.label_step = QLabel(self)
        layout_STEP.addWidget(self.label_step, 1, 1)
        self.setLayout(layout_STEP)

        # self.main_widget = QWidget(self)
        # l = QVBoxLayout(self.main_widget)
        # sc = MyStaticMplCanvas(self.main_widget, width=5, height=4, dpi=100)
        # l.addWidget(sc)
        # self.main_widget.setFocus()
        # self.setCentralWidget(self.main_widget)

def main():
    app = QApplication(sys.argv)
    ex = Main_Window()
    ex.show()
    # sys.exit(app.exec_())
    try:
        sys.exit(app.exec_())
    except:
        print("Каряво закрыли")

if __name__ == '__main__':
    main()
