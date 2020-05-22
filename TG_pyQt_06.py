import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
import read_csv
import window_step_2
from PyQt5.QtCore import pyqtSlot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import random


# класс для Главного окна
class Window_Main(QWidget):

    def __init__(self):
        super(Window_Main, self).__init__()
        self.setup_UI()

    def setup_UI(self):
        self.setWindowTitle('Всякая ересь...Qt')

        # для передачи чила между классами (вывод числа точек)
        self.value = QLineEdit()

        # первый Frame Главного окна
        self.horizontalGroupBox = QGroupBox('Тут тук')
        layout = QGridLayout()
        button_step = QPushButton('Шаги')
        button_step.clicked.connect(self.open_new_window)
        layout.addWidget(button_step, 0, 0)
        layout.addWidget(QPushButton('Скорости'), 0, 1)
        layout.addWidget(QPushButton('ОЗ одного канала'), 1, 0)
        layout.addWidget(QPushButton('ОЗ одной стороны'), 1, 1)

        self.horizontalGroupBox.setLayout(layout)

        # не надо отображать self.value = QLineEdit() он используется
        # только для предачи переменной между классами
        # layout.addWidget(self.value, 2, 0)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

    # метод открытия нового окна
    def read_file(self):
        print('start_open_new_window')

        self.df = read_csv.Window('Открыть файл с "шагами"')

        self.step_point = int(len(self.df.df.index)/10)

        self.value.setText(str(self.step_point))

        # print(df.df.info())

        print('end_open_new_window')

    def open_new_window(self):

        dialog = Window_Steps(self)
        dialog.exec_()

# класс для Дочернего окна (Шаги)
class Window_Steps(QDialog):

    def __init__(self, data):
        super(Window_Steps, self).__init__()
        self.setWindowTitle('Шаги')
        # self.setupPlot
        # print('1')

        # чтение данных из файла
        self.df = read_csv.Window('Открыть файл с "шагами"')

        # Just some button connected to `plot` method
        self.button = QPushButton('Обновить')
        self.button.clicked.connect(self.update_data)

        # combobox для изменения точек графика
        list_dot = ['10', '100', '1000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(0)


        self.step_point = int(len(self.df.df.index) / int(self.combobox_dot.currentText()))
        print('2')
        self.value = QLineEdit()  # для того чтобы писать сюда кол-во отображаемых точек
        # и от сюда вставлять в label_step
        self.value.setText(str(self.step_point))

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

        self.plot()

    def plot(self):
        ''' plot some random stuff '''
        # self.on_click()

        # random data
        data = [random.random() for i in range(10)]

        # print(self.df.info())

        # instead of ax.hold(False)
        self.figure.clear()

        # create an axis
        ax = self.figure.add_subplot(111)

        # discards the old graph
        # ax.hold(False) # deprecated, see above

        # plot data
        ax.plot(data, '*-')

        # refresh canvas
        self.canvas.draw()

    def update_data(self):
        print(self.combobox_dot.currentText())
        step_point = int(len(self.df.df.index) / int(self.combobox_dot.currentText()))
        print(step_point)
        self.label_step.setText(str(step_point))
        self.plot()


    # @pyqtSlot()
    # def on_click(self):
    #     print(self.combobox_dot.currentText())
    #     step_point = int(len(self.df.df.index) / int(self.combobox_dot.currentText()))
    #     # print(step_point)
    #     self.label_step.setText(step_point)
    #     # self.label_step.adjustSize()

def main():
    app = QApplication(sys.argv)
    ex = Window_Main()
    ex.show()
    # try:
    sys.exit(app.exec_())
    # except:
    #     print("Каряво закрыли")


if __name__ == '__main__':
    main()
