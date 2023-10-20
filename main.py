import pandas as pd
import sys
import chardet
import gzip
from typing import List
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMainWindow, QMessageBox
from grath import WindowGrath


class MainWindow(QMainWindow):
    cycle_plc = 0.01

    def __init__(self):
        super().__init__()
        self.width = 640
        self.height = 400
        self.files = None
        self.field_x = []
        self.field_y = []
        self.field_y2 = []
        self.field_name = ("Основная Ось", "Вспомогательная Ось", "Ось X (Времени)")
        self.time_c = 'time, c'
        self.df = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(__file__)

        # Список сигналов:
        self.qlist_signals = QListWidget()
        button_open_files = QPushButton('Open files')
        button_open_files.clicked.connect(self.open_files)
        
        signals_layout = QVBoxLayout()
        signals_layout.addWidget(self.qlist_signals)
        signals_layout.addWidget(button_open_files)
        
        self.gb_signals = QGroupBox("Список сигналов")
        self.gb_signals.setLayout(signals_layout)

        # Основная ось:
        self.qlist_base_axe = QListWidget()
        btn_base_axe_add = QPushButton('Add to Y')
        btn_base_axe_add.clicked.connect(lambda: self.add_to_qlist(self.qlist_base_axe))
        btn_base_axe_remove = QPushButton('Remove from Y')
        btn_base_axe_remove.clicked.connect(lambda: self.remove_qlist(self.qlist_base_axe))
        
        base_axe_layout = QVBoxLayout()
        base_axe_layout.addWidget(self.qlist_base_axe)
        base_axe_layout.addWidget(btn_base_axe_add)
        base_axe_layout.addWidget(btn_base_axe_remove)
        
        self.gb_base_axe = QGroupBox("Основная Ось")
        self.gb_base_axe.setLayout(base_axe_layout)

        # Вспомогательная ось:
        self.qlist_secondary_axe = QListWidget()
        btn_secondary_axe_add = QPushButton('Add to Y2')
        btn_secondary_axe_add.clicked.connect(lambda: self.add_to_qlist(self.qlist_secondary_axe))
        btn_secondary_axe_remove = QPushButton('Remove from Y2')
        btn_secondary_axe_remove.clicked.connect(lambda: self.remove_qlist(self.qlist_secondary_axe))
        
        secondary_axe_layout = QVBoxLayout()
        secondary_axe_layout.addWidget(self.qlist_secondary_axe)
        secondary_axe_layout.addWidget(btn_secondary_axe_add)
        secondary_axe_layout.addWidget(btn_secondary_axe_remove)
        
        self.gb_secondary_axe = QGroupBox("Вспомогательная Ось")
        self.gb_secondary_axe.setLayout(secondary_axe_layout)

        # Ось X
        self.qlist_x_axe = QListWidget()
        btn_x_axe_add = QPushButton('Add to X')
        btn_x_axe_add.clicked.connect(lambda: self.add_to_qlist(self.qlist_x_axe))
        btn_x_axe_remove = QPushButton('Remove from X')
        btn_x_axe_remove.clicked.connect(lambda: self.remove_qlist(self.qlist_x_axe))
        
        layout_x_axe = QVBoxLayout()
        layout_x_axe.addWidget(self.qlist_x_axe)
        layout_x_axe.addWidget(btn_x_axe_add)
        layout_x_axe.addWidget(btn_x_axe_remove)
        
        self.gb_x_axe = QGroupBox("Ось X")
        self.gb_x_axe.setLayout(layout_x_axe)
        
        # верхний слой
        self.first_huge_lay = QHBoxLayout()
        self.first_huge_lay.addWidget(self.gb_signals)
        self.first_huge_lay.addWidget(self.gb_base_axe)
        self.first_huge_lay.addWidget(self.gb_secondary_axe)
        self.first_huge_lay.addWidget(self.gb_x_axe)

        self.first_huge_GroupBox = QGroupBox()
        self.first_huge_GroupBox.setLayout(self.first_huge_lay)

        # нижний слой 
        self.number_raw_point = QLabel()
        self.number_plot_point = QLabel()
        list_dot = ['1', '10', '100', '1000', '10000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(1)
        button_grath = QPushButton('Построить графики')
        button_grath.clicked.connect(self.plot_grath)

        second_vertical_lay = QGridLayout()
        second_vertical_lay.addWidget(QLabel('Количество исходных данных:'), 0, 0)
        second_vertical_lay.addWidget(QLabel('Выборка, каждые:'), 1, 0)
        second_vertical_lay.addWidget(QLabel('Количество отображаемых данных:'), 2, 0)
        second_vertical_lay.addWidget(self.number_raw_point, 0, 1)
        second_vertical_lay.addWidget(self.combobox_dot, 1, 1)
        second_vertical_lay.addWidget(self.number_plot_point, 2, 1)
        second_vertical_lay.addWidget(QLabel(), 2, 3)
        second_vertical_lay.addWidget(QLabel(), 2, 4)
        second_vertical_lay.addWidget(button_grath, 2, 5)
        
        self.second_huge_GroupBox = QGroupBox()
        self.second_huge_GroupBox.setLayout(second_vertical_lay)
        
        # main_layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.first_huge_GroupBox)
        main_layout.addWidget(self.second_huge_GroupBox)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(main_layout)
        
    def open_files(self) -> None:
        self.files, _filter = QFileDialog.getOpenFileNames(self, 'Выбор данных: ', '',
                                                           "GZ Files (*.gz) ;; CSV Files (*.csv) ;; txt (*.txt)")

        if self.files: 
            self.clear_qlists()
            print(*self.files, sep='\n')
            self.parser(self.files[0])
            self.insert_signals_to_column()
    
    def insert_signals_to_column(self) -> None:
        self.qlist_signals.clear()
        self.clear_qlists()

        if self.files and self.encoding:
            # Считывание названия всех сингалов из одного файла
            df_name_signals = pd.read_csv(self.files[0], encoding=self.encoding, delimiter=self.delimiter, nrows=0)
            
            # удаляем лишние колонки
            df_name_signals = df_name_signals.loc[:, ~df_name_signals.columns.str.contains('^Unnamed')]
            
            # заполняем колонку ось columns (Выбирай параметр)
            for i, signal in enumerate(df_name_signals):
                self.qlist_signals.insertItem(i, signal)

            # по умолчанию на ось columns (Выбирай параметр) добавляем 'time'
            # и тут же ее перемещяем на ось Х
            self.qlist_signals.addItem('time, c')
            self.qlist_signals.setCurrentRow(self.qlist_signals.count() - 1)
            self.qlist_x_axe.addItem(self.qlist_signals.takeItem(self.qlist_signals.currentRow()))
            self.qlist_signals.setCurrentRow(0)
            self.qlist_x_axe.setCurrentRow(0)

    def parser(self, file: str) -> None:
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

    def add_to_qlist(self, qlist: QListWidget) -> None:
        add_signal = self.qlist_signals.takeItem(self.qlist_signals.currentRow())
        qlist.addItem(add_signal)
        qlist.setCurrentRow(0)

    def remove_qlist(self, qlist: QListWidget) -> None:
        remove_signal = qlist.takeItem(qlist.currentRow())
        self.qlist_signals.addItem(remove_signal)
        self.qlist_signals.setCurrentRow(0)                

    def clear_qlists(self) -> None:
        """
        Clear three QListWidgets (Основная Ось, Вспомогательная, Ось X)
        """
        self.qlist_base_axe.clear()
        self.qlist_secondary_axe.clear()
        self.qlist_x_axe.clear()

    def load_field_name(self, qlist_axe: QListWidget, field_name: str, num: int):
        if qlist_axe.count() > 0:
            field_name = []
            for _ in range(qlist_axe.count()):
                field_name.append(qlist_axe.item(_).text())
            print(self.field_name[num], field_name)
        else:
            print(f"Для {self.field_name[num]} не выбраны сигналы")
        return field_name
    
    # FIXME
    def load_data(self) -> None:
        self.df = None
        self.field_x, self.field_y, self.field_y2 = [], [], []
        self.field_y = self.load_field_name(self.qlist_base_axe, self.field_y, 0) 
        self.field_y2 = self.load_field_name(self.qlist_secondary_axe, self.field_y2, 1) 
        self.field_x = self.load_field_name(self.qlist_x_axe, self.field_x, 2) 
        
        # Основная загрузка данных (из множества CSV файлов)
        if self.files:
            self.df = pd.concat(pd.read_csv(file, header=0, encoding=self.encoding, delimiter=self.delimiter,
                                            usecols=self.field_y+self.field_y2, decimal=self.decimal) for file in self.files)

            self.number_raw_point.setText(str(len(self.df.index)))
            # для токов и мощностей учет отрицательных значений
            df_name_signals = ['Электрическая мощность двигателя ЭМП ОЗ ГСМ-А, десятки Вт',
                           'Электрическая мощность двигателя ЭМП ОЗ ГСМ-Б, десятки Вт',
                           'Ток момента двигателя ЭМП ОЗ ГСМ-А, десятки мА',
                           'Ток момента двигателя ЭМП ОЗ ГСМ-Б, десятки мА',
                           'Ток статора ЭМП ОЗ ГСМ-А, десятки мА',
                           'Ток статора ЭМП ОЗ ГСМ-Б, десятки мА']
            for _ in self.field_y:
                if _ in df_name_signals:
                    self.df[_] = self.df[_].where(lambda x: x < 50000, lambda x: x - 65536)
                    print(_, ' - есть такой')
                else:
                    pass
                    # print(_, ' - нет такого')
            for _ in self.field_y2:
                if _ in df_name_signals:
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
                print("Time exist in DataFrame")

        else:
            text = "Не открыты файлы архивов"
            self.dialog_box(text)

        print('-' * 30)

    def dialog_box(self, text: str) -> None:
        dlg = QMessageBox.information(self, 'My_info', text, QMessageBox.StandardButton.Ok)

    def plot_grath(self) -> None:
        self.load_data()
        if self.field_y or self.field_y2:
            self.number_plot_point.setText(str(int(len(self.df.index)/int(self.combobox_dot.currentText()))))
            self.grath = WindowGrath(self.df, self.field_y, self.field_y2,
                                step=self.combobox_dot.currentText(),
                                filename=self.files[0])
            self.grath.show()
        else:
            text = "Не выбраны сигналы для отображения"
            self.dialog_box(text)


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
