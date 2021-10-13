# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 11:13:06 2020

@author: sanja_s
"""

from PyQt4 import QtCore, QtGui, uic
#import pandas as pd

def main():
    import sys
    app = QtGui.QApplication(sys.argv)
    window = uic.loadUi("9_qt4.ui")
    QtCore.QObject.connect(window.pushButton_2, QtCore.SIGNAL("clicked()"),
                               QtGui.qApp.quit)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    print('f')
    main()
