import model_NV
import main_gui
import os, sys
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    data_for_gui = model_NV.ModelNV()
    ex = main_gui.MainWindow(data_for_gui)
    ex.show()
    try:
        sys.exit(app.exec())
    except:
        print("Пока")


if __name__ == '__main__':
    main()