import pandas as pd
import sys
import chardet
import gzip
from typing import List, Dict, Tuple
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMainWindow, \
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from grath import WindowGrath
from config.config import MYTIME

class MainWindow(QMainWindow):
    cycle_plc = 0.01

    def __init__(self):
        super().__init__()
        self.width = 640
        self.height = 400
        self.files, self.extension = None, None
        self.field_x, self.field_y,  self.field_y2 = [], [], []
        self.dict_x_axe, self.dict_base_axe, self.dict_secondary_axe = {}, {}, {}
        self.field_name = ("Основная Ось", "Вспомогательная Ось", "Ось X (Времени)")
        self.time_c = MYTIME
        self.df = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle(__file__)

        # Список сигналов:
        self.tb_signals = QTableWidget()
        self.tb_signals.setColumnCount(1)
        self.tb_signals.horizontalHeader().hide()
        self.tb_signals.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tb_signals.horizontalHeader().setStretchLastSection(True)

        btn_open_files = QPushButton('Open files')
        btn_open_files.clicked.connect(self.insert_all_signals)
        
        signals_layout = QVBoxLayout()
        signals_layout.addWidget(self.tb_signals)
        signals_layout.addWidget(btn_open_files)
        
        self.gb_signals = QGroupBox("Список сигналов")
        self.gb_signals.setLayout(signals_layout)

        # Основная ось:
        self.qlist_base_axe = QListWidget()
        btn_base_axe_add = QPushButton('Add to Y')
        btn_base_axe_add.clicked.connect(lambda: self.add_signal(self.qlist_base_axe, self.dict_base_axe))
        btn_base_axe_remove = QPushButton('Remove from Y')
        btn_base_axe_remove.clicked.connect(lambda: self.remove_signal(self.qlist_base_axe, self.dict_base_axe))
        
        base_axe_layout = QVBoxLayout()
        base_axe_layout.addWidget(self.qlist_base_axe)
        base_axe_layout.addWidget(btn_base_axe_add)
        base_axe_layout.addWidget(btn_base_axe_remove)
        
        self.gb_base_axe = QGroupBox("Основная Ось")
        self.gb_base_axe.setLayout(base_axe_layout)

        # Вспомогательная ось:
        self.qlist_secondary_axe = QListWidget()
        btn_secondary_axe_add = QPushButton('Add to Y2')
        btn_secondary_axe_add.clicked.connect(lambda: self.add_signal(self.qlist_secondary_axe, self.dict_secondary_axe))
        btn_secondary_axe_remove = QPushButton('Remove from Y2')
        btn_secondary_axe_remove.clicked.connect(lambda: self.remove_signal(self.qlist_secondary_axe, self.dict_secondary_axe))
        
        secondary_axe_layout = QVBoxLayout()
        secondary_axe_layout.addWidget(self.qlist_secondary_axe)
        secondary_axe_layout.addWidget(btn_secondary_axe_add)
        secondary_axe_layout.addWidget(btn_secondary_axe_remove)
        
        self.gb_secondary_axe = QGroupBox("Вспомогательная Ось")
        self.gb_secondary_axe.setLayout(secondary_axe_layout)

        # Ось X
        self.qlist_x_axe = QListWidget()
        btn_x_axe_add = QPushButton('Add to X')
        btn_x_axe_add.clicked.connect(lambda: self.add_signal(self.qlist_x_axe, self.dict_x_axe))
        btn_x_axe_remove = QPushButton('Remove from X')
        btn_x_axe_remove.clicked.connect(lambda: self.remove_signal(self.qlist_x_axe, self.dict_x_axe))
        
        layout_x_axe = QVBoxLayout()
        layout_x_axe.addWidget(self.qlist_x_axe)
        layout_x_axe.addWidget(btn_x_axe_add)
        layout_x_axe.addWidget(btn_x_axe_remove)
        
        self.gb_x_axe = QGroupBox("Ось X")
        self.gb_x_axe.setLayout(layout_x_axe)
        
        # первый слой
        self.first_huge_lay = QHBoxLayout()
        self.first_huge_lay.addWidget(self.gb_signals)
        self.first_huge_lay.addWidget(self.gb_base_axe)
        self.first_huge_lay.addWidget(self.gb_secondary_axe)
        self.first_huge_lay.addWidget(self.gb_x_axe)

        self.first_huge_GroupBox = QGroupBox()
        self.first_huge_GroupBox.setLayout(self.first_huge_lay)

        # второй слой 
        self.ql_info = QLabel()

        self.second_lay = QHBoxLayout()
        self.second_lay.addWidget(self.ql_info)

        self.second_huge_GroupBox = QGroupBox()
        self.second_huge_GroupBox.setLayout(self.second_lay)

        # третий слой 
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
        
        self.third_huge_GroupBox = QGroupBox()
        self.third_huge_GroupBox.setLayout(second_vertical_lay)
        
        # main_layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.first_huge_GroupBox)
        main_layout.addWidget(self.second_huge_GroupBox)
        main_layout.addWidget(self.third_huge_GroupBox)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(main_layout)
        
    def open_files(self) -> None:
        """
        Return List opened files and his extension
        """
        FILE_FILTERS = [
            "GZ Files (*.gz)",
            "CSV Files (*.csv)",
            "txt (*.txt)"
        ]
        self.files, self.extension = QFileDialog.getOpenFileNames(self, 'Выбор данных: ', initialFilter=FILE_FILTERS[0], 
                                                                    filter=";;".join(FILE_FILTERS))
        
    def read_all_signals(self) -> None:

        if self.files and self.encoding:
            # Считывание названия всех сигналов из первого файла
            df_all_signals = pd.read_csv(self.files[0], encoding=self.encoding, delimiter=self.delimiter, nrows=0)
            
            # удаляем лишние колонки
            df_all_signals = df_all_signals.loc[:, ~df_all_signals.columns.str.contains('^Unnamed')]
            self.dict_all_signals = {signal:i for i, signal in enumerate(df_all_signals)}
           
            # добавление моего времени
            self.dict_all_signals[self.time_c] = len(self.dict_all_signals)

            # и тут же перемещаем ее на "Ось Х"
            self.dict_x_axe.setdefault(*self.dict_all_signals.popitem())
            self.qlist_x_axe.addItem(self.time_c)
            
    def insert_all_signals(self) -> None:
        """
        Clear all old signals and insert new signals to QTable(Список сигналов)
        """
        self.tb_signals.setRowCount(0)
        if not self.files:
            self.open_files()
        
        if self.files: 
            print(*self.files, sep='\n')
            self.clear_signals()
            self.parser()
            self.read_all_signals()
        
            for signal, i in sorted(self.dict_all_signals.items(), key=lambda item: item[1]):
                row_position = self.tb_signals.rowCount()
                self.tb_signals.insertRow(row_position)
                self.tb_signals.setItem(i, 0, QTableWidgetItem(signal))

            # ставим указатель на первый сигнал ()
            self.tb_signals.selectRow(0)

    def parser(self) -> None:
        """ 
        Detect encoding, delimiter, decimal in opened files
        only in first file
        """
        if self.extension.endswith('(*.gz)'): # если файлы архивы
            with gzip.open(self.files[0], 'rb') as f:
                data_raw = f.read(20000)
                second_row_raw = f.readlines()[1] # вторая строка быстрых
        else:
            with open(self.files[0], 'rb') as f:
                data_raw = f.read(20000)
                second_row_raw = f.readlines()[1]

        # Кодировка
        self.encoding = chardet.detect(data_raw).get('encoding')

        if self.encoding:
            # Разделитель
            data_str = data_raw[:200].decode(self.encoding)
            if data_str.count(';'):
                self.delimiter = ';'
            else:
                self.delimiter = '\t'

            # Decimal 
            second_row_str = second_row_raw.decode(self.encoding) 
            if second_row_str.count('.') > second_row_str.count(','):
                self.decimal = '.'
            else:
                self.decimal = ','

            self.ql_info.setText(f"Исходные файлы: encoding: {self.encoding} delimiter: {repr(self.delimiter)} decimal: {self.decimal}")
        else:
            text = f"Не удалось определить кодировку, попробуйте разархивировать файл {self.files[0]}"
            self.dialog_box(text)

    def add_signal(self, qlist_axe: QListWidget = 0, dict_axe: Dict = {}) -> None:
        """
        Remove signal from Qtable(Список сигналов) and append his to qlist(given qlist) and dict_axe
        """
        print(self.tb_signals.rowCount())
        print(self.tb_signals)
        if self.tb_signals.rowCount():
            row = self.tb_signals.currentRow()
            add_signal = self.tb_signals.item(row, 0).text()
            remove_row = self.dict_all_signals.pop(add_signal)
            dict_axe.setdefault(add_signal, remove_row)
            self.tb_signals.removeRow(row) 
            self.tb_signals.selectRow(0) # ставим указатель на первый сигнал
            qlist_axe.addItem(add_signal)  # добавляем 
            qlist_axe.setCurrentRow(0)
        else:
            self.dialog_box(f"Don't open files.\n\tor\nAll signals are already selected.")
        
        print(self.dict_all_signals)

    def remove_signal(self, qlist_axe: QListWidget, dict_axe: Dict = {}) -> None:
        """
        Remove signal from Qlist(given qlist) and append his to Qtable(Список сигналов) and dict_axe
        """
        if qlist_axe.count() and qlist_axe.currentRow() != -1:
            remove_signal = qlist_axe.takeItem(qlist_axe.currentRow()).text()
            remove_row_signal = dict_axe.pop(remove_signal)
            self.dict_all_signals.setdefault(remove_row_signal, remove_signal)
            row_position = self.tb_signals.rowCount()
            print(remove_row_signal, remove_signal)
            self.tb_signals.insertRow(row_position)
            self.tb_signals.setItem(remove_row_signal, 0, QTableWidgetItem(remove_signal))
            self.tb_signals.selectRow(0) # ставим указатель на первый сигнал
        else:
            self.dialog_box("don't select signals for removing")
        
    def clear_signals(self) -> None:
        """
        Clear All QListWidgets (Список сигналов, Основная Ось, Вспомогательная, Ось X)
        и их словари
        """
        self.dict_base_axe.clear()
        self.dict_secondary_axe.clear()
        self.dict_x_axe.clear()
        self.qlist_base_axe.clear()
        self.qlist_secondary_axe.clear()
        self.qlist_x_axe.clear()
        self.tb_signals.setRowCount(0)

    def load_field_name(self, qlist_axe: QListWidget, field_name: str, num: int) -> str:
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
        self.field_x.clear(), self.field_y.clear(), self.field_y2.clear()
        self.field_y = self.load_field_name(self.qlist_base_axe, self.field_y, 0) 
        self.field_y2 = self.load_field_name(self.qlist_secondary_axe, self.field_y2, 1) 
        self.field_x = self.load_field_name(self.qlist_x_axe, self.field_x, 2) 
        
        # Основная загрузка данных (из множества CSV файлов)
        if self.files:
            self.df = pd.concat(pd.read_csv(file, header=0, encoding=self.encoding, delimiter=self.delimiter,
                                            usecols=self.field_y+self.field_y2, decimal=self.decimal) for file in self.files)

            self.number_raw_point.setText(str(len(self.df.index)))
            # для токов и мощностей учет отрицательных значений
            all_signals = ['Электрическая мощность двигателя ЭМП ОЗ ГСМ-А, десятки Вт',
                           'Электрическая мощность двигателя ЭМП ОЗ ГСМ-Б, десятки Вт',
                           'Ток момента двигателя ЭМП ОЗ ГСМ-А, десятки мА',
                           'Ток момента двигателя ЭМП ОЗ ГСМ-Б, десятки мА',
                           'Ток статора ЭМП ОЗ ГСМ-А, десятки мА',
                           'Ток статора ЭМП ОЗ ГСМ-Б, десятки мА']
            for _ in self.field_y:
                if _ in all_signals:
                    self.df[_] = self.df[_].where(lambda x: x < 50000, lambda x: x - 65536)
                    print(_, ' - есть такой')
                else:
                    pass
                    # print(_, ' - нет такого')
            for _ in self.field_y2:
                if _ in all_signals:
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
        dlg = QMessageBox.information(self, 'TG_info', text, QMessageBox.StandardButton.Ok)

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