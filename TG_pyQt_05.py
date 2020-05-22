import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
import read_csv
import window_step

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

        self.show()

    # метод открытия нового окна
    def open_new_window(self):
        print('start_open_new_window')

        files = QFileDialog.getOpenFileName(self, 'Открыть файл с "шагами"', 'csv', '*.csv')

        df = read_csv.Read_files(files[0])

        view_point = int(len(df.df.index)/10)

        self.dialog = window_step.Window_Steps()
        # print('11')
        self.dialog.label_step.setText(str(view_point))
        # print('12')
        self.dialog.exec_()
        print('end_open_new_window')

def main():
    app = QApplication(sys.argv)
    ex = Window_Main()
    ex.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Каряво закрыли")

if __name__ == '__main__':
    main()