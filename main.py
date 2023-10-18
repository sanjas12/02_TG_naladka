import pandas as pd
import sys
import chardet
import gzip
import ctypes
from typing import List
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMainWindow
from grath import WindowGrath


class MainWindow(QWidget):
    cycle_plc = 0.01

    def __init__(self):
        super().__init__()
        self.width = 640
        self.height = 400
        self.files = None
        self.field_x = []
        self.field_y = []
        self.field_y2 = []
        self.field_name = ("Ось Y", "Ось Y2", "Ось X")
        self.time_c = 'time, c'
        self.setup_ui()
        self.df = None

    def setup_ui(self):
        # self.setGeometry(10, 10, self.width, self.height)
        self.setWindowTitle(__file__)

        # Список сигналов:
        inner_layout_1 = QVBoxLayout()
        inner_layout_1.addWidget(QLabel('Список сигналов:'))
        self.columns = QListWidget()
        inner_layout_1.addWidget(self.columns)
        button_open_files = QPushButton('Open files')
        button_open_files.clicked.connect(self.open_files)
        inner_layout_1.addWidget(button_open_files)
        self.horizontalGroupBox = QGroupBox()
        self.horizontalGroupBox.setLayout(inner_layout_1)

        # Основная ось:
        vertical_lay_2 = QGridLayout()
        vertical_lay_2.addWidget(QLabel('Основная ось:'), 0, 0)
        self.axe_y = QListWidget()
        vertical_lay_2.addWidget(self.axe_y, 1, 0)
        button_add_to_y = QPushButton('Add to Y')
        button_add_to_y.clicked.connect(self.add_to_y)
        vertical_lay_2.addWidget(button_add_to_y)
        button_remove_y = QPushButton('Remove from Y')
        button_remove_y.clicked.connect(self.remove_y)
        vertical_lay_2.addWidget(button_remove_y, 3, 0)
        self.horizontalGroupBox_2 = QGroupBox()
        self.horizontalGroupBox_2.setLayout(vertical_lay_2)

        # Вспомогательная ось:
        vertical_lay_4 = QGridLayout()
        vertical_lay_4.addWidget(QLabel('Вспомогательная ось:'), 0, 0)
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

        # Ось X
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

    def open_files(self)-> List[str]:
        self.files, _filter = QFileDialog.getOpenFileNames(self, 'Выбор данных: ', '',
                                                           "GZ Files (*.gz) ;; CSV Files (*.csv) ;; txt (*.txt)")

        if self.files: 
            print(*self.files, sep='\n')
            self.parser(self.files[0])
            self.insert_signals_to_column(self.files[0])
    
    def insert_signals_to_column(self, file):
        # очищаем колонки
        self.columns.clear()
        self.axe_y.clear()
        self.axe_y2.clear()
        self.axe_x.clear()

        if self.files and self.encoding:
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

    def parser(self, file: str)  -> None:
        """ 
        Detect encoding, delimiter, decimal in opened files
        """
        if file.endswith('.gz'): # определение типа файла
            with gzip.open(file, 'rb') as f:
                raw_data = f.read(20000)
                second_row = f.readlines()[2] # вторая строка
        else:
            with open(file, 'rb') as f:
                raw_data = f.read(20000)
                second_row = f.readlines()[2]

        # Кодировка
        self.chardet= chardet.detect(raw_data)
        self.encoding = chardet.detect(raw_data).get('encoding')

        if self.encoding:
            # Разделитель
            str_data = raw_data[:200].decode(self.encoding)
            if str_data.count(';'):
                self.delimiter = ';'
            else:
                self.delimiter = '\t'

            # Decimal 
            data = second_row.decode(self.encoding) 
            if data.count('.') > data.count(','):
                self.decimal = '.'
            else:
                self.decimal = ','

            print(f"encoding: {self.encoding} delimiter: {repr(self.delimiter)} decimal: {self.decimal}")
        else:
            print(f"Не удалось определить кодировку, попробуйте разархивировать файл")

    def add_to_x(self):
        self.axe_x.addItem(self.columns.takeItem(self.columns.currentRow()))
        self.axe_x.setCurrentRow(0)

    def remove_x(self):
        self.columns.addItem(self.axe_x.takeItem(self.axe_x.currentRow()))
        self.columns.setCurrentRow(0)
        self.field_x = []

    def add_to_y(self):
        self.axe_y.addItem(self.columns.takeItem(self.columns.currentRow()))
        self.axe_y.setCurrentRow(0)

    def remove_y(self):
        self.columns.addItem(self.axe_y.takeItem(self.axe_y.currentRow()))
        self.columns.setCurrentRow(0)                
        self.field_y = []

    def add_to_y2(self):
        self.axe_y2.addItem(self.columns.takeItem(self.columns.currentRow()))
        self.axe_y2.setCurrentRow(0)

    def remove_y2(self):
        self.columns.addItem(self.axe_y2.takeItem(self.axe_y2.currentRow()))
        self.columns.setCurrentRow(0)
        self.field_y2 = []

    def clear_y(self):
        self.axe_y.clear()
        self.axe_y2.clear()
        # self.axe_x.clear()

    def load_field_name(self, axe, field_name, num):
        if axe.count() > 0:
            field_name = []
            for _ in range(axe.count()):
                field_name.append(axe.item(_).text())
            print(self.field_name[num], field_name)
        else:
            print(f"Для {self.field_name[num]} не выбраны сигналы")
        return field_name

    def load_data(self):
        self.df = None
        self.field_y = self.load_field_name(self.axe_y, self.field_y, 0) 
        self.field_y2 = self.load_field_name(self.axe_y2, self.field_y2, 1) 
        self.field_x = self.load_field_name(self.axe_x, self.field_x, 2) 
        
        # Основная загрузка данных (из множества CSV файлов)
        if self.field_y or self.field_y2:
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

            # добавляем колонку time если ее нет
            if self.time_c not in self.df:
                self.df[self.time_c] = [_ * __class__.cycle_plc for _ in range(len(self.df.index))]
                print('Time added.')
            else:
                print("Time exist")

        else:
            print('No data for grath')

        print('-' * 30)

    def plot_grath(self):
        self.load_data()
        if self.files and (self.field_y or self.field_y2):
            self.grath = WindowGrath(self.df, self.field_y, self.field_y2,
                                step=self.combobox_dot.currentText(),
                                filename=self.files[0])
            self.user32 = ctypes.windll.user32
            self.screensize = self.user32.GetSystemMetrics(0), self.user32.GetSystemMetrics(1)
            self.grath.resize(self.screensize[0] - 10, self.screensize[1] - 150)
            self.grath.show()


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
