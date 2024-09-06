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
    QPushButton,
    QMainWindow
)
import pyqtgraph as pg
import pandas as pd
import random
from config.config import MYTIME, TICK_MARK_COUNT


class WindowGrath(QMainWindow):
    def __init__(self, data: pd.DataFrame, base_axe: List = [str], secondary_axe: List = [str],
                x_axe: str = MYTIME, step: int = 1, filename: str = 'E:/ТГ41-2021-06-25_134810_14099.csv.gz ') -> None:
        """
        Class to plot graph
        """
        super().__init__()
        self.filename = filename
        self.data = data
        self.step = int(step)
        self.base_axe = base_axe
        self.secondary_axe = secondary_axe
        self.x_axe = x_axe

        self.ui()

    def ui(self):
        self.setWindowTitle('Graphs')

        # first line of GUI
        list_dot = ['1', '10', '100', '1000', '10000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(1)
        self.number_point = QLabel()
        self.number_point.setText(str(len(self.data)))
        btn_update = QPushButton('Update Graphs')
        btn_update.clicked.connect(self.update_graph)
        
        vbox_1 = QVBoxLayout()
        vbox_1.addStretch(10)
        vbox_1.addWidget(QLabel('Number of points: '))
        vbox_1.addWidget(self.number_point)
        vbox_1.addWidget(btn_update)

        self.gb_1 = QGroupBox()
        self.gb_1.setLayout(vbox_1)

        # second line of GUI
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Y Axis')
        self.plot_widget.setLabel('bottom', 'X Axis')
        
        vbox_2 = QVBoxLayout()
        vbox_2.addWidget(self.plot_widget)
        
        self.gb_2 = QGroupBox()
        self.gb_2.setLayout(vbox_2)

        main = QHBoxLayout()
        main.addWidget(self.gb_2)

        wid = QWidget()
        wid.setLayout(main)
        self.setCentralWidget(wid)

        self.plot()

    def update_graph(self):
        self.step = int(self.combobox_dot.currentText())
        print(self.step)
        self.plot()

    def plot(self) -> None:
        self.plot_widget.clear()  # Clear previous plots

        if self.base_axe:
            for signal in self.base_axe:
                self.plot_widget.plot(
                    self.data[self.x_axe][::self.step], 
                    self.data[signal][::self.step], 
                    pen='b', 
                    name=signal
                )

        if self.secondary_axe:
            for i, signal in enumerate(self.secondary_axe):
                self.plot_widget.plot(
                    self.data[self.x_axe][::self.step], 
                    self.data[signal][::self.step], 
                    pen={'color': 'r', 'width': 2}, 
                    name=signal
                )

        # Add legend
        self.plot_widget.addLegend()

        # Set title
        self.set_suptitle_grath()

    def set_suptitle_grath(self):
        title = ''
        if not self.filename:
            title = __file__
        elif 'ШУР' in self.filename:
            index_tg = self.filename.rfind('ШУР')
            title = f'ТГ:{self.filename[index_tg + 3]}, Канал:{self.filename[index_tg + 4]}, Кол-во данных: {str(len(self.data))}'
        elif 'ШСП' in self.filename:
            index_tg = self.filename.rfind('ШСП')
            title = f'ШСП:{self.filename[index_tg + 3]}, Канал:{self.filename[index_tg + 4]}, Кол-во данных: {str(len(self.data))}'
        else:
            index_tg = self.filename.rfind('ТГ')
            title = f'ТГ:{self.filename[index_tg + 2]}, Канал:{self.filename[index_tg + 3]}, Кол-во данных: {str(len(self.data))}'
        
        self.setWindowTitle(title)

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
    ex = WindowGrath(df, base_axe=y1, secondary_axe=y2, x_axe=MYTIME, filename='E:/ТГ41-2021-06-25_134810_14099.csv.gz ')
    ex.show()

    try:
        sys.exit(app.exec())
    except:
        print('close: ', __file__)

if __name__ == '__main__':
    main()
