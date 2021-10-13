import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QComboBox, QHBoxLayout, QGroupBox, QDialog, QVBoxLayout, \
    QGridLayout, QLabel, QFileDialog, QSizePolicy, QMainWindow, QLineEdit
import read_csv_2
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import time
import pandas as pd

class Window_Shift(QWidget):

    def __init__(self):
        super(Window_Shift, self).__init__()
        self.setup_UI()

    def setup_UI(self):

        # self.data = [random.randint(0, 10) for _ in range(9)]

        self.setWindowTitle('Создание смещения')

        self.button = QPushButton('Создать смещение')
        self.button.clicked.connect(self.plot)

        list_dot = ['100', '1000', '4000', '8000']
        self.combobox_dot = QComboBox()
        self.combobox_dot.addItems(list_dot)
        self.combobox_dot.setCurrentIndex(2)
        print('4')

        self.read_file()

        self.value = QLineEdit()  # для того чтобы писать сюда кол-во отображаемых точек
        # # и от сюда вставлять в label_step
        # print(str(len(self.df.df.index) / int(self.combobox_dot.currentText())))
        # self.value.setText(str(self.df.df.index/int(self.combobox_dot.currentText())))
        print('5')
        self.label_UP = QLabel(self)
        self.label_UP.setText(str(len(self.data_up.df.index)))

        self.label_Down = QLabel(self)
        self.label_Down.setText(str(len(self.data_down.df.index)))

        # self.figure = plt.figure()
        # self.canvas = FigureCanvas(self.figure)
        # self.toolbar = NavigationToolbar(self.canvas, self)

        print('6')
        self.horizontalGroupBox = QGroupBox()
        grid = QGridLayout()
        grid.addWidget(QLabel('Число усредняемых отсчетов:'), 0, 0)
        grid.addWidget(QLabel('Число данных при движение Вверх: '), 1, 0)
        grid.addWidget(QLabel('Число данных при движение Вниз: '), 2, 0)
        grid.addWidget(self.combobox_dot, 0, 1)
        grid.addWidget(self.label_UP, 1, 1)
        grid.addWidget(self.label_Down, 2, 1)
        grid.addWidget(self.button, 3, 1)
        self.horizontalGroupBox.setLayout(grid)
        print('7')
        self.horizontalGroupBox_2 = QGroupBox()
        # grid_2 = QVBoxLayout()
        # grid_2.addWidget(self.canvas)
        # grid_2.addWidget(self.toolbar)
        # self.horizontalGroupBox_2.setLayout(grid_2)

        windowLayout = QHBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        windowLayout.addWidget(self.horizontalGroupBox_2)
        self.setLayout(windowLayout)
        print('8')

        # self.step_point = int(len(self.df.df.index) / int(self.combobox_dot.currentText()))

        # self.plot()


        print('9')

    def read_file(self):

        self.data_up = read_csv_2.Window('Открыть CSV файлы для Смещения. Движение вверх')

        # print(self.data_up.df.info)
        # print(self.data_up.info())

        self.data_down = read_csv_2.Window('Открыть CSV файлы для Смещения. Движение вниз')

        # print(self.data_up['time'][::])

    def shift_oz(self):

        # print(self.combobox_dot.currentText())

        print(11111)

        # print(self.data_up.df.info())

        time_start = time.time()

        print(int(self.combobox_dot.currentText()))

        # 33-34 секунды на работе занимает выполнение этой строки
        # self.data_up.df['filter_GSM_A_up'] = self.moving_average_np(self.data_up.df['ГСМ-А.Текущее положение'],
        #                                                             # int(self.combobox_dot.currentText()))
        #                                                             4000)
        # # 62 секунды на работе занимает выполнение этой строки
        self.data_up.df['filter_GSM_A_up'] = self.moving_average_pd(self.data_up.df['ГСМ-А.Текущее положение'],
                                                                    # int(self.combobox_dot.currentText()))
                                                                    4000)

        print('shift_oz', 2222, time.time()-time_start)

        # self.data_up.df['filter_down_A'] = self.moving_average(self.data_down.df['ГСМ-А.Текущее положение'],
        #                                                 int(self.combobox_dot.currentText()))

        print(3333)

        # усреднение значение ГСМ
        # print(self.data_up.df.info())
        # print(self.data_down.df.info())

        print(2222)
        # print(self.data_up[self.data_up.GSM_A_column][1::10])
        # data_up_a = self.movingaverage(np.array(self.data_up[self.data_up.GSM_A_column].iloc[:, 2]), int(self.combobox_dot.currentText()))
        # print(data_up_a.head)
        # data_up_b = movingaverage(np.array(data_up[0].iloc[:, 3]), iterat)

        # number_TG = data_up[2]
        #
        # time_read = float(data_up[1]) + float(data_down[1])

        # создание списка tablenumber из значений GSM от 0 до 320
        # tablenumber = [n4 for n4 in range(321)]

        # скользящее среднее
        # iterat = int(combo_iteration.get())

    def moving_average_pd(self, series, n):           #series,  n - кол-во усреднений

        # print(type(series))
        print(series.size)
        # print(series.__len__)
        print('2')
        # print(series[0:n + 0].mean())

        moving_average_list = pd.Series()

        print('3')
        for _ in series.index:
            print('_', _, 'n', n)
            b = int(series.size) - n + 1
            print(b)
            if _ < n // 2:
                moving_average_list.append(series[_:n + _].mean())
            elif n // 2 <= _ <= b:
                moving_average_list.append(series[_ - n // 2:_ + n // 2 + 1].mean())
            else:
                moving_average_list.append(series[-n:].mean())
            print(moving_average_list.size)

        print(self.moving_average_list.head())
        return self.moving_average_list

    def moving_average_np(self, series, n):           #series,  n - кол-во усреднений

        # преобразование dframe (pandas) в np (numpy)

        self.moving_average_list = []
        for zz in range(len(series)):
            b = len(series) - n + 1
            if zz < n // 2:
                self.moving_average_list.append(np.average(series[zz:n + zz]))
            elif n // 2 <= zz <= b:
                self.moving_average_list.append(np.average(series[zz - n // 2:zz + n // 2 + 1]))
            else:
                self.moving_average_list.append(np.average(series[-n:]))
        return self.moving_average_list

    def plot(self):

        self.shift_oz()

        print('plot _1')
        fig = plt.figure(figsize=(6, 6))
        fig.canvas.set_window_title('Скачки/Шаги')
        ax = fig.add_subplot(111, facecolor='#FFFFCC')
        print('plot _2')
        point_step = 10
        # point = point_f//2
        line, = ax.plot(self.data_up.df['ГСМ-А.Текущее положение'][1::point_step],
                        self.data_up.df['ОЗ ГСМ-А.Текущее положение'][1::point_step], lw=2, color='b',
                        label="ГСМ-А")
        # line_1, = ax.plot(self.data_down.df['ГСМ-Б.Текущее положение'][1::point_step],
        #                   self.data_down.df['ОЗ ГСМ-Б.Текущее положение'][1::point_step], lw=2, color='g',
        #                   label='ГСМ-Б')
        line_filtr, = ax.plot(self.data_up.df['filter_GSM_A_up'][1::point_step],
                              self.data_up.df['ОЗ ГСМ-А.Текущее положение'][1::point_step], lw=2, color='r',
                              label="ГСМ-А.Фильтр")
        # line_1_filtr, = ax.plot(self.data_up.df['filter_down_A'][1::point_step],
        #                       self.data_up.df['ОЗ ГСМ-А.Текущее положение'][1::point_step], lw=2, color='r',
        #                       label="ГСМ-А.Фильтр")

        # fig.suptitle('vvxc', fontsize='large')
        ax.set_xlabel('ГСМ, мм')
        ax.set_ylabel('ОЗ, мм')
        ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
        plt.title('Движение ГСМ-А. n=' + str(self.combobox_dot.currentText()), fontsize='large')
        print('plot _3')
        ax.legend((line, line_filtr), ('Вверх.Оригин.', 'Фильтр.'))
        print('plot _4')
        plt.show()

    def pass_S(self):

        start_program = time.time()

        data_up_a = movingaverage(np.array(data_up[0].iloc[:, 2]), iterat)
        # print(data_up.head)
        data_up_b = movingaverage(np.array(data_up[0].iloc[:, 3]), iterat)
        data_up[0]['ОЗ ГСМ-А.Текущее положение. Усредненное'] = data_up_a[0]
        data_up[0]['ОЗ ГСМ-Б.Текущее положение. Усредненное'] = data_up_b[0]

        data_down_a = movingaverage(np.array(data_down[0].iloc[:, 2]), iterat)
        data_down_b = movingaverage(np.array(data_down[0].iloc[:, 3]), iterat)
        data_down[0]['ОЗ ГСМ-А.Текущее положение. Усредненное'] = data_down_a[0]
        data_down[0]['ОЗ ГСМ-Б.Текущее положение. Усредненное'] = data_down_b[0]

        time_average = time.time() - start_program

        print('Усреднение данных: %.2f cек' % time_average)

        with open('log.txt', 'a') as csv_out:
            csv_out.write('Усреднение данных: %.2f cек\n' % time_average)

        time_all = time.time()

        # функция рисования графиков движение (ВВЕРХ-ВНИЗ)
        def draw(name, GSM_up, OZ_up, OZ_up_filtr, GSM_down, OZ_down, OZ_down_filtr):
            fig, ax = plt.subplots()
            point_f = 100
            point = point_f // 2
            if name == 'Движение ГСМ-А. n=' or name == 'Движение ГСМ-Б. n=':
                line, = ax.plot(GSM_up[::point], OZ_up[::point], lw=2, color='b', label="ГСМ-А.Оригин")  # ГСМ-А
                line1, = ax.plot(GSM_up[::point_f], OZ_up_filtr[::point_f], lw=2, color='r', label="ГСМ-Б")  # ГСМ-Б
                line2, = ax.plot(GSM_down[::point], OZ_down[::point], lw=2, color='g', label="ГСМ-Б")  # ГСМ-Б
                line3, = ax.plot(GSM_down[::point_f], OZ_down_filtr[::point_f], lw=2, color='r', label="ГСМ-Б")  # ГСМ-Б
            else:
                line, = ax.plot(GSM_up, OZ_up_filtr, 'ro', markersize=2, color='b', label="Вверх")  # ГСМ-А
                line1, = ax.plot(GSM_up, OZ_down_filtr, 'ro', markersize=2, color='g', label="Вниз")  # ГСМ-Б
            fig.suptitle(name + str(iterat), fontsize='large')
            ax.set_xlabel('ГСМ, мм')
            ax.set_ylabel('ОЗ, мм')
            ax.grid(linestyle='--', linewidth=0.5, alpha=.85)

            if name == 'Движение ГСМ-А. n=':
                ax.legend((line, line1, line2, line3), ('Вверх.Оригин.', 'Вниз.Оригин.', 'Вверх.Фильтр',
                                                        'Вниз.Фильтр'))
            elif name == 'Движение ГСМ-Б. n=':
                ax.legend((line, line1, line2, line3), ('Вверх.Оригин.', 'Вниз.Оригин.', 'Вверх.Фильтр',
                                                        'Вниз.Фильтр'))
            else:
                ax.legend((line, line1), ('Вверх.', 'Вниз.'))

        draw1 = draw('Движение ГСМ-А. n=', data_up[0].iloc[:, 0], data_up[0].iloc[:, 2], data_up[0].iloc[:, 4],
                     data_down[0].iloc[:, 0], data_down[0].iloc[:, 2], data_down[0].iloc[:, 4])
        draw2 = draw('Движение ГСМ-Б. n=', data_up[0].iloc[:, 1], data_up[0].iloc[:, 3], data_up[0].iloc[:, 5],
                     data_down[0].iloc[:, 1], data_down[0].iloc[:, 3], data_down[0].iloc[:, 5])

        # функция создания смещений при движении вверх
        def find_shift_up(GSM_in, OZ_in):
            print('-+' * 15)
            z = 0
            n = 0
            OZ_out = []
            for yy in range(len(GSM_in)):
                if float(GSM_in[z]) >= tablenumber[n]:
                    OZ_out.append(float(OZ_in[z]))
                    n = n + 1
                if n == 321:
                    break
                z = z + 1
            if len(tablenumber) == len(OZ_out):
                print('списки совпадают')
            else:
                OZ_out.append(OZ_out[n - 1])
                print('список дополнен')
            print('up', len(tablenumber), len(OZ_out))
            return OZ_out

        # функция создания смещений при движении вниз
        def find_shift_down(GSM_in, OZ_in):
            print('-+' * 15)
            z = 0
            n = 320
            OZ_out = []
            for yy in range(len(GSM_in)):
                if float(GSM_in[z]) <= tablenumber[n]:
                    OZ_out.append(float(OZ_in[z]))
                    n = n - 1
                if n == 0:
                    break
                z = z + 1
            if len(tablenumber) == len(OZ_out):
                print('списки совпадают')
            else:
                OZ_out.append(OZ_out[n - 1])
                print('список дополнен')
            OZ_out.reverse()
            print('down', len(tablenumber), len(OZ_out))
            return OZ_out

        OZ_A_final_up = find_shift_up(np.array(data_up[0].iloc[:, 0]), np.array(data_up[0].iloc[:, 4]))
        OZ_B_final_up = find_shift_up(np.array(data_up[0].iloc[:, 1]), np.array(data_up[0].iloc[:, 5]))
        OZ_A_final_down = find_shift_down(np.array(data_down[0].iloc[:, 0]), np.array(data_down[0].iloc[:, 4]))
        OZ_B_final_down = find_shift_down(np.array(data_down[0].iloc[:, 1]), np.array(data_down[0].iloc[:, 5]))

        draw3 = draw('Отсечка. ГСМ-А. n=', tablenumber, tablenumber, OZ_A_final_up,
                     tablenumber, tablenumber, OZ_A_final_down)
        draw4 = draw('Отсечка. ГСМ-Б. n=', tablenumber, tablenumber, OZ_B_final_up,
                     tablenumber, tablenumber, OZ_B_final_down)

        # функция создания УСТАВОК для Unity (ОТСЕЧКИ)
        def otsechka(OZ_up_in, OZ_down_in):
            OZ_otsechka = []
            i = 0
            for zz in range(len(OZ_up_in)):
                OZ_otsechka.append('%.3f' % ((OZ_up_in[i] + OZ_down_in[i]) / 2))
                i = i + 1
            return OZ_otsechka

        OZ_A_otsechka = otsechka(OZ_A_final_up, OZ_A_final_down)
        OZ_B_otsechka = otsechka(OZ_B_final_up, OZ_B_final_down)

        # запись в файл CSV
        out_file = 'out_merge_4.csv'
        with open(out_file, 'w', newline='') as csv_out:
            w = csv.writer(csv_out, delimiter=';')
            w.writerow(('i', 'ОЗ ГСМ-А.Вверх', 'ОЗ ГСМ-А.Вниз', 'ОЗ ГСМ-А.Отсечка', 'ОЗ ГСМ-Б.Вниз', 'ОЗ ГСМ-Б.Вниз',
                        'ОЗ ГСМ-Б.Отсечка'))
        i = 0
        for zz in range(len(tablenumber)):
            with open(out_file, 'a', newline='') as csv_out:
                w = csv.writer(csv_out, delimiter=';')
                w.writerow((tablenumber[i], OZ_A_final_up[i], OZ_A_final_down[i], OZ_A_otsechka[i], OZ_B_final_up[i],
                            OZ_B_final_down[i], OZ_B_otsechka[i]))
            i = i + 1

        # функция записи в файл TXT для UNITY
        def write_UNITY(out_file, tablenumber, OZ_otsechka):
            with open(out_file, 'w', newline='') as csv_out:
                if out_file == 'gsm_tg1_a.txt':
                    csv_out.write('Ust_shift1A_def	%kw16000	ARRAY[0..340] OF REAL\t\t(')
                else:
                    csv_out.write('Ust_shift1B_def	%kw16682	ARRAY[0..340] OF REAL\t\t(')
                fi = 0
                for zz in range(len(tablenumber)):
                    if zz == 320:
                        csv_out.write('[' + str(tablenumber[fi]) + ']:=' + OZ_otsechka[fi])
                    else:
                        csv_out.write('[' + str(tablenumber[fi]) + ']:=' + OZ_otsechka[fi] + ',')
                    fi = fi + 1
                csv_out.write(')\n')

        if number_TG == 1:
            write_UNITY('gsm_tg1_a.txt', tablenumber, OZ_A_otsechka)
            write_UNITY('gsm_tg1_b.txt', tablenumber, OZ_B_otsechka)
        else:
            write_UNITY('gsm_tg2_a.txt', tablenumber, OZ_A_otsechka)
            write_UNITY('gsm_tg2_b.txt', tablenumber, OZ_B_otsechka)

        time_all = time.time() - time_all
        time_all = float(time_all) + float(time_average) + float(time_read)

        print('Общее время Смещения: %.2f cек' % time_all)

        with open(log_name, 'a', newline='') as csv_out:
            csv_out.write('Общее время Смещения: %.2f cек\n' % time_all)
            csv_out.write('-' * 20 + '\n')

        plt.show()


def main():
    app = QApplication(sys.argv)
    ex = Window_Shift()
    ex.show()
    try:
        sys.exit(app.exec_())
    except ValueError:
        print("Каряво закрыли")


if __name__ == '__main__':
    main()
