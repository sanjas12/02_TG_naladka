import os
import time
import pandas as pd
import sys
import chardet
import gzip
import csv
from typing import List, Dict, Tuple
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QGroupBox, \
    QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMainWindow, \
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from win32api import GetFileVersionInfo
from grath_matplot import WindowGrath
from config.config import MYTIME, AxeName, DEFAULT_TIME, FONT_SIZE
from myGroupBox import MyGroupBox


class MainWindow(QMainWindow):
    cycle_plc = 0.01

    def __init__(self, version: str) -> None:
        super().__init__()
        self.df = None
        self.ready_plot = False
        self.files, self.extension = None, None
        self.base_signals, self.secondary_signals = [], []
        self.dict_x_axe: Dict[str, int] = {}
        self.dict_base_axe: Dict[str, int] = {}
        self.dict_secondary_axe: Dict[str, int] = {}
        self.setup_ui(version)

    def setup_ui(self, version) -> None:
        self.setWindowTitle(version)

        # Список сигналов:
        self.qt_all_signals = QTableWidget()
        self.qt_all_signals.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.qt_all_signals.setColumnCount(2)
        self.qt_all_signals.setColumnWidth(0, 1)
        self.qt_all_signals.horizontalHeader().hide()
        self.qt_all_signals.verticalHeader().hide()
        self.qt_all_signals.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.qt_all_signals.horizontalHeader().setStretchLastSection(True)

        btn_open_files = QPushButton('Open files')
        btn_open_files.clicked.connect(self.insert_all_signals)
        
        signals_layout = QVBoxLayout()
        signals_layout.addWidget(self.qt_all_signals)
        signals_layout.addWidget(btn_open_files)
        
        self.gb_signals = QGroupBox("Список сигналов")
        self.gb_signals.setLayout(signals_layout)

        # Основная ось:
        self.gb_base_axe = MyGroupBox(title=AxeName.BASE_AXE.value)
        self.gb_base_axe.add_func_to_btn(self.gb_base_axe.btn_add, 
                                         lambda: self.add_signal(self.gb_base_axe.qtable_axe, self.gb_base_axe.dict_axe))
        self.gb_base_axe.add_func_to_btn(self.gb_base_axe.btn_remove, 
                                         lambda: self.remove_signal(self.gb_base_axe.qtable_axe, self.gb_base_axe.dict_axe))
        

        # Вспомогательная ось:
        self.gb_secondary_axe = MyGroupBox(title=AxeName.SECONDARY_AXE.value)
        self.gb_secondary_axe.add_func_to_btn(self.gb_secondary_axe.btn_add, 
                                         lambda: self.add_signal(self.gb_secondary_axe.qtable_axe, self.gb_secondary_axe.dict_axe))
        self.gb_secondary_axe.add_func_to_btn(self.gb_secondary_axe.btn_remove, 
                                         lambda: self.remove_signal(self.gb_secondary_axe.qtable_axe, self.gb_secondary_axe.dict_axe))

        # Ось X
        self.gb_x_axe = MyGroupBox(title=AxeName.X_AXE.value)
        self.gb_x_axe.add_func_to_btn(self.gb_x_axe.btn_add, 
                                         lambda: self.add_signal(self.gb_x_axe.qtable_axe, self.gb_x_axe.dict_axe))
        self.gb_x_axe.add_func_to_btn(self.gb_x_axe.btn_remove, 
                                         lambda: self.remove_signal(self.gb_x_axe.qtable_axe, self.gb_x_axe.dict_axe))
        
        # первый горизонтальный слой
        self.first_huge_lay = QHBoxLayout()
        self.first_huge_lay.addWidget(self.gb_signals)
        self.first_huge_lay.addWidget(self.gb_base_axe)
        self.first_huge_lay.addWidget(self.gb_secondary_axe)
        self.first_huge_lay.addWidget(self.gb_x_axe)

        self.first_huge_GroupBox = QGroupBox()
        self.first_huge_GroupBox.setLayout(self.first_huge_lay)

        # второй горизонтальный слой 
        self.ql_info = QLabel()

        self.second_lay = QHBoxLayout()
        self.second_lay.addWidget(self.ql_info)

        self.second_huge_GroupBox = QGroupBox()
        self.second_huge_GroupBox.setLayout(self.second_lay)

        # третий горизонтальный слой 
        self.number_raw_point = QLabel()
        self.number_plot_point = QLabel()
        list_dot = ['1', '10', '100', '1000', '10000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(1)
        self.button_grath = QPushButton('Построить графики')
        self.button_grath.clicked.connect(self.plot_grath)
        self.button_grath.setEnabled(False)

        second_vertical_lay = QGridLayout()
        second_vertical_lay.addWidget(QLabel('Количество исходных данных:'), 0, 0)
        second_vertical_lay.addWidget(QLabel('Выборка, каждые:'), 1, 0)
        second_vertical_lay.addWidget(QLabel('Количество отображаемых данных:'), 2, 0)
        second_vertical_lay.addWidget(self.number_raw_point, 0, 1)
        second_vertical_lay.addWidget(self.combobox_dot, 1, 1)
        second_vertical_lay.addWidget(self.number_plot_point, 2, 1)
        second_vertical_lay.addWidget(QLabel(), 2, 3)
        second_vertical_lay.addWidget(QLabel(), 2, 4)
        second_vertical_lay.addWidget(self.button_grath, 2, 5)
        
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
        Create List contein opened files and his extension
        """
        FILE_FILTERS = [
            "GZ Files (*.gz)",
            "CSV Files (*.csv)",
            "txt (*.txt)"
        ]
        self.files, self.extension = QFileDialog.getOpenFileNames(self, 'Выбор данных: ', initialFilter=FILE_FILTERS[0], 
                                                                    filter=";;".join(FILE_FILTERS))
        
    def read_all_signals(self) -> None:

        if self.encoding:
            # Считывание названия всех сигналов из первого файла
            df_all_signals = pd.read_csv(self.files[0], encoding=self.encoding, delimiter=self.delimiter, nrows=0)
            
            # удаляем лишние колонки
            df_all_signals = df_all_signals.loc[:, ~df_all_signals.columns.str.contains('^Unnamed')]
            self.dict_all_signals: Dict[str, int] = {signal:i for i, signal in enumerate(df_all_signals.columns, start=1)}
            # print(f"{self.dict_all_signals=}")
           
    def insert_all_signals(self) -> None:
        """
        Clear all old signals and insert new signals to QTable(Список сигналов)
        """
        try:
            self.qt_all_signals.setRowCount(0)
            self.clear_signals()
            self.open_files()

            if self.files:
                self.button_grath.setEnabled(True)
                self.parser(self.files[0])
                self.read_all_signals()
                self.insert_all_signals_true(self.qt_all_signals, self.dict_all_signals)
                self.insert_default_time()
        
        except EOFError:
            self.dialog_box(f"Ошибка в данных {self.files}. Файл испорчен. Попробуйте распаковать сторонним архиватором.")
            
    def insert_all_signals_true(self, qt_axe: QTableWidget, dict_axe: Dict[str, int]) -> None:
            qt_axe.setRowCount(0)
            for signal, i in sorted(dict_axe.items(), key=lambda item: item[1]):
                row_position = qt_axe.rowCount()
                qt_axe.insertRow(row_position)
                qt_axe.setItem(row_position, 0, QTableWidgetItem(str(i)))
                qt_axe.setItem(row_position, 1, QTableWidgetItem(signal))

    def insert_default_time(self) -> None:
        if DEFAULT_TIME in self.dict_all_signals.keys():
            self.qt_all_signals.selectRow(0)
            self.add_signal(self.gb_x_axe.qtable_axe, self.gb_x_axe.dict_axe)
            print("дефолтное время найдено")
        else:
            print("дефолтное время не найдено")

    def parser(self, file: str = None, read_bytes: int = 20000) -> None:
        """
        Detect encoding, delimiter, decimal in opened files by first file
        
        :param file: Путь к файлу для анализа.
        :param read_bytes: Количество байт для чтения из файла (по умолчанию 20,000).
        
        """

        if not file or not os.path.isfile(file):
            self.dialog_box(f"Файл не указан или недоступен: {file}")
            return
        
        try:
            if file.endswith(".gz"):  # если файлы архивы
                with gzip.open(self.files[0], "rb") as f: # type: ignore
                    data_raw = f.read(read_bytes)
                    f.seek(0)
                    second_row_raw = f.readlines()[1]  # вторая строка быстрых
            else:
                with open(self.files[0], "rb") as f: # type: ignore
                    data_raw = f.read(read_bytes)
                    f.seek(0)
                    second_row_raw = f.readlines()[1]

            # Encoding detection
            self.encoding = chardet.detect(data_raw).get("encoding")

            if self.encoding:
                data_str = data_raw[:200].decode(self.encoding, errors='ignore')
                # Delimiter detection
                if data_str.count(";") > data_str.count("\t"):
                    self.delimiter = ";"
                else:
                    self.delimiter = "\t"

                # Decimal detection
                second_row_str = second_row_raw.decode(self.encoding)
                if second_row_str.count(".") > second_row_str.count(","):
                    self.decimal = "."
                else:
                    self.decimal = ","

                self.ql_info.setText(
                    f"Исходные файлы: encoding: {self.encoding} delimiter: {repr(self.delimiter)} decimal: {self.decimal}"
                )
            else:
                raise ValueError("Encoding could not be detected")

        except Exception as e:
            text = (
                f"Не удалось определить параметры файла: {str(e)}\n"
                f"Не удалось определить кодировку, попробуйте разархивировать файл {file}"
            )
            self.dialog_box(text)
        
    def add_signal(self, qt_axe: QTableWidget, dict_axe: Dict[str, int]) -> None:
        """
        Remove signal from Qtable(Список сигналов) and append his to qlist(given qlist) and dict_axe
        """
        if self.qt_all_signals.rowCount() and self.qt_all_signals.currentRow() > -1:
            row = self.qt_all_signals.currentRow()
            index_signal = self.qt_all_signals.item(row, 0).text() # type: ignore
            signal = self.qt_all_signals.item(row, 1).text() # type: ignore
            dict_axe.setdefault(signal, int(index_signal))
            self.qt_all_signals.removeRow(row)
            self.dict_all_signals.pop(signal) 

            self.insert_all_signals_true(qt_axe, dict_axe)
        else:
            self.dialog_box(f"Don't open files.\nDon't select signal.\nAll signals are already selected.")
        
    def remove_signal(self, qt_axe: QTableWidget, dict_axe: Dict[str, int]) -> None:
        """
        Remove signal from Qlist(given qlist) and append his to Qtable(Список сигналов) and dict_axe
        """
        if qt_axe.rowCount() and qt_axe.currentRow() > -1:
            row = qt_axe.currentRow()
            index_signal = qt_axe.item(row, 0).text() # type: ignore
            signal = qt_axe.item(row, 1).text() # type: ignore
            self.dict_all_signals.setdefault(signal, int(index_signal))
            print(f"{signal=} {index_signal=}")
            qt_axe.removeRow(row)
            dict_axe.pop(signal)

            self.insert_all_signals_true(self.qt_all_signals, self.dict_all_signals)
        else:
            self.dialog_box("don't select signals for removing")
        
    def clear_signals(self) -> None:
        """
        Clear All QTableWidgets (Список сигналов, Основная Ось, Вспомогательная, Ось X)
        и их словари
        """
        self.button_grath.setEnabled(False)
        self.dict_base_axe.clear()
        self.dict_secondary_axe.clear()
        self.dict_x_axe.clear()
        self.gb_base_axe.qtable_axe.clear()
        self.gb_secondary_axe.qtable_axe.clear()
        self.gb_x_axe.qtable_axe.clear()
        self.qt_all_signals.setRowCount(0)
        self.ql_info.setText(f"")
    
    def selected_signals(self, qt_axe: QTableWidget, name_axe: str) -> List[str]:
        if qt_axe.rowCount() > 0:
            return [qt_axe.item(_, 1).text() for _ in range(qt_axe.rowCount())]
        else:
            print(f"{time.ctime()} -> Для {name_axe} не выбраны сигналы")
            return []

    def load_data_for_plot(self) -> None:
        self.df = None
        self.base_signals.clear()
        self.secondary_signals.clear()
        
        self.base_signals = self.selected_signals(self.gb_base_axe.qtable_axe, AxeName.BASE_AXE.value) 
        self.secondary_signals = self.selected_signals(self.gb_secondary_axe.qtable_axe, AxeName.SECONDARY_AXE.value) 
        self.x_axe = self.selected_signals(self.gb_x_axe.qtable_axe, AxeName.X_AXE.value)

        # Основная загрузка данных (из нескольких файлов)
        if self.files and (self.base_signals or self.secondary_signals):

            self.df = pd.concat(pd.read_csv(file, header=0, encoding=self.encoding, delimiter=self.delimiter,
                                            usecols=self.base_signals+self.secondary_signals+self.x_axe, decimal=self.decimal) for file in self.files)

            self.number_raw_point.setText(str(len(self.df.index)))

            self.ready_plot = True
        else:
            text = f"Не открыты файлы архивов или не выбраны сигналы"
            self.dialog_box(text)

    def dialog_box(self, text: str) -> None:
        QMessageBox.information(self, 'TG_info', text, QMessageBox.StandardButton.Ok)

    def plot_grath(self) -> None:
        self.load_data_for_plot()
        if self.ready_plot:
            self.number_plot_point.setText(str(int(len(self.df.index)/int(self.combobox_dot.currentText()))))
            self.grath = WindowGrath(self.df, self.base_signals, self.secondary_signals, *self.x_axe, 
                                    step=self.combobox_dot.currentText(), filename=self.files[0])
            self.grath.show()


def main():
    global app
    sys_argv = sys.argv
    if '.exe' in sys.argv[0]:                                # если EXE in Win
        version = GetFileVersionInfo(sys.argv[0], '\\')
        version = (version['FileVersionMS'] // 65536, version['FileVersionMS'] % 65536, version['FileVersionLS'] // 65536, version['FileVersionLS'] % 65536)
        version = '#' + '.'.join(map(str, version))
    else:
        with open('setup.py', 'r+', encoding='utf-8') as f:
            version = f.readline()
        print(version)

    app = QApplication(sys_argv)
    
    font_size =FONT_SIZE
    style = f"""
        * {{
        font-size: {font_size}pt;
        font-family: Arial;
        }}
    """
    app.setStyleSheet(style)
    
    ex = MainWindow(version)
    ex.show()
    try:
        sys.exit(app.exec())
    except:
        print("Пока")

if __name__ == '__main__':
    main()