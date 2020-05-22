import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
import read_csv

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

# класс для Second окна (Шаги)
class Window_Steps(QDialog):

    def __init__(self, data):
        super(Window_Steps, self).__init__()
        self.setWindowTitle('Шаги')

        self.read_file()

        self.button = QPushButton('Обновить')
        self.button.clicked.connect(self.update_win)


        list_dot = ['10', '100', '1000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(0)
        print('4')

        self.value = QLineEdit()  # для того чтобы писать сюда кол-во отображаемых точек
        # # и от сюда вставлять в label_step
        print(str(len(self.df.df.index) / int(self.combobox_dot.currentText())))
        # self.value.setText(str(self.df.df.index/int(self.combobox_dot.currentText())))
        print('5')
        self.label_step = QLabel(self)
        self.label_step.setText(self.value.text())

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)


        self.horizontalGroupBox = QGroupBox()
        grid = QGridLayout()
        grid.addWidget(QLabel('Число для деления данных:'), 0, 0)
        grid.addWidget(QLabel('Число отображаемых точек: '), 1, 0)
        grid.addWidget(self.combobox_dot, 0, 1)
        grid.addWidget(self.label_step, 1, 1)
        grid.addWidget(self.button, 2, 0)
        self.horizontalGroupBox.setLayout(grid)

        self.horizontalGroupBox_2 = QGroupBox()
        grid_2 = QVBoxLayout()
        grid_2.addWidget(self.canvas)
        grid_2.addWidget(self.toolbar)
        self.horizontalGroupBox_2.setLayout(grid_2)

        windowLayout = QHBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.horizontalGroupBox_2)
        self.setLayout(windowLayout)

        # self.plot()

    def plot(self):
        ''' plot some random stuff '''
        # self.on_click()


        # instead of ax.hold(False)
        self.figure.clear()


        fig = plt.figure(figsize=(6, 6))
        # create an axis
        ax = self.figure.add_subplot(111, facecolor='#FFFFCC')
        ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
        plt.title('ТГ', fontsize='large')
        # discards the old graph
        # ax.hold(False) # deprecated, see above

        step_point = int(self.combobox_dot.currentText())

        # print(self.df.df[self.df.GSM_A_column][1::self.step_point])

        # plot data
        ax.plot(self.df.df[self.df.time][1::step_point],
                self.df.df[self.df.GSM_A_column][1::step_point], lw=1, color='b', label="ГСМ-А")
        ax.plot(self.df.df[self.df.time][1::step_point],
                self.df.df[self.df.GSM_B_column][1::step_point], lw=1, color='r', label="ГСМ-Б")
        ax.plot(self.df.df[self.df.time][1::step_point],
                self.df.df[self.df.zadanie_column][1::step_point], lw=1, color='black', label="Задание")
        ax.set_xlabel('Время, c')
        ax.set_ylabel('ГСМ, мм')

        # refresh canvas
        self.canvas.draw()

    def update_win(self):
        print(self.combobox_dot.currentText())
        self.step_point = int(len(self.df.df.index) / int(self.combobox_dot.currentText()))
        print(self.step_point)
        self.label_step.setText(str(self.step_point))
        self.plot()
        # print(self.df.df[self.df.time], self.df.df[self.df.GSM_A_column])

    def read_file(self):
        print('start_read_file')

        self.df = read_csv.Window('Открыть файл с "шагами"')

        print('end_read_file')
    # @pyqtSlot()
    # def on_click(self):
    #     print(self.combobox_dot.currentText())
    #     step_point = int(len(self.df.df.index) / int(self.combobox_dot.currentText()))
    #     # print(step_point)
    #     self.label_step.setText(step_point)
    #     # self.label_step.adjustSize()
