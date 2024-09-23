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
from config.config import AxeName


class MyGroupBox(QGroupBox):
    def __init__(
        self,
        button_add_name: str = "Add to Axe",
        button_remove_name: str = "Remove from Axe",
        title: str = None,
    ):
        super().__init__(title)

        self.dict_axe = {}
        self.qtable_axe = QTableWidget()
        self.qtable_axe.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.qtable_axe.setColumnCount(2)
        self.qtable_axe.setColumnWidth(0, 1)
        self.qtable_axe.horizontalHeader().hide()
        self.qtable_axe.verticalHeader().hide()
        self.qtable_axe.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.qtable_axe.horizontalHeader().setStretchLastSection(True)

        self.btn_add = QPushButton(button_add_name)
        self.btn_remove = QPushButton(button_remove_name)

        self.lay = QVBoxLayout()
        self.lay.addWidget(self.qtable_axe)
        self.lay.addWidget(self.btn_add)
        self.lay.addWidget(self.btn_remove)

        self.setLayout(self.lay)


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

        # Основная ось:
        self.gb_base_axe = MyGroupBox(title=AxeName.BASE_AXE.value)
        self.layout.addWidget(self.gb_base_axe)

        # Вспомогательная ось:
        self.gb_secondary_axe = MyGroupBox(title=AxeName.SECONDARY_AXE.value)
        self.layout.addWidget(self.gb_secondary_axe)

        # Ось X
        self.gb_x_axe = MyGroupBox(title=AxeName.X_AXE.value)
        self.layout.addWidget(self.gb_x_axe)  # type: ignore

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

    def test(self, text):
        print(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # window = MainWindow()
    # window.show()
    box = MyGroupBox(button_add_name="1 кнопка", title="заголовок")
    box.add_func_to_btn(box.btn_add, lambda: test("sdsd"))
    box.add_func_to_btn(box.btn_remove, lambda: test("remove"))
    box.show()

    def test(text):
        print(text + "  dsdsd")

    app.exec()
