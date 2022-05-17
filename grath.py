import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QGridLayout, QLabel, QGroupBox, QVBoxLayout, QWidget, \
    QDialog, QPushButton, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import pandas as pd
import ctypes
from matplotlib.widgets import CheckButtons
import matplotlib.ticker as ticker


class WindowGrath(QDialog):

    def __init__(self, data: list, columns_y: list, columns_y2: list,
                 step: int = 1, filename: str = None) -> None:
        """
        data -> должен поддерживать ndim \n
        step -> должен быть int \n
        filename -> должен быть str \n
        """
        print(data.info())
        self.filename = filename
        self.data = data
        self.data_x = self.data['time, c']
        self.data_y = self.data.drop('time, c', axis=1)
        self.step = int(step)
        self.color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        self.color_inv = self.color[::-1]
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
        elif self.columns_y2:
            self.plot_y2()
        else:
            print('Не выбраны данные')

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
        ax1 = self.figure.add_subplot(111)
        ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)

        # self.number_point.setText(str(len(self.data.index) // self.step))

        for i, v in enumerate(self.columns_y):
            for _ in v:
                                # X                     Y
                ax1.plot(self.data_x[::self.step], self.data[_][::self.step], lw=2,
                         label=_)
                ax1.set_ylabel(self.columns_y[i])
                ax1.xaxis.set_major_locator(ticker.MaxNLocator(20))
                ax1.yaxis.set_major_locator(ticker.MaxNLocator(20))

        # color = 'tab:olive'

        for i, v in enumerate(self.columns_y2):
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            for i2, _ in enumerate(v):
                ax2.plot(self.data_x[::self.step], self.data[_][::self.step], ls='-.', lw=2, label=_,
                         color=self.color_inv[i2])
                ax2.set_ylabel(self.columns_y2[i], color='b')  # we already handled the x-label with ax1
                ax2.tick_params(axis='y', labelcolor='b')
                ax2.xaxis.set_major_locator(ticker.MaxNLocator(20))
                ax2.yaxis.set_major_locator(ticker.MaxNLocator(20))

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
        ax1 = self.figure.add_subplot(111, facecolor='#f8fadc')
        ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)

        for i, v in enumerate(self.columns_y):
            for i2, _ in enumerate(v):
                # X                     Y
                ax1.plot(self.data_x[::self.step], self.data[_][::self.step], lw=2, label=_,
                         color=self.color[i2])
                ax1.set_ylabel(self.columns_y[i])
                ax1.xaxis.set_major_locator(ticker.MaxNLocator(20))
                ax1.yaxis.set_major_locator(ticker.MaxNLocator(20))

        plt.draw()

        ax1.legend(loc=2)

        ax1.set_xlabel('time, c')

        self.canvas.draw()

    # Plot only y2
    def plot_y2(self):
        print('plot_y2')
        self.figure.clear()
        self.set_suptitle_grath()

        # первый вариант
        # fig = plt.figure(figsize=(20, 20))
        # ax=fig.add_subplot()

        # второй вариант
        ax1 = self.figure.add_subplot(111, facecolor='#f8fadc')
        ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)

        for i, v in enumerate(self.columns_y2):
            for i2, _ in enumerate(v):
                                # X                     Y
                ax1.plot(self.data_x[::self.step], self.data[_][::self.step], lw=2, ls='-.',
                         label=_, color=self.color_inv[i2])
                ax1.set_ylabel(self.columns_y2[i])

        plt.draw()

        ax1.legend(loc=2)

        ax1.set_xlabel('Время, c')

        self.canvas.draw()

    def set_suptitle_grath(self):
        if not self.filename:
            self.figure.suptitle(__file__)
        elif self.filename.find('ШУР') >= 0:
            index_tg = self.filename.find('ШУР')
            self.figure.suptitle(f'ТГ:{self.filename[index_tg + 3]}, '
                                 f'канал:{self.filename[index_tg + 4]}')
            # для проекта РК
        elif self.filename.find('ШСП') >= 0:
            index_tg = self.filename.find('ШСП')
            self.figure.suptitle(f'ШСП:{self.filename[index_tg + 3]}, '
                                 f'канал:{self.filename[index_tg + 4]}')
        else:
            index_tg = self.filename.find('ТГ')
            # print(index_tg, type(index_tg), self.filename[index_tg+2])
            self.figure.suptitle(f'ТГ:{self.filename[index_tg+2]}, '
                                 f'канал:{self.filename[index_tg+3]}')


def main():
    df = pd.DataFrame()
    number_point = 11
    df['ГСМ-А'] = [random.randint(300, 321) for _ in range(number_point)]
    df['ГСМ-Б'] = [random.randint(300, 321) for _ in range(number_point)]
    df['time, c'] = [i for i in range(number_point)]
    df['ОЗ-А'] = [random.random() for _ in range(number_point)]
    df['ОЗ-Б'] = [random.random() for _ in range(number_point)]

    y2 = ['ГСМ-А', 'ГСМ-Б']
    y1 = ['ОЗ-А', 'ОЗ-Б']

    app = QApplication(sys.argv)
    ex = WindowGrath(df, y1, y2, filename='E:/ТГ41-2021-06-25_134810_14099.csv.gz ')
    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    ex.resize(screensize[0]-10, screensize[1]-150)
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
