import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QGridLayout, QLabel, QGroupBox, QVBoxLayout, QWidget, \
    QDialog, QPushButton, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import pandas as pd
from matplotlib.widgets import CheckButtons
import numpy as np


class WindowGrath(QDialog):

    def __init__(self, data: list, columns_y: list, columns_y2: list,
                 step: int = 1, filename: str = None) -> None:
        """
        data -> должен поддерживать ndim \n
        step -> должен быть int \n
        filename -> должен быть str \n
        """
        self.filename = filename
        self.data = data
        self.data_x = self.data['time, c']
        self.data_y = self.data.drop('time, c', axis=1)
        self.step = int(step)
        if columns_y:
            self.columns_y = []
            self.columns_y.append(columns_y)
        else:
            self.columns_y = None
        if columns_y2:
            self.columns_y2 = []
            self.columns_y2.append(columns_y2)
        else:
            self.columns_y2 = None
        self.columns = self.data.columns
        self.label_list = []
        self.lines_list = []

        self.ui()

    def ui(self):
        super().__init__()
        self.setWindowTitle('Графики')

        self.horizontalGroupBox = QGroupBox()
        grid = QVBoxLayout()
        grid.addWidget(QLabel('Число отображаемых точек: '))

        self.number_point = QLabel()
        grid.addWidget(self.number_point)

        list_dot = ['10', '100', '1000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(0)
        grid.addWidget(self.combobox_dot)

        #TODO
        # button_grath = QPushButton('Обновить графики')
        # button_grath.clicked.connect(self.update)
        # grid.addWidget(button_grath)
        # grid.addStretch()
        # self.horizontalGroupBox.setLayout(grid)

        self.horizontalGroupBox_2 = QGroupBox()
        grid_2 = QVBoxLayout()
        self.figure = plt.figure(figsize=(10, 10))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        grid_2.addWidget(self.canvas)
        grid_2.addWidget(self.toolbar)
        self.horizontalGroupBox_2.setLayout(grid_2)

        windowLayout = QGridLayout()
        # windowLayout.addWidget(self.horizontalGroupBox, 0, 0)
        windowLayout.addWidget(self.horizontalGroupBox_2, 0, 1)
        self.setLayout(windowLayout)

        if self.columns_y and self.columns_y2:
            self.plot_y_y2()
        elif self.columns_y:
            self.plot_y()
        else:
            self.plot_y2()

    def update(self):
        self.step = self.combobox_dot.currentText()
        print(self.step)
        self.canvas.draw()

    # checkbox для выбора графиков
    def set_visible(self, label):
        print(label)
        index = self.label_list.index(label)
        print(index)
        self.lines_list[index].set_visible(not self.lines_list[index].get_visible())

        plt.draw()

    # Plot both y and y2
    def plot_y_y2(self):
        print('plot_y_y2')
        self.figure.clear()
        self.set_suptitle_grath()

        # первый вариант
        # fig = plt.figure(figsize=(20, 20))
        # ax=fig.add_subplot()

        # второй вариант
        ax1 = self.figure.add_subplot(111, facecolor='#FFFFCC')
        ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)

        # self.number_point.setText(str(len(self.data.index) // self.step))

        for _ in self.columns_y:
                                # X                     Y
            ax1.plot(self.data_x[::self.step], self.data[_][::self.step], lw=2, label=_)
            ax1.set_ylabel(_)  # we already handled the x-label with ax1

        color = 'tab:red'
        for _ in self.columns_y2:
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            ax2.set_ylabel(_, color='tab:red')  # we already handled the x-label with ax1
            ax2.plot(self.data_x[::self.step], self.data[_][::self.step], ls='-.', color=color,
                     label=_)
            ax2.tick_params(axis='y', labelcolor='tab:red')

        plt.draw()

        ax1.legend(loc=2)
        ax2.legend(loc=4)

        ax1.set_xlabel('time, c')

        # Чек-боксы графиков
        # положение чекбокса - x,y, х1,y1 - размер окна
        # rax = plt.axes([0.0, 0.1, 0.12, 0.13])
        # check = CheckButtons(rax, self.label_list, (True for _, s in enumerate(self.label_list)))
        # check.on_clicked(self.set_visible)

        # refresh canvas
        self.canvas.draw()

    # Plot only y
    def plot_y(self):
        print('plot_y')
        self.figure.clear()
        self.set_suptitle_grath()

        # первый вариант
        # fig = plt.figure(figsize=(20, 20))
        # ax=fig.add_subplot()

        # второй вариант
        ax1 = self.figure.add_subplot(111, facecolor='#FFFFCC')
        ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)

        for _ in self.columns_y:
                                # X                     Y
            ax1.plot(self.data_x[::self.step], self.data[_][::self.step], lw=2, label=_)
            ax1.set_ylabel(_)  # we already handled the x-label with ax1

        plt.draw()

        ax1.legend(loc=2)

        ax1.set_xlabel('time, c')

        self.canvas.draw()

    # Plot only y
    def plot_y2(self):
        print('plot_y2')
        self.figure.clear()
        self.set_suptitle_grath()

        # первый вариант
        # fig = plt.figure(figsize=(20, 20))
        # ax=fig.add_subplot()

        # второй вариант
        ax1 = self.figure.add_subplot(111, facecolor='#FFFFCC')
        ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)

        for _ in self.columns_y2:
                                # X                     Y
            ax1.plot(self.data_x[::self.step], self.data[_][::self.step], lw=2, label=_)
            ax1.set_ylabel(_)  # we already handled the x-label with ax1

        plt.draw()

        ax1.legend(loc=2)

        ax1.set_xlabel('time, c')

        self.canvas.draw()

    def set_suptitle_grath(self):
        print('set')
        if not self.filename:
            self.figure.suptitle(__file__)
        else:
            index_tg = self.filename.find('ТГ')
            print(index_tg, type(index_tg), self.filename[index_tg+2])
            self.figure.suptitle(f'ТГ:{self.filename[index_tg+2]}, '
                                 f'канал:{self.filename[index_tg+3]}')


def main():
    df = pd.DataFrame()
    number_point = 11
    df['ГСМ-А'] = [random.randint(300, 321) for _ in range(number_point)]
    df['ГСМ-Б'] = [random.randint(300, 321) for _ in range(number_point)]
    df['time, c'] = [i for i in range(number_point)]
    df['ОЗ'] = [random.random() for _ in range(number_point)]
    df['ОЗ-2'] = [random.random() for _ in range(number_point)]

    app = QApplication(sys.argv)
    ex = WindowGrath(df, None, ['ГСМ-А', 'ГСМ-Б'], filename='E:/ТГ41-2021-06-25_134810_14099.csv.gz ')
    ex.resize(1220, 680)
    ex.show()

    try:
        sys.exit(app.exec())
    except:
        print('close: ', __file__)


if __name__ == '__main__':
    # import matplotlib
    # print(matplotlib.matplotlib_fname())
    main()

# TODO
# Овновление графика добавить
# разница между plt.show() и plt.draw()
# ex.resize(1220, 680) - получать расшерения экрана
