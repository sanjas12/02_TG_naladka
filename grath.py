import sys
from PyQt5.QtWidgets import QApplication, QComboBox, QGridLayout, QLabel, QGroupBox, QVBoxLayout, QWidget, \
    QDialog, QPushButton, QMainWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import pandas as pd


class WindowGrath(QDialog):

    def __init__(self, data, data_x, data_y, step=1):
        """
        data -> должен поддерживать ndim \n
        data_x -> должен быть list \n
        data_y -> должен быть list
        """
        super(WindowGrath, self).__init__()
        self.setWindowTitle('Графики')
        # print(1)
        self.data = data
        self.data_x = data_x
        self.data_y = data_y
        self.step = int(step)
        # print('step', type(self.step), self.step)

        self.horizontalGroupBox = QGroupBox()
        grid = QVBoxLayout()
        # grid.addWidget(QLabel('Число для деления данных:'))
        grid.addWidget(QLabel('Число отображаемых точек: '))

        self.number_point = QLabel()
        grid.addWidget(self.number_point)

        list_dot = ['10', '100', '1000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(0)
        grid.addWidget(self.combobox_dot)

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

        self.plot()

    def update(self):
        self.step = self.combobox_dot.currentText()
        print(self.step)
        self.canvas.draw()

    def plot(self):

        # instead of ax.hold(False)
        self.figure.clear()

        # fig = plt.figure(figsize=(10, 10))

        # print('index', len(self.data.index))
        # print(len(self.data.index) // self.step)

        # create an axis
        ax = self.figure.add_subplot(111, facecolor='#FFFFCC')
        ax.grid(linestyle='--', linewidth=0.5, alpha=.85)

        self.number_point.setText(str(len(self.data.index)//self.step))

        # plt.title('Количество точек данных:' + str(len(self.data.index)//self.step), fontsize='large')

        # plot multiply graths
        for _ in range(len(self.data_y)):
            ax.plot(self.data[self.data_x[0]][1::self.step], self.data[self.data_y[_]][1::self.step],
                    lw=1, label=self.data_y[_])
            ax.legend()

        ax.set_xlabel('c')

        # refresh canvas
        self.canvas.draw()


def main():
    df = pd.DataFrame()
    df['time, c'] = [i for i in range(10)]
    df['ГСМ'] = [random.randint(1, 10) for _ in range(10)]
    df['ОЗ'] = [random.random() for _ in range(10)]
    time = ["time, c", ]
    gg = ['ГСМ', 'ОЗ']

    app = QApplication(sys.argv)
    ex = WindowGrath(df, time, gg)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()


# TODO
# Овновление графика добавить
