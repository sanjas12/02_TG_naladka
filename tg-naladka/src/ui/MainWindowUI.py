from pathlib import Path
import sys
from PyQt5.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QTableWidget,
    QAbstractItemView,
    QLabel,
    QComboBox,
    QGridLayout,
    QMessageBox
)
from typing import Dict, Callable, Union

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import AxeName


class CreateTable:
    @staticmethod
    def create_table() -> QTableWidget:
        table = QTableWidget()
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setColumnCount(2)
        table.setColumnWidth(0, 1)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.resizeRowsToContents()
        return table


class MainWindowUI(QMainWindow):
    def __init__(self, version: str):
        super().__init__()
        self.setup_ui(version)

    def setup_ui(self, version: str):
        self.setWindowTitle(version)

        # Список сигналов:
        self.gb_signals = MyGroupBox(
            title=AxeName.LIST_SIGNALS.value,
            name_first_button="Open files",
            enable_second_btn=False,
        )

        # Основная ось:
        self.gb_base_axe = MyGroupBox(title=AxeName.BASE_AXE.value)

        # Вспомогательная ось:
        self.gb_secondary_axe = MyGroupBox(title=AxeName.SECONDARY_AXE.value)

        # Ось X
        self.gb_x_axe = MyGroupBox(title=AxeName.TIME_AXE.value, enable_first_btn=False, enable_second_btn=False)

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
        list_dot = ["1", "10", "100", "1000", "10000"]
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(1)
        self.button_grath = QPushButton("Построить графики")
        self.button_grath.setEnabled(False)

        second_vertical_lay = QGridLayout()
        second_vertical_lay.addWidget(QLabel("Количество исходных данных:"), 0, 0)
        second_vertical_lay.addWidget(QLabel("Выборка, каждые:"), 1, 0)
        second_vertical_lay.addWidget(QLabel("Количество отображаемых данных:"), 2, 0)
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

    def dialog_box(self, text: str) -> None:
        QMessageBox.information(self, 'TG_info', text, QMessageBox.StandardButton.Ok)
    
    def show_error(self, message: str) -> None:
        """Показывает сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)

class MyGroupBox(QGroupBox):
    """
    Custom QGroupBox с кнопками добавления и удаления.

    Аргументы:
        title (str, optional): Заголовок группы. Defaults to None.
        name_first_button (str, optional): Текст первой кнопки. Defaults to "Add to Axe".
        name_second_button (str, optional): Текст второй кнопки. Defaults to "Remove from Axe".
        enable_first_btn (bool, optional): Включена ли первая кнопка. Defaults to True.
        enable_second_btn (bool, optional): Включена ли вторая кнопка. Defaults to True.
    """

    # Определяем тип для функции, которая может принимать 2 параметра или не принимать параметры
    FuncType = Union[Callable[[], None], Callable[[QTableWidget, Dict[str, int]], None]]

    def __init__(
        self,
        title: str = None,
        name_first_button: str = "Add to Axe",
        name_second_button: str = "Remove from Axe",
        enable_first_btn: bool = True,
        enable_second_btn: bool = True,
    ):
        super().__init__(title)

        self.dict_axe: Dict[str, int] = {}
        self.qtable_axe = CreateTable.create_table()

        self.btn_first = self._create_button(name_first_button, enable_first_btn)
        self.btn_second = self._create_button(name_second_button, enable_second_btn)

        self.lay = QVBoxLayout()
        self.lay.addWidget(self.qtable_axe)

        if enable_first_btn:
            self.lay.addWidget(self.btn_first)
        if enable_second_btn:
            self.lay.addWidget(self.btn_second)

        self.setLayout(self.lay)

    def _create_button(self, name: str, is_enabled: bool) -> QPushButton:
        """Создает кнопку с заданным текстом и состоянием."""
        btn = QPushButton(name)
        btn.setVisible(is_enabled)
        return btn

    def add_func_to_btn(self, btn: QPushButton, func: FuncType):
        """Добавляет функцию к кнопке, если она передана."""
        if func:
            btn.clicked.connect(lambda: func())
        else:
            btn.clicked.connect(lambda: print("Функция не определена"))

# для тестирования 3-x myGroupBox
class TestMyGroupBox(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        # self.layout = QVBoxLayout()
        # for _ in range(3):
        #     btn = QPushButton(str(_))
        #     self.layout.addWidget(btn)

        self.layout = QHBoxLayout()

        # self.my_group = MyGroupBox("test", "какая-то ось")
        # self.layout.addWidget(self.my_group)
        # for axe in AxeName:
        #     _ = MyGroupBox(title=axe.value)
        #     self.layout.addWidget(_)

        self.gb_base_axe = MyGroupBox("Base Axe")
        self.gb_secondary_axe = MyGroupBox("Secondary Axe")
        self.gb_x_axe = MyGroupBox("X Axe")

        for box in [self.gb_base_axe, self.gb_secondary_axe, self.gb_x_axe]:
            self.layout.addWidget(box)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def test(self, text):
        print(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # для тестирования 3-x myGroupBox создан класс TestMyGroupBox
    # window = TestMyGroupBox()    # для тестирования 3-x myGroupBox создан класс MainWindow
    # window.show()             # для тестирования 3-x myGroupBox

    # для тестирования одного myGroupBox
    # box = MyGroupBox(button_add_name="1 кнопка", title="заголовок", enable_btns=True)
    # box.add_func_to_btn(box.btn_first, lambda: test("add"))
    # box.add_func_to_btn(box.btn_second, lambda: test("remove"))
    # box.show()
    # def test(text):
    #    print(text + "  some text")

    # для тестирования главного окна
    main_window = MainWindowUI("Test")
    main_window.gb_base_axe.add_func_to_btn(main_window.gb_base_axe.btn_first, lambda: test("add to base axe"))
    main_window.gb_base_axe.add_func_to_btn(main_window.gb_base_axe.btn_second, lambda: test("remove from base axe"))
    main_window.gb_signals.add_func_to_btn(main_window.gb_signals.btn_first, lambda: test("add func to parser all sugnals"))
    
    def test(text: str):
       print(text + "  some text")
    
    main_window.show()

    app.exec()
