import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QGroupBox, QVBoxLayout, \
    QGridLayout, QMainWindow, QLineEdit
import grath
import random
import pandas as pd


class WindowMain(QWidget):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle('Всякая ересь...Qt')

        # для передачи числа между классами (вывод числа точек)
        self.value = QLineEdit()

        # первый Frame Главного окна
        self.horizontalGroupBox = QGroupBox('Тут тук')
        layout = QGridLayout()
        # button_step = QPushButton('Загрузить данные')
        # button_step.clicked.connect(self.open_new_window)
        # layout.addWidget(button_step, 0, 0)
        button_step_2 = QPushButton('Grath')
        button_step_2.clicked.connect(self.grath)
        layout.addWidget(button_step_2, 0, 1)

        self.horizontalGroupBox.setLayout(layout)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.setLayout(windowLayout)

    def grath(self):
        df = pd.DataFrame()
        df['time'] = [i for i in range(10)]
        df['gg'] = [random.random() for _ in range(10)]
        time = ['time']
        gg = ['gg']
        new_window = grath.WindowGrath(df, time, gg)
        new_window.exec_()


def main():
    app = QApplication(sys.argv)
    ex = WindowMain()
    ex.show()
    # try:
    sys.exit(app.exec_())
    # except:
    #     print("Каряво закрыли")


if __name__ == '__main__':
    main()
