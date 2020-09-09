# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 11:25:26 2020

@author: sanja_s
"""

import tkinter as tk
from tkinter import filedialog as fd
import pandas as pd
#import PyQt4

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Open GZ files"
        self.hi_there["command"] = self.open_gz
        self.hi_there.pack(side="top")
        
#        self.Button_print = tk.Button(self)
#        self.Button_print['text'] = 'print'
#        self.Button_print["command"] = self.print_data
#        self.Button_print.pack(side="top")
        
#        self.QUIT = tk.Button(self, text="QUIT", fg="red",
#                                            command=root.destroy)
#        self.QUIT.pack(side="bottom")

    def open_gz(self):
        
        
        self.gz_files = fd.askopenfiles(title='Открыть GZ файл', 
                                       filetypes=[('GZ files', '*.gz'), ('CSV files', '*.csv')], initialdir='')
        
        # Считывание названия всех колонок
        name_column = pd.read_csv(self.gz_files[0], delim_whitespace='\t', nrows=0)
        print(name_column)
        
        
#       print(self.csv_file)
#       print(self.b)
#        for file_ in self.gz_files:
#            print(file_)
#            df = pd.read_csv(file_, encoding="cp1251")        
#        columns_csv = pd.read_csv(self.csv_file, header=0)
#        print(df.info)        

root = tk.Tk()
app = Application(master=root)
app.mainloop()
