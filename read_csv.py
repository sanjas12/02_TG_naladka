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

        fields = [self.GSM_A_column, self.GSM_B_column, self.zadanie_column, self.Time_column]

        files, _filter = QFileDialog.getOpenFileName(self, namedialog, 'csv', '*.csv')


        if files:
            self.df = pd.read_csv(open(files, 'r'), header=0, delimiter=';', usecols=fields)

            self.time = 'time'

            time_data = []
            summa = 0
            for z in range(len(self.df.index)):
                time_data.append(float('%.2f' % summa))
                summa = summa + 0.01

            self.df[self.time] = time_data


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Window('Открыть файл с "шагами"')
    print(ex.df.info())
    sys.exit(app.exec_())
