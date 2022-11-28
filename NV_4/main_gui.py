import pandas as pd
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMainWindow
import chardet
import gzip
import model_NV
from graphs.graph_gpk import graph_gpk
from graphs.graph_time import graph_time
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from data_base import data_base

class MainWindow(QWidget):

    def __init__(self, data):
        super().__init__()
        self.width = 640
        self.height = 400
        self.data_for_gui = data
        self.setup_ui()

    def setup_ui(self):
        # self.setGeometry(10, 10, self.width, self.height)
        self.setWindowTitle(__file__)

        # first row, first column (Imitator)
        imitator_layout = QGridLayout()
        imitator_layout.addWidget(QLabel('Давление в ГПК, МЕДИАНА'), 0, 0)
        imitator_layout.addWidget(QLabel("43.6"), 0, 1)
        self.horizontalGroupBox = QGroupBox("Imitator")
        
        self.horizontalGroupBox.setLayout(imitator_layout)

        # first row, second column (sarz)
        sarz_layout = QGridLayout()
        sarz_layout.addWidget(QLabel('Ось X:'), 0, 0)
        self.axe_x = QListWidget()
        sarz_layout.addWidget(self.axe_x, 1, 0)
        button_add_to_x = QPushButton('Add to X')
        
        sarz_layout.addWidget(button_add_to_x, 2, 0)
        button_remove_x = QPushButton('Remove from X')
       
        sarz_layout.addWidget(button_remove_x, 3, 0)
        self.horizontalGroupBox_2 = QGroupBox("Sarz")
        self.horizontalGroupBox_2.setLayout(sarz_layout)

        self.first_huge_lay = QHBoxLayout()
        self.first_huge_lay.addWidget(self.horizontalGroupBox)
        self.first_huge_lay.addWidget(self.horizontalGroupBox_2)

        self.first_huge_GroupBox = QGroupBox()
        self.first_huge_GroupBox.setLayout(self.first_huge_lay)

        # second row, first column
        second_vertical_lay = QGridLayout()
        second_vertical_lay.addWidget(QLabel('Количество данных:'), 0, 0)
        self.number_point = QLabel()
        second_vertical_lay.addWidget(self.number_point, 0, 1)

        button_load_data = QPushButton('Загрузить данные')
        
        second_vertical_lay.addWidget(button_load_data, 0, 2)

        second_vertical_lay.addWidget(QLabel('Количество отображаемых данных:'), 3, 0)
        self.number_point_grath = QLabel()
        second_vertical_lay.addWidget(self.number_point_grath, 3, 1)

        list_dot = ['1', '10', '100', '1000', '10000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(1)
        second_vertical_lay.addWidget(self.combobox_dot, 2, 0)

        button_grath = QPushButton('Построить графики')
        
        second_vertical_lay.addWidget(button_grath, 2, 1)

        self.horizontal_2_GroupBox = QGroupBox()
        self.horizontal_2_GroupBox.setLayout(second_vertical_lay)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.first_huge_GroupBox)
        windowLayout.addWidget(self.horizontal_2_GroupBox)
        self.setLayout(windowLayout)

        self.show()


def main():
    app = QApplication(sys.argv)
    data = "test"
    ex = MainWindow(data)
    ex.show()
    try:
        sys.exit(app.exec())
    except:
        print("Bye!")


if __name__ == '__main__':
    main()
