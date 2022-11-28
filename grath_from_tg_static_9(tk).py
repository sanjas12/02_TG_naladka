# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 11:25:26 2020

@author: sanja_s
"""

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pandas as pd


class Filedialogdemo(QWidget):
    def __init__(self, parent=None):
        super(Filedialogdemo, self).__init__(parent)

        layout = QVBoxLayout()
        self.btn1 = QPushButton("Open GZ files")
        self.btn1.clicked.connect(self.open_gz)
        layout.addWidget(self.btn1)

        self.setLayout(layout)
        self.setWindowTitle("File Dialog")

    def open_gz(self):
        # self.columns.clear()
        # self.axe_y.clear()
        # self.axe_x.clear()

        # Считывание названия всех колонок
        # self.files = QFileDialog.getOpenFileNames(self, 'Open GZ files', '*.gz')
        fname = QFileDialog.getOpenFileNames(self, 'Open file', '*.gz')
        print(fname[0])

        # self.name_column = pd.read_csv(fname[0], encoding="cp1251", delim_whitespace=True, nrows=0)
        # self.columns = pd.read_csv(fname[0], encoding="utf-16", sep='\t', nrows=1)
        self.columns = pd.read_csv(fname[0], encoding="mac_cyrillic", sep='\t', nrows=1)
        # self.columns = pd.read_csv(fname[0], encoding="cp1251", sep='\t', nrows=1)

        # print(len(self.columns))
        # print(self.columns)

        # заполняем колонку ось columns (Выбирай параметр)
        for i, _ in enumerate(self.columns):
            print(i, _)
            # self.columns.insertItem(i, _)

        # dlg = QFileDialog()
        # dlg.setFileMode(QFileDialog.AnyFile)
        # dlg.setFilter("Text files (*.txt)")
        # filenames = QStringList()
        # if dlg.exec_():
        #     filenames = dlg.selectedFiles()
        # f = open(filenames[0], 'r')
        # with f:
        #     data = f.read()
        # self.contents.setText(data)





        # self.gz_files = fd.askopenfiles(title='Открыть GZ файл',
        #                                filetypes=[('GZ files', '*.gz'), ('CSV files', '*.csv')], initialdir='')
        # print(self.gz_files[0])
        #
        # # Считывание названия всех колонок
        # name_column = pd.read_csv(self.gz_files[0], delim_whitespace='\t', nrows=0)
        # print(name_column)


# print(self.csv_file)
#       print(self.b)
#        for file_ in self.gz_files:
#            print(file_)
#            df = pd.read_csv(file_, encoding="cp1251")        
#        columns_csv = pd.read_csv(self.csv_file, header=0)
#        print(df.info)        

def main():
    app = QApplication(sys.argv)
    ex = Filedialogdemo()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
