from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QHBoxLayout, QGroupBox, QVBoxLayout, QGridLayout, QLabel, QFileDialog, QListWidget, QComboBox, QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt5.QtCore import Qt
import sys
import os

# Добавляем корневую папку проекта (src) в sys.path для возможности корректного импорта модулей 
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.config.config import AxeName
from src.ui.myGroupBox import MyGroupBox


class MainWindow(QMainWindow):
    def __init__(self, version: str) -> None:
        super().__init__()
        self.setWindowTitle(version)
        self.init_ui()

    def init_ui(self):
        # Список сигналов:
        self.qt_all_signals = QTableWidget()
        self.qt_all_signals.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.qt_all_signals.setColumnCount(2)
        self.qt_all_signals.setColumnWidth(0, 1)
        self.qt_all_signals.horizontalHeader().hide() # type: ignore
        self.qt_all_signals.verticalHeader().hide() # type: ignore
        self.qt_all_signals.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.qt_all_signals.horizontalHeader().setStretchLastSection(True) # type: ignore
        self.qt_all_signals.resizeRowsToContents()

        btn_open_files = QPushButton('Open files')
        # btn_open_files.clicked.connect(self.insert_all_signals)
        
        signals_layout = QVBoxLayout()
        signals_layout.addWidget(self.qt_all_signals)
        signals_layout.addWidget(btn_open_files)

        # Список сигналов   
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

        self.third_lay = QGridLayout()
        self.third_lay.addWidget(QLabel('Количество исходных данных:'), 0, 0)
        self.third_lay.addWidget(QLabel('Выборка, каждые:'), 1, 0)
        self.third_lay.addWidget(QLabel('Количество отображаемых данных:'), 2, 0)
        self.third_lay.addWidget(self.number_raw_point, 0, 1)
        self.third_lay.addWidget(self.combobox_dot, 1, 1)
        self.third_lay.addWidget(self.number_plot_point, 2, 1)
        self.third_lay.addWidget(QLabel(), 2, 3)
        self.third_lay.addWidget(QLabel(), 2, 4)
        self.third_lay.addWidget(self.button_grath, 2, 5)

        self.third_huge_GroupBox = QGroupBox()
        self.third_huge_GroupBox.setLayout(self.third_lay)

        # Главный слой
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.first_huge_GroupBox)
        main_layout.addWidget(self.second_huge_GroupBox)
        main_layout.addWidget(self.third_huge_GroupBox)

        wid = QWidget(self)
        self.setCentralWidget(wid)
        wid.setLayout(main_layout)

    def add_signal(self, table, dictionary):
        # Логика добавления сигнала
        pass

    def remove_signal(self, table, dictionary):
        # Логика удаления сигнала
        pass

    def plot_grath(self):
        # Логика построения графиков
        pass


# ``` **Преимущества вынесения UI в отдельный файл**

# *   **Упрощение отладки**: Когда код UI находится в отдельном файле, легче находить и исправлять ошибки, так как вы можете сосредоточиться на конкретной части приложения.
# *   **Совместная работа**: Разделение кода позволяет нескольким разработчикам работать над разными частями проекта одновременно, что ускоряет процесс разработки.
# *   **Лучшая читаемость**: Код становится более читаемым и понятным, так как каждая часть отвечает за свою функциональность.

# **Рекомендации по организации кода**

# *   **Используйте шаблоны проектирования**: Например, шаблон MVC (Model-View-Controller) может помочь в организации кода и разделении логики.
# *   **Документируйте код**: Добавление комментариев и документации к каждому файлу и классу поможет другим разработчикам (или вам в будущем) быстрее понять структуру и логику приложения.

# **Пример использования шаблона MVC**

# ```python
# model.py
# class DataModel:
    # def __init__(self):
    #     self.data = []

    # def add_data(self, item):
    #     self.data.append(item)

    # def get_data(self):
    #     return self.data

# controller.py
# class Controller:
#     def __init__(self, model):
#         self.model = model

#     def add_item(self, item):
#         self.model.add_data(item)

# view.py

# class MainView(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Пример MVC")

# main.py
# from model import DataModel
# from controller import Controller
# from view import MainView

if __name__ == "__main__":
    # app = QApplication([])
    # model = DataModel()
    # controller = Controller(model)
    # view = MainView()
    # view.show()
    # app.exec_()
    
    sys_argv = sys.argv
    app = QApplication(sys_argv)
    ex = MainWindow("1.0.0")
    ex.show()
    try:
        sys.exit(app.exec())
    except:
        print("Пока")
