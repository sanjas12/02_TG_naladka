import sys
import time
from pathlib import Path
from typing import Dict, Optional, Callable, Union

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressDialog,
    QTableWidget,
    QVBoxLayout,
    QWidget,
    QAbstractItemView,
    QCheckBox,
)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import AxeName


class WorkerThread(QThread):
    """Поток для имитации длительной загрузки данных."""

    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def run(self) -> None:
        total = 100
        for i in range(total + 1):
            time.sleep(0.03)  # имитация работы
            self.progress.emit(i)
        self.finished.emit()


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
        self.progress_dialog: Optional[QProgressDialog] = None
        self.worker_thread: Optional[WorkerThread] = None
        self.setup_ui(version)

    def setup_ui(self, version: str) -> None:
        self.setWindowTitle(version)

        # Группы
        self.gb_signals = MyGroupBox(
            title=AxeName.LIST_SIGNALS.value,
            name_first_button="Open files",
            enable_second_btn=False,
            enable_analyzer=False,
        )
        self.gb_base_axe = MyGroupBox(title=AxeName.BASE_AXE.value)
        self.gb_secondary_axe = MyGroupBox(title=AxeName.SECONDARY_AXE.value, enable_analyzer=False)
        self.gb_x_axe = MyGroupBox(
            title=AxeName.TIME_AXE.value,
            enable_first_btn=False,
            enable_second_btn=False,
            enable_analyzer=False,
        )

        # Первый горизонтальный слой
        first_layout = QHBoxLayout()
        for box in (
            self.gb_signals,
            self.gb_base_axe,
            self.gb_secondary_axe,
            self.gb_x_axe,
        ):
            first_layout.addWidget(box)
        self.first_group = QGroupBox()
        self.first_group.setLayout(first_layout)

        # Второй слой
        self.ql_info = QLabel()
        second_layout = QHBoxLayout()
        second_layout.addWidget(self.ql_info)
        self.second_group = QGroupBox()
        self.second_group.setLayout(second_layout)

        # Третий слой
        self.button_graph = QPushButton("Построить графики")
        self.button_graph.setEnabled(False)

        third_layout = QGridLayout()
        third_layout.addWidget(QLabel(), 0, 1)
        third_layout.addWidget(QLabel(), 0, 2)
        third_layout.addWidget(QLabel(), 0, 3)
        third_layout.addWidget(self.button_graph, 0, 5)

        third_group = QGroupBox()
        third_group.setLayout(third_layout)

        # Главный слой
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.first_group)
        main_layout.addWidget(self.second_group)
        main_layout.addWidget(third_group)
        wid = QWidget(self)
        wid.setLayout(main_layout)
        self.setCentralWidget(wid)

    # ================= Модальный прогресс ===================
    def start_modal_progress(
        self, title: str = "Загрузка данных…", maximum: int = 0
    ) -> None:
        self.progress_dialog = QProgressDialog(title, None, 0, maximum, self)
        self.progress_dialog.setWindowTitle("Пожалуйста, подождите")
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setCancelButton(None)
        self.progress_dialog.setMinimumWidth(500)
        self.progress_dialog.show()

    def set_modal_progress(self, value: int) -> None:
        if self.progress_dialog:
            self.progress_dialog.setValue(value)
            QApplication.processEvents()

    def stop_modal_progress(self) -> None:
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None

    def dialog_box(self, text: str) -> None:
        QMessageBox.information(self, "TG_info", text, QMessageBox.StandardButton.Ok)

    def show_error(self, message: str) -> None:
        """Показывает сообщение об ошибке"""
        QMessageBox.critical(self, "Ошибка", message)


class MyGroupBox(QGroupBox):
    """
    Кастомный QGroupBox с кнопками добавления и удаления.
    
    Аргументы:
        title (str, optional): Заголовок группы. Defaults to None.
        name_first_button (str, optional): Текст первой кнопки. Defaults to "Add to Axe".
        name_second_button (str, optional): Текст второй кнопки. Defaults to "Remove from Axe".
        enable_first_btn (bool, optional): Включена ли первая кнопка. Defaults to True.
        enable_second_btn (bool, optional): Включена ли вторая кнопка. Defaults to True.
    """


    def __init__(
        self,
        title: Optional[str] = None,
        name_first_button: str = "Add to Axe",
        name_second_button: str = "Remove from Axe",
        enable_first_btn: bool = True,
        enable_second_btn: bool = True,
        enable_analyzer: bool = True,
    ):
        super().__init__(title)
        self.dict_axe: Dict[str, int] = {}
        self.qtable_axe = CreateTable.create_table()
        self.btn_first = self._create_button(name_first_button, enable_first_btn)
        self.btn_second = self._create_button(name_second_button, enable_second_btn)
        self.ch_analyzer = QCheckBox("Анализ регулятора ГСМ")
        self.ch_analyzer.setEnabled(False)
        self.ch_analyzer.setChecked(False)

        layout = QVBoxLayout()
        layout.addWidget(self.qtable_axe)
        if enable_first_btn:
            layout.addWidget(self.btn_first)
        if enable_second_btn:
            layout.addWidget(self.btn_second)
        if enable_analyzer:
            layout.addWidget(self.ch_analyzer)
        self.setLayout(layout)

    def _create_button(self, name: str, is_enabled: bool) -> QPushButton:
        """Создает кнопку с заданным текстом и состоянием."""
        btn = QPushButton(name)
        btn.setVisible(is_enabled)
        return btn

    # Определяем тип для функции, которая может принимать 2 параметра или не принимать параметры
    FuncType = Union[Callable[[], None], Callable[[QTableWidget, Dict[str, int]], None]]
    
    def add_func_to_btn(self, btn: QPushButton, func: FuncType) -> None:
        """Добавляет функцию к кнопке."""
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
