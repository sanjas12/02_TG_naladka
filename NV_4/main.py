from nv_package.model_NV import ModelNV as ModelNV
from nv_package.gui_main import MainWindow as MainWindow
from nv_package.gui_imitator import BasePlot as BasePlot
import os, sys
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    model = ModelNV()
    plot = BasePlot()
    plot.start()
    main_window = MainWindow(model.data_for_gui)
    main_window.show()
    try:
        sys.exit(app.exec())
    except:
        print("Пока")


if __name__ == '__main__':
    main()