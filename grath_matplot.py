import sys
from typing import List
from PyQt5.QtWidgets import (
                            QApplication, 
                            QComboBox, 
                            QHBoxLayout,
                            QLabel,
                            QGroupBox,
                            QVBoxLayout,
                            QWidget,
                            QDialog,
                            QPushButton,
                            QMainWindow
                            )
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import pandas as pd
from matplotlib.widgets import CheckButtons
import matplotlib.ticker as ticker
from config.config import MYTIME

TICK_MARK_COUNT = 20

class WindowGrath(QMainWindow):
    def __init__(self, data: pd.DataFrame, base_axe: List = [], secondary_axe: List = [], axe_x: List = [],
                 step: int = 1, filename: str = None) -> None:
        """
        Class to plot grath
        """
        super().__init__()
        self.filename = filename
        self.data = data
        self.step = int(step)
        self.color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        self.color_inv = self.color[::-1]
        self.base_axe = base_axe
        self.secondary_axe = secondary_axe
        self.axe_x = axe_x
        # print(self.axe_x, self.base_axe, self.secondary_axe, sep='\n')
        self.columns = self.data.columns
        self.label_list = []
        self.lines_list = []

        self.ui()

    def ui(self):
        self.setWindowTitle('Графики')

        # первая линия gui
        list_dot = ['1', '10', '100', '1000', '10000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(1)
        self.number_point = QLabel()
        self.number_point.setText(str(len(self.data)))
        btn_update = QPushButton('Обновить графики')
        btn_update.clicked.connect(self.update)
        
        vbox_1 = QVBoxLayout()
        vbox_1.addStretch(10)
        # vbox_1.addWidget(self.combobox_dot)
        vbox_1.addWidget(QLabel('Число точек: '))
        vbox_1.addWidget(self.number_point)
        vbox_1.addWidget(btn_update)

        self.gb_1 = QGroupBox()
        self.gb_1.setLayout(vbox_1)

        # вторая линия gui
        self.figure = plt.figure(figsize=(10, 10))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        vbox_2 = QVBoxLayout()
        vbox_2.addWidget(self.canvas)
        vbox_2.addWidget(self.toolbar)
        
        self.gb_2 = QGroupBox()
        self.gb_2.setLayout(vbox_2)

        main = QHBoxLayout()
        # main.addWidget(self.gb_1)
        main.addWidget(self.gb_2)

        wid = QWidget()
        wid.setLayout(main)
        self.setCentralWidget(wid)

        self.plot()

    def update(self):
        self.step = self.combobox_dot.currentText()
        print(self.step)
        self.plot()
        self.canvas.draw()

    # checkbox для выбора графиков
    def set_visible(self, label):
        print(label)
        index = self.label_list.index(label)
        print(index)
        self.lines_list[index].set_visible(not self.lines_list[index].get_visible())
        plt.draw()

    def plot(self) -> None:
        # self.figure.clear()
        self.set_suptitle_grath()

        if self.base_axe:
            ax1 = self.figure.add_subplot()
            ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)
            for i, signal in enumerate(self.base_axe):
                                # X                     Y
                ax1.plot(self.axe_x[::self.step], self.data[signal][::self.step], lw=2, label=signal)
                print(signal)
            ax1.set_ylabel(',\n'.join(self.base_axe))
            ax1.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT))
            ax1.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT))
            ax1.legend(loc=2)
            ax1.set_xlabel(MYTIME)

        if self.secondary_axe:
            ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
            for i, signal in enumerate(self.secondary_axe):
                                  # X                     Y
                ax2.plot(self.axe_x[::self.step], self.data[signal][::self.step], ls='-.', lw=2, label=signal, color=self.color_inv[i])
                ax2.tick_params(axis='y', labelcolor='b')
                ax2.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT))
                ax2.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT))
            ax2.set_ylabel(f',\n'.join(self.secondary_axe), color='b')
            ax2.legend(loc=4)

        # refresh canvas
        self.canvas.draw()        

    def set_suptitle_grath(self):
        if not self.filename:
            self.figure.suptitle(__file__)
        elif self.filename.find('ШУР') >= 0:
            index_tg = self.filename.find('ШУР')
            self.figure.suptitle(f'ТГ:{self.filename[index_tg + 3]}, '
                                 f'канал:{self.filename[index_tg + 4]} '
                                 f'Кол-во данных: {str(len(self.data))}'
                                 )
            # для проекта РК
        elif self.filename.find('ШСП') >= 0:
            index_tg = self.filename.find('ШСП')
            self.figure.suptitle(f'ШСП:{self.filename[index_tg + 3]}, '
                                 f'канал:{self.filename[index_tg + 4]} '
                                 f'Кол-во данных: {str(len(self.data))}'
                                 )
        else:
            index_tg = self.filename.find('ТГ')
            self.figure.suptitle(f'ТГ:{self.filename[index_tg+2]}, '
                                 f'канал:{self.filename[index_tg+3]} '
                                 f'Кол-во данных: {str(len(self.data))}'
                                 )

def main():
    df = pd.DataFrame()
    number_point = 15
    first_signal = 'ГСМ-А. Очень длинный сигнал'
    df[first_signal] = [random.randint(300, 321) for _ in range(number_point)]
    df['ГСМ-Б'] = [random.randint(300, 321) for _ in range(number_point)]
    df['ОЗ-А'] = [random.random() for _ in range(number_point)]
    df['ОЗ-Б'] = [random.random() for _ in range(number_point)]
    df[MYTIME] = [i for i in range(number_point)]

    y1 = ['ОЗ-А', 'ОЗ-Б']
    y2 = [first_signal, 'ГСМ-Б']

    app = QApplication(sys.argv)
    ex = WindowGrath(df, base_axe=y1, secondary_axe=y2, axe_x=df[MYTIME], filename='E:/ТГ41-2021-06-25_134810_14099.csv.gz ')
    ex.show()

    try:
        sys.exit(app.exec())
    except:
        print('close: ', __file__)

if __name__ == '__main__':
    main()
