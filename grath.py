
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
                 step: int = 1) -> None:
        """
        data -> должен поддерживать ndim \n
        step -> должен быть int \n
        """
        self.data = data
        self.data_x = self.data['time, c']
        self.data_y = self.data.drop('time, c', axis=1)
        self.step = int(step)
        self.columns_y = []
        self.columns_y.append(columns_y)
        self.columns_y2 = []
        self.columns_y2.append(columns_y2)
        self.columns = self.data.columns

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

        self.label_list = []
        self.lines_list = []

        self.plot()

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

    def plot(self):
        # первый вариант
        # fig = plt.figure(figsize=(20, 20))
        # ax=fig.add_subplot()

        # второй вариант
        self.figure.clear()
        self.figure.suptitle(__file__)


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
            ax2.plot(self.data_x[::self.step], self.data[_][::self.step], ls='-.',
                     color=color, label=_)
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


def main():
    df = pd.DataFrame()
    number_point = 11
    df['ГСМ-А'] = [random.randint(300, 321) for _ in range(number_point)]
    df['ГСМ-Б'] = [random.randint(300, 321) for _ in range(number_point)]
    df['time, c'] = [i for i in range(number_point)]
    df['ОЗ'] = [random.random() for _ in range(number_point)]
    df['ОЗ-2'] = [random.random() for _ in range(number_point)]

    app = QApplication(sys.argv)
    ex = WindowGrath(df, ['ГСМ-А', 'ГСМ-Б'], ['ОЗ', 'ОЗ-2'])
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
