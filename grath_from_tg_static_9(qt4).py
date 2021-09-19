# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 11:13:06 2020

@author: sanja_s
"""

from PyQt4 import QtCore, QtGui
import pandas as pd
import gzip


class MyWindow(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.btn_open = QtGui.QPushButton("&Open GZ files")
        self.btn_close = QtGui.QPushButton("&Close") # & - для быстрого доступа через Alt
        self.columns = QtGui.QListWidget()

        self.vbox = QtGui.QVBoxLayout()
        self.vbox.addWidget(self.btn_open)
        self.vbox.addWidget(self.btn_close)
        self.vbox.addWidget(self.columns)
        self.setLayout(self.vbox)
        
        self.btn_open.clicked.connect(self.open_gz)
        self.connect(self.btn_close, QtCore.SIGNAL("clicked()"),
                               QtGui.qApp.quit)

        self.setWindowTitle("File Dialog")
        self.resize(300, 70)


        # Определение кодировки 
    def detect_encoding_delimiter(self, filename):
        if self.filename_extension():
            with open(filename, 'rb') as f:
                raw_data = f.read(20000)
                self.encoding = chardet.detect(raw_data)['encoding']
            # и разделителя csv
            with open(filename, 'r', encoding=self.encoding) as f:
                print(f.readline(100))
                if f.readline(100).count(';'):
                    self.delimiter = ';'
                else:
                    self.delimiter = '\t'
            # заполняем колонку ось columns (Выбирай параметр)
        else:
            # Определение кодировки
            with gzip.open(self.files[0], 'rb') as f:
                raw_data = f.read(20000)
                self.encoding = chardet.detect(raw_data)['encoding']
            # и разделителя gz
            with gzip.open(self.files[0], 'r') as f:
                if f.readline(100).decode(self.encoding).count(';'):
                    self.delimiter = ';'
                else:
                    self.delimiter = '\t'
    return self.encoding, self.delimiter


    def open_gz(self):
        self.columns.clear()
        # self.axe_y.clear()
        # self.axe_x.clear()

        fname = QtGui.QFileDialog.getOpenFileNames(self, 'Open file', '*.gz')
#        print(fname[0])

        # self.name_column = pd.read_csv(fname[0], encoding="cp1251", delim_whitespace=True, nrows=0)
        
        
        self.df = pd.read_csv(fname[0], encoding="cp1251", sep='\t')
#        self.df = pd.read_csv(fname[0])
#        print(self.df.columns)

        # заполняем колонку ось columns (Выбирай параметр)
        for i, _ in enumerate(self.df.columns):
            print(i, _)
            self.columns.insertItem(i, _)

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
    import sys
    app = QtGui.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
