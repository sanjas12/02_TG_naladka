"""
Created on Tue Aug 18 11:25:26 2020

@author: sanja_s
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import time
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import SpanSelector
from tkinter.filedialog import *  # для askopenfilename
from tkinter.ttk import *  # для combobox
import csv
from tkinter import filedialog as fd
import pandas as pd
import os
from tkinter import *

# from memory_profiler import profile

# "Скачки/Шаги"
# @profile
def stepper(event):
    GSM_A_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
    GSM_B_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
    Zadanie_column = 'Значение развертки. Положение ГСМ'  # Значение развертки. Положение ГСМ
    time_column = 'миллисекунды'  # время

    fields = [GSM_A_column, GSM_B_column, Zadanie_column, time_column]

    opened_csv_files = fd.askopenfiles(title='Открыть CSV файл с ШАГАМИ', filetypes=[('CSV files', '*.csv'), ],
                                       initialdir='')

    print(opened_csv_files)

    # определение номера канала из названия файла
    name_ch = str(opened_csv_files)
    name_temp = name_ch = name_ch.split('/')
    if int(name_ch[len(name_ch) - 1][3]) == 1:
        name_ch = '1 channel'
    else:
        name_ch = '2 channel'

    # определение номера ТГ из названия файла
    name_TG = int(name_temp[len(name_temp) - 1][2])

    time_data = []

    for file_ in opened_csv_files:
        print(file_)
        df = pd.read_csv(file_, header=0, delimiter=';', usecols=fields)

    # поиск количества строк
    num_rows = len(df.index)

    # создание пустого DataFrames
    df_1 = pd.DataFrame(None, index=range(num_rows), columns=['time'])
    # print(df_1.shape)

    summa = 0
    for z in range(num_rows):
        time_data.append(float('%.2f' % summa))
        summa = summa + 0.01

    # print(df.shape)
    # print(len(time_data))
    # print(time_data)
    # print(type(time_data[3]))

    # отрисовка окна для графиков
    point_f = 10

    print('точек отрисовки:', int(len(time_data) / point_f))
    #    print(f'точек отрисовки: {int(len(time_data)/point_f)}')

    fig = plt.figure(figsize=(6, 6))
    fig.canvas.set_window_title('Скачки/Шаги')
    if matplotlib.__version__ == '1.4.3':
        ax = fig.add_subplot(211, ) 
    else:
        ax = fig.add_subplot(211, facecolor='#FFFFCC')
    line, = ax.plot(time_data[1::point_f], df[GSM_A_column][1::point_f],
                    linewidth=1, color='b', label="GSM-A")  # ГСМ-А
    line1, = ax.plot(time_data[1::point_f], df[GSM_B_column][1::point_f],
                     linewidth=1, color='r', label="GSM-B")  # ГСМ-Б
    line2, = ax.plot(time_data[1::point_f], df[Zadanie_column][1::point_f],
                     lw=1, color='black', label="Zadanie")  # Задание

    ax.set_xlabel('Time, c')
    ax.set_ylabel('GSM, mm')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
    plt.title('TG-' + str(name_TG) + ', ' + str(name_ch), fontsize='large')

    # отрисовка легенды
    ax.legend((line, line1, line2), ('GSM-A', 'GSM-B', 'Zadanie'))

    # отрисовка 2 графика
    if matplotlib.__version__ == '1.4.3':
        ax2 = fig.add_subplot(212, )
    else:
        ax2 = fig.add_subplot(212, facecolor='#FFFFCC')

    line02, = ax2.plot(time_data[1::point_f], df[GSM_A_column][1::point_f], lw=1, color='b', label="GSM-A")  # ГСМ-А
    line12, = ax2.plot(time_data[1::point_f], df[GSM_B_column][1::point_f], lw=1, color='r', label="GSM-B")  # ГСМ-Б
    line22, = ax2.plot(time_data[1::point_f], df[Zadanie_column][1::point_f], lw=1, color='black',
                       label="Zadanie")  # задание
    ax2.set_xlabel('Time, c')
    ax2.set_ylabel('GSM, mm')
    ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # функция выделения_старая
    def onselect(xmin, xmax):
        print('*' * 20)
        #        print(f'от курсора: {xmin}, {xmax}')
        print('от курсора:', xmin, xmax)
        indmin, indmax = np.searchsorted(time_data,
                                        float(xmin), float(xmax))  # получение минимального и максимального
        print('min_max', indmin, indmax)
        # indmax = min(len(time_data) - 1, indmax)
        print(indmin, indmax)

        thisx = time_data[indmin:indmax]  # новые данные для значений "время"
        thisx_new = []  # формирование нового массива значений "время"
        for zz in range(len(thisx)):
            thisx_new.append(zz * 0.01)
        thisy0 = np.array(df[GSM_A_column][indmin:indmax])  # новые данные для значений "ГСМ-А")
        thisy1 = np.array(df[GSM_B_column][indmin:indmax])  # новые данные для значений "ГСМ-Б"
        thisy2 = np.array(df[Zadanie_column][indmin:indmax])  # новые данные для значений "Задание"
        line02.set_data(thisx_new, thisy0)  # перерисовка графика "ГСМ-А"
        line12.set_data(thisx_new, thisy1)  # перерисовка графика "ГСМ-Б"
        line22.set_data(thisx_new, thisy2)  # перерисовка графика Задание
        print(thisx_new[0], thisx_new[-1])
        ax2.set_xlim(thisx_new[0], thisx_new[-1])  # перерисовка масштаба осей X
        ax2.set_ylim(thisy2.min() - 1, thisy2.max() + 1)  # перерисовка масштаба осей Y от Задания
        print('*' * 20)
        fig.canvas.draw()

    # set useblit True on gtkagg for enhanced performance
    span = SpanSelector(ax, onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))

    # функция - отображения графиков 1 чек-бокс
    def func(label):
        if label == 'GSM-A':
            line.set_visible(not line.get_visible())
        elif label == 'GSM-B':
            line1.set_visible(not line1.get_visible())
        elif label == 'Zadanie':
            line2.set_visible(not line2.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 1
    rax = plt.axes([0.0, 0.5, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
    check = CheckButtons(rax, ('GSM-A', 'GSM-B', 'Zadanie'), (True, True, True))
    check.on_clicked(func)

    # функция - отображения графиков 2 чек-бокс
    def func_2(label):
        if label == 'GSM-A':
            line02.set_visible(not line02.get_visible())
        elif label == 'GSM-B':
            line12.set_visible(not line12.get_visible())
        elif label == 'Zadanie':
            line22.set_visible(not line22.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 2
    rax_2 = plt.axes([0.0, 0.01, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
    check_2 = CheckButtons(rax_2, ('GSM-A', 'GSM-B', 'Zadanie'), (True, True, True))
    check_2.on_clicked(func_2)

    plt.show()


# "Скорости"
# @profile
def velosity(event):
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('Программа Скорости запущена:' + time.strftime('%Y_%m_%d_%H:%M:%S') + '\n')

    def openCSV(event, name_direction):
        op = askopenfiles(title=name_direction, filetypes=[('CSV files', '*.csv'), ], initialdir='')
        return op

    op = openCSV(event, 'Открыть CSV файл')

    start_program = time.time()
    count = 0

    # функция поиска номера нужной колонки
    def find_column(name_column):
        in_file_for_header = str(op[0])
        count = in_file_for_header.split("'")
        in_file_for_header = count[1]
        count = in_file_for_header.split("'")
        in_file_for_header = count[0]
        infile = open(in_file_for_header, 'r')
        for row in csv.reader(infile):
            row = str(row)
            count = row.split(";")
            i = 0
            n = 1
            while count[i] != name_column and n < len(count):
                i = i + 1
                n = n + 1
            else:
                break
        if n == len(count):
            n = 0
            #            print(f'Колонка {name_column} не найдена. !!!!!!!!!!')
            print('Колонка ', name_column, ' не найдена. !!!!!!!!!!')
        else:
            #            print(f'{name_column} - колонка номер : {n}')
            print(name_column, ' - колонка номер :', n)
        infile.close()
        return n

    # поиск номеров колонок из файла csv
    print('*' * 50)
    GSM_A_column = find_column('ГСМ-А.Текущее положение') - 1  # ГСМ-А.Текущее положение
    GSM_B_column = find_column('ГСМ-Б.Текущее положение') - 1  # ГСМ-Б.Текущее положение
    time_column = find_column('time') - 1  # время

    # функция создания массива данных из оригинальных файлов
    def read_data_from_file(name_file_CSV, GSM_A_column, name_column, GSM_B_column, name_column_2,
                            time_column, name_column_4):
        number_row_in_all_csv_file = 0
        GSM_A = []
        GSM_B = []
        time = []
        temp_time = []
        # запись данных
        for zz in range(len(name_file_CSV)):  # отсавлена возможность для выбора нескольких файлов
            i = 0
            for row in csv.reader(name_file_CSV[zz], delimiter=';'):
                if i == 0:
                    # пропуск первой строки
                    pass
                else:
                    GSM_A.append(float(row[GSM_A_column - 1]))  # ГСМ-А
                    GSM_B.append(float(row[GSM_B_column - 1]))  # ГСМ-Б
                    if time_column > 0:
                        time.append(float(row[time_column]))  # время из CSV, если есть колонка время
                    else:
                        temp_time.append(float(row[1]))  # время для расчета
                i = i + 1
                number_row_in_all_csv_file += 1

        # создание колонки время, если ее нет
        if time_column > 0:
            print('колонка ВРЕМЯ уже есть')
        else:
            i = 0
            summa = 0
            while i < len(temp_time) - 1:
                if (temp_time[i + 1] - temp_time[i]) != -990:
                    summa = summa +temp_time[i + 1] - temp_time[i]/ 1000
                    time.append(summa)
                else:
                    summa = summa +1 + (temp_time[i + 1] - temp_time[i]) / 1000
                    time.append(summa)
                i = i + 1
            print('массив ВРЕМЯ cформирована')

        # дописываем значение если разные длина массива время не совпадает
        if len(time) == len(GSM_A):
            pass
        else:
            time.append(time[len(time) - 1])

        print('Колонка\t', ' \t' * 4, '\tДлина массива')
        print(name_column, ' \t' * 2, len(GSM_A))
        print(name_column_2, ' \t' * 2, len(GSM_B))
        print(name_column_4, ' \t' * 2, len(time))
        print('Кол-во строк во всех СSV:', number_row_in_all_csv_file)
        # (0)   1)    2)    3)
        return GSM_A, GSM_B, time, number_row_in_all_csv_file

    data_from_file = read_data_from_file(op, GSM_A_column, 'ГСМ-А.Текущее положение', GSM_B_column,
                                         'ГСМ-Б.Текущее положение', time_column, 'time')

    # отрисовка окна для графиков
    fig = plt.figure(figsize=(6, 6))
    fig.canvas.set_window_title('Скорости')

    # отрисовка 1 графика
    ax = fig.add_subplot(211, facecolor='#FFFFCC')
    line, = ax.plot(data_from_file[2], data_from_file[0], lw=2, color='b', label="GSM-A")  # ГСМ-А
    line1, = ax.plot(data_from_file[2], data_from_file[1], lw=2, color='r', label="GSM-B")  # GSM-B
    ax.set_xlabel('Время, c')
    ax.set_ylabel('ГСМ, мм')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
    plt.title('Скорости')

    # шаг осей
    # ax.xaxis.set_major_locator(ticker.LinearLocator(10))
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(30))

    # отрисовка легенды
    fig.legend((line, line1),('GSM-A', 'GSM-B',))

    # отрисовка 2 графика
    ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
    line02, = ax2.plot(data_from_file[2], data_from_file[0], lw=2, color='b', label="GSM-A")  # ГСМ-А
    line12, = ax2.plot(data_from_file[2], data_from_file[1], lw=2, color='r', label="GSM-B")  # ГСМ-Б
    ax2.set_xlabel('Время, c')
    ax2.set_ylabel('ГСМ, мм')
    ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # функция выделения
    def onselect(xmin, xmax):
        indmin, indmax = np.searchsorted(data_from_file[2], (xmin, xmax))  # получение минимального и максимального
        # элемента для значений  dataf[0] - "время"
        indmax = min(len(data_from_file[2]) - 1, indmax)
        thisx = data_from_file[2][indmin:indmax]  # новые данные для значений "время"
        thisx_new = []  # формирование нового массива значений "время"
        for zz in range(len(thisx)):
            thisx_new.append(zz * 0.01)
        thisy0 = np.array(data_from_file[0][indmin:indmax])  # новые данные для значений "ГСМ-А")
        thisy1 = np.array(data_from_file[1][indmin:indmax])  # новые данные для значений "ГСМ-А"
        # thisy2 = np.array(data_from_file[2][indmin:indmax])             # новые данные для значений "Задание"
        line02.set_data(thisx_new, thisy0)  # перерисовка графика Задание
        line12.set_data(thisx_new, thisy1)  # перерисовка графика Задание
        # line22.set_data(thisx_new, thisy2)               # перерисовка графика Задание
        ax2.set_xlim(thisx_new[0], thisx_new[-1])  # перерисовка масштаба осей X
        ax2.set_ylim(thisy1.min() - 1, thisy1.max() + 1)  # перерисовка масштаба осей Y от Задания
        fig.canvas.draw()

    # set useblit True on gtkagg for enhanced performance
    span = SpanSelector(ax, onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))

    # функция - отображения графиков 1 чек-бокс
    def func(label):
        if label == 'GSM-A':
            line.set_visible(not line.get_visible())
        elif label == 'GSM-B':
            line1.set_visible(not line1.get_visible())
        # elif label == 'Zadanie':
        #     line2.set_visible(not line2.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 1
    rax = plt.axes([0.0, 0.5, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
    check = CheckButtons(rax, ('GSM-A', 'GSM-B'), (True, True))
    check.on_clicked(func)

    # функция - отображения графиков 2 чек-бокс
    def func_2(label):
        if label == 'GSM-A':
            line02.set_visible(not line02.get_visible())
        elif label == 'GSM-B':
            line12.set_visible(not line12.get_visible())
        # elif label == 'Zadanie':
        #     line22.set_visible(not line22.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 2
    rax_2 = plt.axes([0.0, 0.01, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
    check_2 = CheckButtons(rax_2, ('GSM-A', 'GSM-B'), (True, True))
    check_2.on_clicked(func_2)

    with open(log_name, 'a', newline='') as csv_out:
        csv_out.write('время работы функции Скорости: %.2f cек\n' % float(time.time() - start_program))
        csv_out.write('-' * 20 + '\n')
    print('время работы функции ШАГИ: %.2f cек' % float(time.time() - start_program))

    plt.show()


# "Сравнение ОЗ одной стороны"
# @profile
def one_side(event):
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('-' * 20 + '\n')
        csv_out.write('Функция "Сравнение энкод/ОЗ одной стороны" из файла ' + os.path.basename(__file__) +
                      ' запущена на: ' + os.getlogin() + ' в ' +
                      time.strftime('%Y_%m_%d_%H:%M:%S') + '\n')

    OZ_A_name_column = 'ОЗ ГСМ-А.Текущее положение'  # ОЗ ГСМ-А.Текущее положение
    OZ_B_name_column = 'ОЗ ГСМ-Б.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение
    GSM_name_column = 'ГСМ.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение
    OZ_zadanie_A_name_column = 'Задание. Положение ОЗ ГСМ-А'
    OZ_zadanie_B_name_column = 'Задание. Положение ОЗ ГСМ-Б'
    time_column = "миллисекунды"
    mast_chanel = 'Канал ведущий'

    fields = [OZ_A_name_column, OZ_B_name_column, time_column, GSM_name_column, mast_chanel,
              OZ_zadanie_A_name_column, OZ_zadanie_B_name_column]

    # функция чтения данных из csv
    def reading_data(namedirection):
        opened_csv_files = fd.askopenfiles(title=namedirection, filetypes=[('CSV files', '*.csv'), ], initialdir='')

        start_read = time.time()

        # определение номера канала из названия файла
        name_ch = str(opened_csv_files)
        name_temp = name_ch = name_ch.split('/')

        # определение номера ТГ из названия файла
        name_TG = int(name_temp[len(name_temp) - 1][2])

        list_ = []
        time_2 = []
        start_read = time.time()
        for file_ in opened_csv_files:
            df = pd.read_csv(file_, header=0, delimiter=';', usecols=fields)
            list_.append(df)
        data_out = pd.concat(list_)
        # temp_time = df[time_column]
        i = 0
        summa = 0
        while i < len(df[time_column]) - 1:
            if (df[time_column][i + 1] - df[time_column][i]) < 0:
                summa = summa + (1000 + df[time_column][i + 1] - df[time_column][i]) / 1000
                time_2.append('%.2f' % summa)
            else:
                summa = summa + abs(((df[time_column][i + 1] - df[time_column][i])) / 1000)
                time_2.append('%.2f' % summa)
            i = i + 1
        time_2.append(time_2[len(time_2) - 1])

        # print('массив ВРЕМЯ cформирован')

        # data_out = pd.concat(time_2)

        # print(time.time()-start_read)

        # print(data_out.head)

        # print(data_out.shape)

        # print(len(time_2))

        time_read = time.time() - start_read

        print('Загрузка данных: %.2f сек ' % time_read, namedirection[-8:])
        # write = 'Загрузка данных: %.2f сек ' % time_read, namedirection[-8:]

        with open(log_name, 'a', newline='') as csv_out:
            csv_out.write('Загрузка данных: %.2f сек ' % time_read + namedirection[-8:] + '\n')

        return data_out, time_2, name_TG, time_read

    data_1_ch = reading_data('Открыть CSV файл 1 канала')
    data_2_ch = reading_data('Открыть CSV файл 2 канала')

    time_start = time.time()

    # print('1 канал', data_1_ch[0].shape, 'time', len(data_1_ch[1]))
    # print('2 канал', data_2_ch[0].shape, 'time', len(data_2_ch[1]))

    # функция рисования графиков
    def draw(name, name_column, name_zadanie_column, OZ_1, OZ_2):

        fig, ax = plt.subplots()

        fig.canvas.set_window_title('ОЗ Одного канала' + name)

        point_f = 10
        # x                   y
        line, = ax.plot(OZ_1[1][1::point_f], OZ_1[0][name_column][1::point_f], lw=0.5, color='b', label="1 канал тек")
        line1, = ax.plot(OZ_2[1][1::point_f], OZ_2[0][name_column][1::point_f], lw=0.5, color='r', label="2 канал тек")
        # line2, = ax.plot(OZ_1[1][1::point_f], OZ_1[0][name_zadanie_column][1::point_f], lw=0.5, color='black',
        #                  label="1 канал задание")
        # line3, = ax.plot(OZ_2[1][1::point_f], OZ_2[0][name_zadanie_column][1::point_f], lw=0.5, color='green',
        #                   label="2 канал задание")
        fig.suptitle('ТГ:' + name, fontsize='large')
        ax.set_xlabel('Время, c')
        ax.set_ylabel('ОЗ, мм')
        ax.grid(linestyle='--', linewidth=0.5, alpha=.85)

        # для вспомогательной оси
        ax2 = ax.twinx()
        # line4, = ax2.plot(OZ_1[1][1::point_f], OZ_1[0][mast_chanel][1::point_f], lw=2, color='y',
        #                   label='Ведущий 1 канал')
        # line5, = ax2.plot(OZ_2[1][1::point_f], OZ_2[0][mast_chanel][1::point_f], lw=2, color='g',
        #                   label='Ведущий 2 канал')
        ax2.set_ylabel('Ведуший канал')

        ax.legend((line, line1), ('1 канал тек', '2 канал тек'))

        # # функция - отображения графиков 1 чек-бокс
        # def func(label):
        #     if label == '1 канал тек':
        #         line.set_visible(not line.get_visible())
        #     elif label == '2 канал тек':
        #         line1.set_visible(not line1.get_visible())
        #     elif label == 'Ведуший 1 канал':
        #         line4.set_visible(not line4.get_visible())
        #     elif label == 'Ведуший 2 канал':
        #         line5.set_visible(not line5.get_visible())
        #     plt.draw()
        #
        # # работа со списком чек-боксов отображающих графики 1
        # rax = plt.axes([0.0, 0.2, 0.1, 0.08])  # x,y - положение чекбокса ..... х1,y1 - размер окна
        # check = CheckButtons(rax,'1 канал тек', '2 канал тек', 'Ведущий 1 канал', 'Ведущий 2 канал'),
        #                      (True, True, True, True))
        # check.on_clicked(func)

    draw1 = draw((str(data_1_ch[2]) + ', Сторона А'), OZ_A_name_column, OZ_zadanie_A_name_column, data_1_ch, data_2_ch)
    draw2 = draw((str(data_1_ch[2]) + ', Сторона Б'), OZ_B_name_column, OZ_zadanie_B_name_column, data_1_ch, data_2_ch)

    # print(time.time() - time_start)

    time_all = time.time() - time_start + data_1_ch[3] + data_2_ch[3]

    # print(id(time_all))
    # print(sys.getsizeof(data_1_ch))

    print('Общее время: %.2f cек' % time_all)

    with open(log_name, 'a', newline='') as csv_out:
        csv_out.write('Общее время: %.2f cек\n' % time_all)
        csv_out.write('-' * 20 + '\n')

    plt.show()


# Показания "ОЗ Одного канала"
# @profile
def one_channel(event):
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('-' * 20 + '\n')
        csv_out.write('Функция "показания "ОЗ Одного канала" ' + os.path.basename(__file__) + ' запущена на: '
                      + os.getlogin() + ' в ' +
                      time.strftime('%Y_%m_%d_%H:%M:%S') + '\n')

    OZ_A_name_column = 'ОЗ ГСМ-А.Текущее положение'
    OZ_B_name_column = 'ОЗ ГСМ-Б.Текущее положение'
    GSM_name_column = 'ГСМ.Текущее положение'
    time_column = "миллисекунды"
    mast_chanel = 'Канал ведущий'
    OZ_zadanie_A_name_column = 'Задание. Положение ОЗ ГСМ-А'
    OZ_zadanie_B_name_column = 'Задание. Положение ОЗ ГСМ-Б'
    GSM_A_cur = 'ГСМ-А.Текущее положение'
    GSM_B_cur = 'ГСМ-Б.Текущее положение'
    Save_TG = 'Защита ТГ'

    fields = [OZ_A_name_column, OZ_B_name_column, time_column, GSM_name_column, mast_chanel,
              OZ_zadanie_A_name_column, OZ_zadanie_B_name_column, GSM_A_cur, GSM_B_cur, Save_TG]

    # функция чтения данных из csv
    def reading_data(namedirection):

        opened_csv_files = fd.askopenfiles(title=namedirection, filetypes=[('CSV files', '*.csv'), ], initialdir='')

        # определение номера канала из названия файла
        name_ch = str(opened_csv_files)
        name_temp = name_ch = name_ch.split('/')
        if int(name_ch[len(name_ch) - 1][3]) == 1:
            name_ch = '1 канал'
        else:
            name_ch = '2 канал'

        # определение номера ТГ из названия файла
        name_TG = int(name_temp[len(name_temp) - 1][2])

        data_out = pd.DataFrame()
        list_ = []
        temp_time_2 = []
        start_read = time.time()
        for file_ in opened_csv_files:
            df = pd.read_csv(file_, header=0, delimiter=';', usecols=fields)
            list_.append(df)
        data_out = pd.concat(list_)

        temp_time = df[time_column]

        i = 0
        summa = 0
        while i < len(df[time_column]) - 1:
            if (df[time_column][i + 1] - df[time_column][i]) != -990:
                summa = summa + (df[time_column][i + 1] - df[time_column][i]) / 1000
                temp_time_2.append('%.2f' % summa)
            else:
                summa = summa + (1 + (df[time_column][i + 1] - df[time_column][i]) / 1000)
                temp_time_2.append('%.2f' % summa)
            i = i + 1
        temp_time_2.append(temp_time_2[len(temp_time_2) - 1])

        print('массив ВРЕМЯ cформирован')

        # data_out = pd.concat(temp_time_2)

        print(time.time() - start_read)

        # print(data_out.head)
        # print(len(temp_time_2))

        return data_out, temp_time_2, name_ch, name_TG

    data_ch = reading_data('Открыть CSV файл одного канала')

    start_program = time.time()

    name_draw = data_ch[2]
    name_TG = data_ch[3]

    print('1 канал', data_ch[0].shape)

    # print(data_ch[0][OZ_zadanie_B_name_column])

    # рисование графиков
    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(facecolor='#FFFFCC')
    fig.canvas.set_window_title('ОЗ Одного канала')

    point_f = 10

    line, = ax.plot(data_ch[1][1::point_f], data_ch[0][OZ_A_name_column][1::point_f],
                    lw=0.5, color='b', label="ОЗ_А")
    line1, = ax.plot(data_ch[1][1::point_f], data_ch[0][OZ_B_name_column][1::point_f],
                     lw=0.5, color='r', label="ОЗ_Б")
    line11, = ax.plot(data_ch[1][1::point_f], data_ch[0][mast_chanel][1::point_f],
                      lw=2, color='y', label="Ведущий канал")
    line12, = ax.plot(data_ch[1][1::point_f], data_ch[0][OZ_zadanie_A_name_column][1::point_f],
                      lw=0.5, color='black', label="ОЗ_А задание")
    line13, = ax.plot(data_ch[1][1::point_f], data_ch[0][OZ_zadanie_B_name_column][1::point_f],
                      lw=0.5, color='black', label="ОЗ_Б задание")
    line14, = ax.plot(data_ch[1][1::point_f], data_ch[0][Save_TG][1::point_f],
                      lw=0.5, color='black', label="Зашита ТГ")

    fig.suptitle('ТГ:' + str(name_TG) + ', ' + str(name_draw), fontsize='large')
    ax.set_xlabel('Время, c')
    ax.set_ylabel('ОЗ, мм')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # для вспомогательной оси
    ax2 = ax.twinx()
    line2, = ax2.plot(data_ch[1][1::(point_f * 2)], data_ch[0][GSM_name_column][1::(point_f * 2)],
                      lw=0.5, color='g', label="ГСМ")
    line21, = ax2.plot(data_ch[1][1::point_f], data_ch[0][GSM_A_cur][1::point_f],
                       lw=0.5, color='b', label="ГСМ_А_тек")
    line22, = ax2.plot(data_ch[1][1::point_f], data_ch[0][GSM_B_cur][1::point_f],
                       lw=0.5, color='r', label="ГСМ_Б_тек")

    ax2.set_ylabel('ГСМ, мм')
    ax.legend((line, line1, line11, line12, line13, line14), ('ОЗ_А', 'ОЗ_Б', "Ведущий канал", "ОЗ_А задание",
                                                              "ОЗ_Б задание", Save_TG))
    ax2.legend((line2, line21, line22), ('ГСМ.Текущее', 'ГСМ-А.Текущее', 'ГСМ-Б.Текущее'))

    # функция - отображения графиков 1 чек-бокс
    def func(label):
        if label == 'ОЗ_А':
            line.set_visible(not line.get_visible())
        elif label == 'ОЗ_Б':
            line1.set_visible(not line1.get_visible())
        elif label == "Ведущий канал":
            line11.set_visible(not line11.get_visible())
        elif label == "ОЗ_А задание":
            line12.set_visible(not line12.get_visible())
        elif label == "ОЗ_Б задание":
            line13.set_visible(not line13.get_visible())
        elif label == "ГСМ":
            line2.set_visible(not line2.get_visible())
        elif label == "GSM-A":
            line21.set_visible(not line21.get_visible())
        elif label == "GSM-B":
            line22.set_visible(not line22.get_visible())
        elif label == Save_TG:
            line14.set_visible(not line14.get_visible())
        plt.draw()

    # Чек-боксы графиков
    rax = plt.axes([0.0, 0.1, 0.12, 0.13])  # положение чекбокса - x,y, х1,y1 - размер окна
    check = CheckButtons(rax, ('ОЗ_А', 'ОЗ_Б', "Ведущий канал", "ОЗ_А задание", "ОЗ_Б задание", 'ГСМ', 'GSM-A',
                               'GSM-B', Save_TG),
                         (True, True, True, True, True, True, True, True, True))
    check.on_clicked(func)

    time_all = time.time() - start_program
    # time_all = float(time_all) + float(time_average) + float(time_read)

    with open(log_name, 'a', newline='') as csv_out:
        csv_out.write('Общее время "ОЗ Одного канала": %.2f cек\n' % time_all)
        csv_out.write('-' * 20 + '\n')

    plt.show()


# Смещение
# @profile
def shift_oz(event):
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('-' * 20 + '\n')
        time_now = time.strftime('%Y_%m_%d_%H:%M:%S')
        csv_out.write(f'Функция "Cмещение" из файла {os.path.basename(__file__)} запущена на: {os.getlogin()} в {time_now} \n')
        csv_out.write('N:' + combo_iteration.get() + '\n')

    GSM_A_name_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
    GSM_B_name_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
    OZ_A_name_column = 'ОЗ ГСМ-А.Текущее положение'  # ОЗ ГСМ-А.Текущее положение
    OZ_B_name_column = 'ОЗ ГСМ-Б.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение

    fields = [GSM_A_name_column, OZ_A_name_column, GSM_B_name_column, OZ_B_name_column]

    # функция чтения данных из csv
    def reading_data(namedirection):

        opened_csv_files = fd.askopenfiles(title=namedirection,
                                           filetypes=[('CSV files', '*.csv'), ('GZ Files', '*.gz')], 
                                           initialdir='')

        start_read = time.time()

        # определение номера канала из названия файла
        file_name = str(opened_csv_files)
        # name_temp = name_ch = name_ch.split('/')
        # if int(name_ch[len(name_ch)-1][3]) == 1:
        #     name_ch = '1 канал'
        # else:
        #     name_ch = '2 канал'
        #
        #
        # # определение номера ТГ из названия файла
        # name_tg = int(name_temp[len(name_temp) - 1][2])

        if file_name.find('ШУР') >= 0:
            index_tg = file_name.find('ШУР')
            name_ch = file_name[index_tg + 3]
            name_tg = file_name[index_tg + 4]
        else:
            index_tg = file_name.find('ТГ')
            name_ch = file_name[index_tg + 3]
            name_tg = file_name[index_tg + 4]

        list_ = []
        for file_ in opened_csv_files:
            df = pd.read_csv(file_, header=0, delimiter=';', usecols=fields)
            list_.append(df)
        data_out = pd.concat(list_)
        time_read = '%.2f' % float(time.time() - start_read)

        return data_out, time_read, name_tg

    data_up = reading_data('Открыть CSV файлы. Движение вверх')
    data_down = reading_data('Открыть CSV файлы. Движение вниз')

    number_TG = data_up[2]

    time_read = float(data_up[1]) + float(data_down[1])

    print('Загрузка данных: %.2f сек' % time_read)
    with open('log.txt', 'a') as csv_out:
        csv_out.write('Загрузка данных: %.2f cек\n' % time_read)

    print('движение ВВЕРХ', data_up[0].shape)
    print('движение ВНИЗ', data_down[0].shape)

    # создание списка tablenumber из значений GSM от 0 до 320
    tablenumber = [n4 for n4 in range(321)]

    # скользящее среднее
    iterat = int(combo_iteration.get())

    def movingaverage(series, n):  # series,  n - кол-во усреднений
        out = []
        for zz in range(len(series)):
            b = len(series) - n + 1
            if zz < n // 2:
                out.append(np.average(series[zz:n + zz]))
            elif n // 2 <= zz <= b:
                out.append(np.average(series[zz - n // 2:zz + n // 2 + 1]))
            else:
                out.append(np.average(series[-n:]))
        return out, len(out)

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
            line1, = ax.plot(GSM_up[::point_f], OZ_up_filtr[::point_f], lw=2, color='r', label="GSM-B")  # ГСМ-Б
            line2, = ax.plot(GSM_down[::point], OZ_down[::point], lw=2, color='g', label="GSM-B")  # ГСМ-Б
            line3, = ax.plot(GSM_down[::point_f], OZ_down_filtr[::point_f], lw=2, color='r', label="GSM-B")  # ГСМ-Б
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

    draw1 = draw('Движение ГСМ-А. n=', data_up[0].iloc[:, 0], data_up[0].iloc[:, 2],
                 data_up[0].iloc[:, 4], data_down[0].iloc[:, 0],
                 data_down[0].iloc[:, 2], data_down[0].iloc[:, 4])
    draw2 = draw('Движение ГСМ-Б. n=', data_up[0].iloc[:, 1], data_up[0].iloc[:, 3],
                 data_up[0].iloc[:, 5], data_down[0].iloc[:, 1], data_down[0].iloc[:, 3],
                 data_down[0].iloc[:, 5])

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
        w.writerow(('i', 'ОЗ ГСМ-А.Вверх', 'ОЗ ГСМ-А.Вниз', 'ОЗ ГСМ-А.Отсечка', 'ОЗ ГСМ-Б.Вниз',
                    'ОЗ ГСМ-Б.Вниз', 'ОЗ ГСМ-Б.Отсечка'))
    i = 0
    for zz in range(len(tablenumber)):
        with open(out_file, 'a', newline='') as csv_out:
            w = csv.writer(csv_out, delimiter=';')
            w.writerow((tablenumber[i], OZ_A_final_up[i], OZ_A_final_down[i], OZ_A_otsechka[i],
                        OZ_B_final_up[i], OZ_B_final_down[i], OZ_B_otsechka[i]))
        i = i + 1

    # функция записи в файл TXT для UNITY
    def write_to_UNITY(out_file, tablenumber, OZ_otsechka):
        with open(out_file, 'w', newline='') as unity_out:
            if out_file == 'gsm_tg1_a.txt':
                unity_out.write('Ust_shift1A_def	%kw16000	ARRAY[0..340] OF REAL\t\t(')
            else:
                unity_out.write('Ust_shift1B_def	%kw16682	ARRAY[0..340] OF REAL\t\t(')
            fi = 0
            for zz in range(len(tablenumber)):
                if zz == 320:
                    unity_out.write('[' + str(tablenumber[fi]) + ']:=' + OZ_otsechka[fi])
                else:
                    unity_out.write('[' + str(tablenumber[fi]) + ']:=' + OZ_otsechka[fi] + ',')
                fi = fi + 1
        unity_out.write(')\n')

    if number_TG == 1:
        write_to_UNITY('gsm_tg1_a.txt', tablenumber, OZ_A_otsechka)
        write_to_UNITY('gsm_tg1_b.txt', tablenumber, OZ_B_otsechka)
    else:
        write_to_UNITY('gsm_tg2_a.txt', tablenumber, OZ_A_otsechka)
        write_to_UNITY('gsm_tg2_b.txt', tablenumber, OZ_B_otsechka)

    time_all = time.time() - time_all
    time_all = float(time_all) + float(time_average) + float(time_read)

    print('Общее время Смещения: %.2f cек' % time_all)

    with open(log_name, 'a', newline='') as csv_out:
        csv_out.write('Общее время Смещения: %.2f cек\n' % time_all)
        csv_out.write('-' * 20 + '\n')

    plt.show()


# Закрытия окна GUI
def quit():
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('*' * 50 + '\n')
    root.quit()  # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate


if __name__ == '__main__':
    root = Tk()
    root.minsize()
    root.title('Всякая ересь...')

    # кнопка вывод Frame "1"
    win_1 = Frame()
    win_1.grid(row=0, column=0)
    frame_b = LabelFrame(win_1, text='Тук_тук')
    frame_b.grid(row=0, column=0)

    # кнопка СКАЧКИ
    butSTEP = Button(win_1, text="Скачки/Шаги")
    butSTEP.grid(in_=frame_b, sticky=S, row=0, column=0)
    butSTEP.bind('<ButtonRelease-1>', stepper)

    # кнопка СКОРОСТИ
    butVel = Button(win_1, text="Скорости", width=20)
    butVel.grid(in_=frame_b, sticky=S, row=0, column=1)
    butVel.bind('<ButtonRelease-1>', velosity)

    # кнопка сравнение энкодеров по одной стороне
    but_Enc = Button(win_1, text="ОЗ по одной стороне")
    but_Enc.grid(in_=frame_b, sticky=S, row=1, column=0)
    but_Enc.bind('<ButtonRelease-1>', one_side)

    # кнопка вывод показаний энкодрера по одному каналу.
    but_one_channel = Button(win_1, text="ОЗ по одному каналу")
    but_one_channel.grid(in_=frame_b, sticky=S, row=1, column=1)
    but_one_channel.bind('<ButtonRelease-1>', one_channel)

    # вывод кнопки Закрыть  в окно приложения
    B4 = Button(root, text='Закрыть', command=quit)
    B4.grid(column=1, row=5)

    # кнопка вывод Frame "Смещения"
    win = Frame()
    win.grid(row=1, column=0)

    frame_a = LabelFrame(win, text='Смещение')
    frame_a.grid(column=0, row=0)
    Label(win, text='Число усредняемых отсчетов:  ', font="Arial 12").grid(in_=frame_a, sticky=S)
    list_iteration = [50, 100, 200, 300, 400, 1000, 4000, 8000]
    combo_iteration = Combobox(values=list_iteration, width=5, height=5)
    combo_iteration.grid(in_=frame_a, row=0, column=1)
    combo_iteration.set('4000')
    but_ustavki = Button(frame_a, text="Создать смещения")
    but_ustavki.grid(row=1, column=1)
    but_ustavki.bind('<ButtonRelease-1>', shift_oz)

    root.mainloop()


#todo
# 1. добавить архивные файлы
# 2. кольские не читает отсечки