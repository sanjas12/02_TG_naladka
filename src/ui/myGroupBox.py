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
)
from typing import Dict, Callable, Union



class MyGroupBox(QGroupBox):
    """
    Custom QGroupBox с кнопками добавления и удаления.

    Аргументы:
        title (str, optional): Заголовок группы. Defaults to None.
        button_add_name (str, optional): Текст кнопки добавления. Defaults to "Add to Axe".
        button_remove_name (str, optional): Текст кнопки удаления. Defaults to "Remove from Axe".
        enable_btns (bool, optional): Включены ли кнопки по умолчанию. Defaults to True.
    """

    def __init__(
        self,
        title: str = None,
        button_add_name: str = "Add to Axe",
        button_remove_name: str = "Remove from Axe",
        enable_btns: bool = True,
    ):
        super().__init__(title)

        self.dict_axe = {}
        self.qtable_axe = self._create_table()

        self.btn_add = QPushButton(button_add_name)
        self.btn_remove = QPushButton(button_remove_name)

        self.lay = QVBoxLayout()
        self.lay.addWidget(self.qtable_axe)
        
        if enable_btns:
            self.lay.addWidget(self.btn_add)
            self.lay.addWidget(self.btn_remove)

        self.setLayout(self.lay)

    def _create_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setColumnCount(2)
        table.setColumnWidth(0, 1)
        table.horizontalHeader().hide()
        table.verticalHeader().hide()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        return table

    # Определяем тип для функции, которая может принимать 2 параметра или не принимать параметры
    FuncType = Union[Callable[[], None], Callable[[QTableWidget, Dict[str, int]], None]]

    def add_func_to_btn(self, btn: QPushButton, func: FuncType):
        if func:
            btn.clicked.connect(lambda: func())  # type: ignore # Передача внешней функции
        else:
            btn.clicked.connect(lambda: print("Функция не определена"))


class MainWindow(QMainWindow):
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
    # window = MainWindow()    # для тестирования создан MainWindow
    # window.show()             # для тестирования создан 
   
    box = MyGroupBox(button_add_name="1 кнопка", title="заголовок", enable_btns=True)
    box.add_func_to_btn(box.btn_add, lambda: test("sdsd"))
    box.add_func_to_btn(box.btn_remove, lambda: test("remove"))
    box.show()

    def test(text):
        print(text + "  dsdsd")

    app.exec()
