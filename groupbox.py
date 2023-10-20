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
            self.qlist = QListWidget()
            self.btn = QPushButton('Add to')
            # btn_secondary_axe_add.clicked.connect(lambda: self.add_to_qlist(self.qlist_secondary_axe))
            # btn_secondary_axe_remove = QPushButton('Remove from Y2')
            # btn_secondary_axe_remove.clicked.connect(lambda: self.remove_qlist(self.qlist_secondary_axe))
            
            self.lay = QVBoxLayout()
            self.lay.addWidget(self.qlist)
            self.lay.addWidget(self.btn)
            # secondary_axe_layout.addWidget(btn_secondary_axe_remove)
            
            self.gb = QGroupBox("Вспомогательная Ось")
            self.gb.setLayout(self.lay)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
       
        self.my_group = MyGroupBox()
        print(self.my_group)

        self.layout = QVBoxLayout()
        for _ in range(3):
            btn = QPushButton(str(_))
            self.layout.addWidget(btn)  
        
        self.layout.addWidget(self.group)
        # for _ in range(10):
        #     _ = MyGroupBox()  
        #     self.layout.addWidget(_)    

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()