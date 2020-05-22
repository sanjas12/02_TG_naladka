import sys
from PyQt5.QtWidgets import QApplication

import TG_pyQt_04 as my_GUI

def main():
    app = QApplication(sys.argv)
    ex = my_GUI.Window_Main()
    ex.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Каряво закрыли")

if __name__ == '__main__':
    main()
