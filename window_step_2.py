from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import sys
import TG_pyQt_06

from PyQt5.QtCore import pyqtSlot

# класс для Second окна (Шаги)
class Window_Steps(QDialog):

    def __init__(self, parent=None):
        super(Window_Steps, self).__init__(parent)
        self.setWindowTitle('Шаги')
        # self.setupPlot

        # Just some button connected to `plot` method
        self.button = QPushButton('Обновить')
        self.button.clicked.connect(self.on_click)

        # combobox для изменения точек графика
        list_dot = ['10', '100', '1000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(0)

        self.label_step = QLabel(self)

        # self.text = 1000
        # self.label_step.setText(str(self.text))

        grid = QGridLayout()
        grid.addWidget(QLabel('Число отображаемых точек: '), 1, 0)
        grid.addWidget(QLabel('Число для деления данных:'), 0, 0)
        grid.addWidget(self.combobox_dot, 0, 1)
        grid.addWidget(self.label_step, 1, 1)
        grid.addWidget(self.button, 2, 0)

        self.setLayout(grid)

        # self.show()

    def calc_label(self):
        n_2 = self.text/int(self.combobox_dot.currentText())
        return int(n_2)

    def update_label(self, index):
        # self.text_2 = self.calc_label()
        print(index)
        print()
        print(self.combobox_dot.currentText())
        pass

    @pyqtSlot()
    def on_click(self):
        print(self.combobox_dot.currentText())
        self.label_step.setText('some text')
        self.label_step.adjustSize()


def main():
    app = QApplication(sys.argv)
    ex = Window_Steps()
    ex.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Каряво закрыли")


if __name__ == '__main__':
        main()