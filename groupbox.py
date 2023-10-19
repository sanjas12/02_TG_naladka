import sys
from PyQt5.QtWidgets import (QGroupBox,
                            QListWidget,
                            QPushButton, 
                            QVBoxLayout,
                            QApplication,
                            QMainWindow,
                            QWidget,
                            QHBoxLayout
)


class MyGroupBox(QGroupBox):
        def __init__(self):
            super().__init__()
            self.qlist_secondary_axe = QListWidget()
            self.btn_secondary_axe_add = QPushButton('Add to Y2')
            # btn_secondary_axe_add.clicked.connect(lambda: self.add_to_qlist(self.qlist_secondary_axe))
            # btn_secondary_axe_remove = QPushButton('Remove from Y2')
            # btn_secondary_axe_remove.clicked.connect(lambda: self.remove_qlist(self.qlist_secondary_axe))
            
            self.lay = QVBoxLayout()
            self.lay.addWidget(self.qlist_secondary_axe)
            self.lay.addWidget(self.btn_secondary_axe_add)
            # secondary_axe_layout.addWidget(btn_secondary_axe_remove)
            
            self.gb_secondary_axe = QGroupBox("Вспомогательная Ось")
            self.gb_secondary_axe.setLayout(self.lay)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.button_is_checked = True 
        
        self.setWindowTitle("My App")
        # self.windowTitleChanged.connect(self.the_window_title_changed)
       
        self.button = QPushButton("Press Me!")
        # self.button.clicked.connect(self.the_button_was_clicked)
        # self.button.clicked.connect(self.the_button_was_toggled)
        self.button.setChecked(self.button_is_checked)

        self.group = MyGroupBox()

        self.layout = QVBoxLayout()
        for _ in range(3):
            btn = QPushButton(str(_))
            self.layout.addWidget(btn)  
        
        for _ in range(10):
            _ = MyGroupBox()  
            self.layout.addWidget(_)    

        container = QWidget()
        container.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()