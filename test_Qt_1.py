from main import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, QtWidgets,
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication, QWidget, QPushButton, QMessageBox, QInputDialog, QFileDialog
from PyQt5.QtGui import QIcon, QFont
from PyQt5 import uic


class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()
    sys.exit(app.exec_())