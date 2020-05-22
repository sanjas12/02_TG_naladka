import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
import sys

class Window(QWidget):

    def __init__(self, namedialog):
        super().__init__()
        self.GSM_A_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
        self.GSM_B_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
        self.zadanie_column = 'Значение развертки. Положение ГСМ'  # Значение развертки. Положение ГСМ
        self.Time_column = 'миллисекунды'  # время
        self.OZ_A_column = 'ОЗ ГСМ-А.Текущее положение'  # ОЗ ГСМ-А.Текущее положение
        self.OZ_B_column = 'ОЗ ГСМ-Б.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение

        fields = [self.GSM_A_column, self.GSM_B_column, self.zadanie_column, self.Time_column, self.OZ_A_column,
                  self.OZ_B_column]

        files, _filter = QFileDialog.getOpenFileNames(self, namedialog, ' ', '*.csv')
        list_ = []

        for file in files:
            # print(file)
            df = pd.read_csv(open(file, 'r'), header=0, delimiter=';', usecols=fields)
            list_.append(df)

        self.df = pd.concat(list_)
        self.time_c = 'time'
        time_data = []
        summa = 0
        for z in range(len(self.df.index)):
            time_data.append(float('%.2f' % summa))
            summa = summa + 0.01

        self.df[self.time_c] = time_data

        print(self.df.info())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window('Открыть файлы')
    # print(ex.df.info())
    sys.exit(app.exec_())
