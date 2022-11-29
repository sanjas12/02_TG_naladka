from nv_package.model_NV import ModelNV as ModelNV
from nv_package.main_gui import MainWindow as MainWindow
import os, sys
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    model = ModelNV()
    ex = MainWindow(model.data_for_gui)
    ex.show()
    try:
        sys.exit(app.exec())
    except:
        print("Пока")


if __name__ == '__main__':
    main()