import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit

import win_shift
import win_step


# класс для Главного окна
class Window_Main(QMainWindow):

    def __init__(self):
        super().__init__()
        # self.width = 640
        # self.height = 400
        self.setup_UI()

    def setup_UI(self):
        self.setWindowTitle('Всякая ересь...Qt')
        # self.setGeometry(10, 10, self.width, self.height)
        # # для передачи чила между классами (вывод числа точек)
        # self.value = QLineEdit()
        #
        # # первый Frame Главного окна
        # self.horizontalGroupBox = QGroupBox()
        layout = QGridLayout()
        button_step = QPushButton('Шаги')
        # button_step.clicked.connect(self.open_win_step)
        layout.addWidget(button_step, 0, 0)
        # layout.addWidget(QPushButton('Скорости'), 0, 1)
        # layout.addWidget(QPushButton('ОЗ одного канала'), 1, 0)
        # layout.addWidget(QPushButton('ОЗ одной стороны'), 1, 1)
        # button_shift = QPushButton('Смещение')
        # button_shift.clicked.connect(self.open_win_shift)
        # layout.addWidget(button_shift, 2, 1)
        #
        #
        # self.horizontalGroupBox.setLayout(layout)
        self.setLayout(layout)
        #
        # windowLayout = QVBoxLayout()
        # windowLayout.addWidget(self.horizontalGroupBox)
        # self.setLayout(windowLayout)

        self.show()

    def open_win_step(self):
        dialog = win_step.Window_Steps()
        dialog.exec_()

    def open_win_shift(self):
        dialog = win_shift.Window_Shift()
        dialog.exec_()
        pass


def main():
    app = QApplication(sys.argv)
    ex = Window_Main()
    # ex.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Каряво закрыли")


if __name__ == '__main__':
    main()
