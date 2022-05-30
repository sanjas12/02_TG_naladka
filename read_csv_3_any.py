import pandas as pd
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMainWindow
from grath import WindowGrath
import chardet
import gzip
import ctypes
import time
from itertools import islice


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.width = 640
        self.height = 400
        self.files = 0
        self.field_x = []
        self.field_y = []
        self.field_y2 = []
        self.time_c = 'time, c'
        self.setup_ui()

    def setup_ui(self):
        # self.setGeometry(10, 10, self.width, self.height)
        self.setWindowTitle(__file__)

        # колонка Выбирай параметр:
        inner_layout_1 = QVBoxLayout()
        inner_layout_1.addWidget(QLabel('Выбирай параметр:'))
        self.columns = QListWidget()
        inner_layout_1.addWidget(self.columns)
        button_open = QPushButton('Open')
        button_open.clicked.connect(self.open_files)
        inner_layout_1.addWidget(button_open)
        self.horizontalGroupBox = QGroupBox()
        self.horizontalGroupBox.setLayout(inner_layout_1)

        # колонка Ось Y
        vertical_lay_2 = QGridLayout()
        vertical_lay_2.addWidget(QLabel('Ось Y:'), 0, 0)
        self.axe_y = QListWidget()
        vertical_lay_2.addWidget(self.axe_y, 1, 0)
        button_add_to_y = QPushButton('Add to Y')
        button_add_to_y.clicked.connect(self.add_to_y, 2, 0)
        vertical_lay_2.addWidget(button_add_to_y)
        button_remove_y = QPushButton('Remove from Y')
        button_remove_y.clicked.connect(self.remove_y)
        vertical_lay_2.addWidget(button_remove_y, 3, 0)
        self.horizontalGroupBox_2 = QGroupBox()
        self.horizontalGroupBox_2.setLayout(vertical_lay_2)

        # колонка Ось X
        vertical_lay_3 = QGridLayout()
        vertical_lay_3.addWidget(QLabel('Ось X:'), 0, 0)
        self.axe_x = QListWidget()
        vertical_lay_3.addWidget(self.axe_x, 1, 0)
        button_add_to_x = QPushButton('Add to X')
        button_add_to_x.clicked.connect(self.add_to_x)
        vertical_lay_3.addWidget(button_add_to_x, 2, 0)
        button_remove_x = QPushButton('Remove from X')
        button_remove_x.clicked.connect(self.remove_x)
        vertical_lay_3.addWidget(button_remove_x, 3, 0)
        self.horizontalGroupBox_3 = QGroupBox()
        self.horizontalGroupBox_3.setLayout(vertical_lay_3)

        # колонка Ось Y2
        vertical_lay_4 = QGridLayout()
        vertical_lay_4.addWidget(QLabel('Ось Y2:'), 0, 0)
        self.axe_y2 = QListWidget()
        vertical_lay_4.addWidget(self.axe_y2, 1, 0)
        button_add_to_y2 = QPushButton('Add to Y2')
        button_add_to_y2.clicked.connect(self.add_to_y2)
        vertical_lay_4.addWidget(button_add_to_y2, 2, 0)
        button_remove_y2 = QPushButton('Remove from Y2')
        button_remove_y2.clicked.connect(self.remove_y2)
        vertical_lay_4.addWidget(button_remove_y2, 3, 0)
        self.horizontalGroupBox_4 = QGroupBox()
        self.horizontalGroupBox_4.setLayout(vertical_lay_4)

        self.first_huge_lay = QHBoxLayout()
        self.first_huge_lay.addWidget(self.horizontalGroupBox)
        self.first_huge_lay.addWidget(self.horizontalGroupBox_2)
        self.first_huge_lay.addWidget(self.horizontalGroupBox_4)
        self.first_huge_lay.addWidget(self.horizontalGroupBox_3)

        self.first_huge_GroupBox = QGroupBox()
        self.first_huge_GroupBox.setLayout(self.first_huge_lay)

        second_vertical_lay = QGridLayout()
        second_vertical_lay.addWidget(QLabel('Количество данных:'), 0, 0)
        self.number_point = QLabel()
        second_vertical_lay.addWidget(self.number_point, 0, 1)

        button_load_data = QPushButton('Загрузить данные')
        button_load_data.clicked.connect(self.load_data)
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
        button_grath.clicked.connect(self.plot_grath)
        second_vertical_lay.addWidget(button_grath, 2, 1)

        self.horizontal_2_GroupBox = QGroupBox()
        self.horizontal_2_GroupBox.setLayout(second_vertical_lay)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.first_huge_GroupBox)
        windowLayout.addWidget(self.horizontal_2_GroupBox)
        self.setLayout(windowLayout)

        self.show()

    def open_files(self):
        self.number_point.setText('0')
        
        # очищаем колонки
        self.columns.clear()
        self.axe_y.clear()
        self.axe_y2.clear()
        self.axe_x.clear()
        self.field_x = []
        self.field_y = []
        self.field_y2 = []

        self.files, _filter = QFileDialog.getOpenFileNames(self, 'Выбор данных: ', '',
                                                           "GZ Files (*.gz) ;; CSV Files (*.csv) ;; txt (*.txt)")
        try:
            if self.filename_extension():

                # Определение кодировки в csv файле
                with open(self.files[0], 'rb') as f:
                    raw_data = f.read(20000)
                    self.encoding = chardet.detect(raw_data)['encoding']
                print('encoding:', self.encoding)

                # и разделителя в csv файле
                with open(self.files[0], 'r', encoding=self.encoding) as f:
                    if f.readline(100).count(';'):
                        self.delimiter = ';'
                    else:
                        self.delimiter = '\t'
                print('delimiter:', repr(self.delimiter))

                # и decimal в csv файле
                with open(self.files[0], 'r', encoding=self.encoding) as f:
                    s = str(f.readlines()[2])
                    if s.count('.') > s.count(','):
                        self.decimal = '.'
                    else:
                        self.decimal = ','
                print('decimal:', self.decimal)

            else:
                # Определение кодировки в gz
                with gzip.open(self.files[0], 'rb') as f:
                    raw_data = f.read(20000)
                    self.encoding = chardet.detect(raw_data)['encoding']
                    print('encoding:', self.encoding)

                # и разделителя gz
                with gzip.open(self.files[0], 'r') as f:
                    if f.readline(100).decode(self.encoding).count(';'):
                        self.delimiter = ';'
                    else:
                        self.delimiter = '\t'
                    print('delimiter:', repr(self.delimiter))

                # и decimal qz
                with gzip.open(self.files[0], 'r') as f:
                    data = f.readlines()[2].decode(self.encoding)
                    if data.count('.') > data.count(','):
                        self.decimal = '.'
                    else:
                        self.decimal = ','
                print('decimal:', self.decimal)

        except IndexError as e:
            print('не выбраны данные')

        # Считывание названия всех колонок
        self.name_column = pd.read_csv(self.files[0], encoding=self.encoding, delimiter=self.delimiter, nrows=0)
        
        # удаляем лишние колонки
        self.name_column = self.name_column.loc[:, ~self.name_column.columns.str.contains('^Unnamed')]
        
        # заполняем колонку ось columns (Выбирай параметр)
        for i, _ in enumerate(self.name_column):
            self.columns.insertItem(i, _)

        # по умолчанию на ось columns (Выбирай параметр) добавляем 'time'
        # и тут же ее перемещяем на ось Х
        self.columns.addItem('time, c')
        self.columns.setCurrentRow(self.columns.count() - 1)
        self.axe_x.addItem(self.columns.takeItem(self.columns.currentRow()))
        self.columns.setCurrentRow(0)
        self.axe_x.setCurrentRow(0)

    # определение расширения
    def filename_extension(self):
        """
        true -> file is 'csv;
        false -> file is 'gz;
        :rtype: object
        """
        extension = self.files[0][-3:]
        if extension == 'csv':
            return True
        else:
            return False

    def add_to_x(self):
        self.axe_x.addItem(self.columns.takeItem(self.columns.currentRow()))
        self.axe_x.setCurrentRow(0)

    def remove_x(self):
        self.columns.addItem(self.axe_x.takeItem(self.axe_x.currentRow()))
        self.columns.setCurrentRow(0)

    def add_to_y(self):
        self.axe_y.addItem(self.columns.takeItem(self.columns.currentRow()))
        self.axe_y.setCurrentRow(0)

    def remove_y(self):
        self.columns.addItem(self.axe_y.takeItem(self.axe_y.currentRow()))
        self.columns.setCurrentRow(0)

    def add_to_y2(self):
        self.axe_y2.addItem(self.columns.takeItem(self.columns.currentRow()))
        self.axe_y2.setCurrentRow(0)

    def remove_y2(self):
        self.columns.addItem(self.axe_y2.takeItem(self.axe_y2.currentRow()))
        self.columns.setCurrentRow(0)

    def clear_y(self):
        self.axe_y.clear()
        self.axe_y2.clear()
        # self.axe_x.clear()

    def load_data(self):
        print('Time load data:', time.asctime())
        if self.axe_x.count() > 0:
            self.field_x = []
            for _ in range(self.axe_x.count()):
                self.field_x.append(self.axe_x.item(_).text())
            print('Ось Х:', self.field_x)
        else:
            print('Ось X:', 'нет данных')

        if self.axe_y.count() > 0:
            self.field_y = []
            for _ in range(self.axe_y.count()):
                self.field_y.append(self.axe_y.item(_).text())
            print('Ось Y:', self.field_y)
        else:
            print('Ось Y:', 'нет данных')

        if self.axe_y2.count() > 0:
            self.field_y2 = []
            for _ in range(self.axe_y2.count()):
                self.field_y2.append(self.axe_y2.item(_).text())
            print('Ось Y2:', self.field_y2)
        else:
            print('Ось Y2:', 'нет данных')

        # Основная загрузка данных (из множества CSV файлов)
        # if self.axe_x.count() > 0 and self.axe_y.count() > 0 and self.axe_y2.count() > 0:
        if True:

            self.df = pd.concat(pd.read_csv(file, header=0, encoding=self.encoding, delimiter=self.delimiter,
                                            usecols=self.field_y+self.field_y2, decimal=self.decimal) for file in self.files)

            self.number_point.setText(str(len(self.df.index)))

            # для токов и мощностей учет отрицательных значений
            name_column = ['Электрическая мощность двигателя ЭМП ОЗ ГСМ-А, десятки Вт',
                           'Электрическая мощность двигателя ЭМП ОЗ ГСМ-Б, десятки Вт',
                           'Ток момента двигателя ЭМП ОЗ ГСМ-А, десятки мА',
                           'Ток момента двигателя ЭМП ОЗ ГСМ-Б, десятки мА',
                           'Ток статора ЭМП ОЗ ГСМ-А, десятки мА',
                           'Ток статора ЭМП ОЗ ГСМ-Б, десятки мА']
            for _ in self.field_y:
                if _ in name_column:
                    self.df[_] = self.df[_].where(lambda x: x < 50000, lambda x: x - 65536)
                    print(_, ' - есть такой')
                else:
                    pass
                    # print(_, ' - нет такого')
            for _ in self.field_y2:
                if _ in name_column:
                    self.df[_] = self.df[_].where(lambda x: x < 50000, lambda x: x - 65536)
                    print(_, ' - есть такой')
                else:
                    pass
                    # print(_, ' - нет такого')

            # print(self.df.info())
        else:
            # print('No data.Ось Y')
            pass

        # добавляем колонку time если ее нет
        if self.time_c not in self.df:
            print('Time added.')
            time_data = []
            summa = 0
            for z in range(len(self.df.index)):
                time_data.append(float('%.2f' % summa))
                summa = summa + 0.01
            self.df[self.time_c] = time_data
        else:
            print("колонка time уже есть")

        print('-' * 30)

        # TODO
        # при загрузки некоторых файлов в конце добавляется неименнованный параметр

    def plot_grath(self):
        # print(self.combobox_dot.currentText())
        print(self.files[0])
        grath = WindowGrath(self.df, self.field_y, self.field_y2,
                            step=self.combobox_dot.currentText(),
                            filename=self.files[0])
        user32 = ctypes.windll.user32
        screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        grath.resize(screensize[0] - 10, screensize[1] - 150)
        grath.exec_()


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    try:
        sys.exit(app.exec())
    except:
        print("Пока")


if __name__ == '__main__':
    main()
