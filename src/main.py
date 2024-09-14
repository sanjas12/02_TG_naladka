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
from config.config import MYTIME, AxeName


class MyGroupBox(QWidget):
        """
        My group box Widget
        """
        def __init__(self, parent = None, name: str = ''):
            super().__init__(parent)
            self.qt_base_axe = QListWidget()
            btn_base_axe_add = QPushButton(f'Add to {name}')
            btn_base_axe_add.clicked.connect(lambda: self.add_signal(self.qt_base_axe, self.dict_base_axe))
            btn_base_axe_remove = QPushButton(f'Remove from {name}')
            btn_base_axe_remove.clicked.connect(lambda: self.remove_signal(self.qt_base_axe, self.dict_base_axe))
            
            base_axe_layout = QVBoxLayout()
            base_axe_layout.addWidget(self.qt_base_axe)
            base_axe_layout.addWidget(btn_base_axe_add)
            base_axe_layout.addWidget(btn_base_axe_remove)
            
            self.gb_base_axe = QGroupBox(name)
            self.gb_base_axe.setLayout(base_axe_layout)
        
        def add_signal(self, qt_axe: QListWidget = 0, dict_axe: Dict = {}) -> None:
            """
            Remove signal from Qtable(Список сигналов) and append his to qlist(given qlist) and dict_axe
            """
            if self.qt_all_signals.rowCount():
                row = self.qt_all_signals.currentRow()
                add_signal = self.qt_all_signals.item(row, 0).text()
                remove_row = self.dict_all_signals.pop(add_signal)
                dict_axe.setdefault(add_signal, remove_row)
                self.qt_all_signals.removeRow(row) 
                # self.qt_all_signals.selectRow(0) # ставим указатель на первый сигнал
                qt_axe.addItem(add_signal)  # добавляем 
                qt_axe.setCurrentRow(0)
            else:
                self.dialog_box(f"Don't open files.\n\tor\nAll signals are already selected.")
        
        def remove_signal(self, qt_axe: QListWidget, dict_axe: Dict = {}) -> None:
            """
            Remove signal from Qlist(given qlist) and append his to Qtable(Список сигналов) and dict_axe
            """
            if qt_axe.count() and qt_axe.currentRow() != -1:
                remove_signal = qt_axe.takeItem(qt_axe.currentRow()).text()
                remove_row_signal = dict_axe.pop(remove_signal)
                self.dict_all_signals.setdefault(remove_row_signal, remove_signal)
                row_position = self.qt_all_signals.rowCount()
                self.qt_all_signals.insertRow(row_position)
                self.qt_all_signals.setItem(remove_row_signal, 0, QTableWidgetItem(remove_signal))
                self.qt_all_signals.selectRow(0) # ставим указатель на первый сигнал
            else:
                self.dialog_box("don't select signals for removing")


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
        self.field_name = ("Основная Ось", "Вспомогательная Ось", "Ось X (Времени)")
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
        # self.qt_all_signals.setSortingEnabled(True)

        btn_open_files = QPushButton('Open files')
        btn_open_files.clicked.connect(self.insert_all_signals)
        
        signals_layout = QVBoxLayout()
        signals_layout.addWidget(self.qt_all_signals)
        signals_layout.addWidget(btn_open_files)
        
        self.gb_signals = QGroupBox("Список сигналов")
        self.gb_signals.setLayout(signals_layout)

        # Основная ось:
        self.qt_base_axe = QTableWidget()
        self.qt_base_axe.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.qt_base_axe.setColumnCount(2)
        self.qt_base_axe.setColumnWidth(0, 1)
        self.qt_base_axe.horizontalHeader().hide()
        self.qt_base_axe.verticalHeader().hide()
        self.qt_base_axe.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.qt_base_axe.horizontalHeader().setStretchLastSection(True)
        
        btn_base_axe_add = QPushButton('Add to Y')
        btn_base_axe_add.clicked.connect(lambda: self.add_signal(self.qt_base_axe, self.dict_base_axe))
        btn_base_axe_remove = QPushButton('Remove from Y')
        btn_base_axe_remove.clicked.connect(lambda: self.remove_signal(self.qt_base_axe, self.dict_base_axe))
        
        base_axe_layout = QVBoxLayout()
        base_axe_layout.addWidget(self.qt_base_axe)
        base_axe_layout.addWidget(btn_base_axe_add)
        base_axe_layout.addWidget(btn_base_axe_remove)
        
        self.gb_base_axe = QGroupBox(AxeName.BASE_AXE.value)
        self.gb_base_axe.setLayout(base_axe_layout)

        # Вспомогательная ось:
        self.qt_secondary_axe = QTableWidget()
        self.qt_secondary_axe.setColumnCount(2)
        self.qt_secondary_axe.setColumnWidth(0, 1)
        self.qt_secondary_axe.horizontalHeader().hide()
        self.qt_secondary_axe.verticalHeader().hide()
        self.qt_secondary_axe.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.qt_secondary_axe.horizontalHeader().setStretchLastSection(True)
        btn_secondary_axe_add = QPushButton('Add to Y2')
        btn_secondary_axe_add.clicked.connect(lambda: self.add_signal(self.qt_secondary_axe, self.dict_secondary_axe))
        btn_secondary_axe_remove = QPushButton('Remove from Y2')
        btn_secondary_axe_remove.clicked.connect(lambda: self.remove_signal(self.qt_secondary_axe, self.dict_secondary_axe))
        
        secondary_axe_layout = QVBoxLayout()
        secondary_axe_layout.addWidget(self.qt_secondary_axe)
        secondary_axe_layout.addWidget(btn_secondary_axe_add)
        secondary_axe_layout.addWidget(btn_secondary_axe_remove)
        
        self.gb_secondary_axe = QGroupBox(AxeName.SECONDARY_AXE.value)
        self.gb_secondary_axe.setLayout(secondary_axe_layout)

        # Ось X
        self.qt_x_axe = QTableWidget()
        btn_x_axe_add = QPushButton('Add to X')
        btn_x_axe_add.clicked.connect(lambda: self.add_signal(self.qt_x_axe, self.dict_x_axe))
        btn_x_axe_remove = QPushButton('Remove from X')
        btn_x_axe_remove.clicked.connect(lambda: self.remove_signal(self.qt_x_axe))
        
        layout_x_axe = QVBoxLayout()
        layout_x_axe.addWidget(self.qt_x_axe)
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
            self.qt_base_axe.setRowCount(0)
            self.qt_secondary_axe.setRowCount(0)
            self.open_files()
            self.clear_signals()

            if self.files:
                self.parser(self.files[0])
                self.read_all_signals()
                self.insert_all_signals_true(self.qt_all_signals, self.dict_all_signals)
        
        except EOFError:
            self.dialog_box(f"Ошибка в данных {self.files}. Файл испорчен. Попробуйте распаковать сторонним архиватором.")
            
    def insert_all_signals_true(self, qt_axe: QTableWidget, dict_axe: Dict[str, int]) -> None:
            qt_axe.setRowCount(0)
            for signal, i in sorted(dict_axe.items(), key=lambda item: item[1]):
                row_position = qt_axe.rowCount()
                qt_axe.insertRow(row_position)
                qt_axe.setItem(row_position, 0, QTableWidgetItem(str(i)))
                qt_axe.setItem(row_position, 1, QTableWidgetItem(signal))
                
    def parser(self, file: str = None) -> None:
        """
        Detect encoding, delimiter, decimal in opened files by first file
        """

        if not file:
            self.dialog_box(f"Файл не указан или недоступен: {file}")
            return
        
        try:
            if self.extension.endswith("(*.gz)"):  # если файлы архивы
                with gzip.open(self.files[0], "rb") as f: # type: ignore
                    data_raw = f.read(20000)
                    f.seek(0)
                    second_row_raw = f.readlines()[1]  # вторая строка быстрых
            else:
                with open(self.files[0], "rb") as f: # type: ignore
                    data_raw = f.read(20000)
                    f.seek(0)
                    second_row_raw = f.readlines()[1]

            # Encoding detection
            self.encoding = chardet.detect(data_raw).get("encoding")

            if self.encoding:
                data_str = data_raw[:200].decode(self.encoding)
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
        self.dict_base_axe.clear()
        self.dict_secondary_axe.clear()
        self.dict_x_axe.clear()
        self.qt_base_axe.clear()
        self.qt_secondary_axe.clear()
        self.qt_x_axe.clear()
        self.qt_all_signals.setRowCount(0)
    
    def selected_signals(self, qt_axe: QTableWidget, name_axe: str) -> List[str]:
        if qt_axe.rowCount() > 0:
            return [qt_axe.item(_).text() for _ in range(qt_axe.count())]
        else:
            print(f"{time.ctime()} -> Для {name_axe} не выбраны сигналы")
            return []

    def load_data_for_plot(self) -> None:
        self.df = None
        self.base_signals.clear(), self.secondary_signals.clear()
        
        self.base_signals = self.selected_signals(self.qt_base_axe, AxeName.BASE_AXE.value) 
        self.secondary_signals = self.selected_signals(self.qt_secondary_axe, AxeName.SECONDARY_AXE.value) 
        self.x_axe = self.selected_signals(self.qt_x_axe, AxeName.X_AXE.value)
        row = self.qt_all_signals.selectRow(0)
        print('row ->', row)

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
    ex = MainWindow(version)
    ex.show()
    try:
        sys.exit(app.exec())
    except:
        print("Пока")

if __name__ == '__main__':
    main()