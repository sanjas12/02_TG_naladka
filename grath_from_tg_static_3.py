import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import SpanSelector
from tkinter.filedialog import *                # для askopenfilename
import csv
from tkinter import filedialog as fd
import pandas as pd

count = 0
# функция построения графика "шаги\скачки\степпера"
def grath_stepper(event):

    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('Программа Шаги запущена:' + time.strftime('%Y_%m_%d_%H:%M:%S') + '\n')

    def openCSV(event, name_direction):
        op = askopenfiles(title=name_direction, filetypes=[('CSV files', '*.csv'), ], initialdir='')
        return op

    op = openCSV(event, 'Открыть CSV файл с ШАГАМИ')

    start_program = time.time()

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
            print('Колонка', name_column, 'не найдена. !!!!!!!!!!:')
        else:
            print(name_column, '  колонка номер :', n)
        infile.close()
        return n

    # поиск номеров колонок из файла csv
    print('*'*50)
    GSM_A_column = find_column('ГСМ-А.Текущее положение')-1  # ГСМ-А.Текущее положение
    GSM_B_column = find_column('ГСМ-Б.Текущее положение')-1  # ГСМ-Б.Текущее положение
    Zadanie_column = find_column('Значение развертки. Положение ГСМ')-1   # Значение развертки. Положение ГСМ
    time_column = find_column('time')-1   # время

    # функция чтения данных из оригинальных CSV файлов
    def read_data_from_file(name_file_CSV, GSM_A_column, name_column, GSM_B_column, name_column_2,
                    Zadanie_column, name_column_3, time_column, name_column_4):
        number_row_in_all_csv_file = 0
        GSM_A = []
        GSM_B = []
        Zadanie = []
        time = []
        temp_time = []
        # запись данных
        for zz in range(len(name_file_CSV)):               # отсавлена возможность для выбора нескольких файлов
            i = 0
            for row in csv.reader(name_file_CSV[zz], delimiter=';'):
                if i == 0:
                    # пропуск первой строки
                    pass
                else:
                    GSM_A.append(float(row[GSM_A_column]))  # ГСМ-А
                    GSM_B.append(float(row[GSM_B_column]))  # ГСМ-Б
                    Zadanie.append(float(row[Zadanie_column]))  # Задание ГСМ
                    if time_column > 0:
                        time.append(float(row[time_column]))  # время из CSV, если есть колонка время
                    else:
                        temp_time.append(float(row[1]))  # время для расчета
                i = i + 1
                number_row_in_all_csv_file += 1

        # создание колонки ВРЕМЯ, если ее нет
        if time_column > 0:
            print('колонка ВРЕМЯ уже есть')
        else:
            i = 0
            summa = 0
            while i < len(temp_time) - 1:
                if (temp_time[i + 1] - temp_time[i]) != -990:
                    summa = summa + (temp_time[i + 1] - temp_time[i]) / 1000
                    time.append('%.2f' % summa)
                else:
                    summa = summa + (1 + (temp_time[i + 1] - temp_time[i]) / 1000)
                    time.append('%.2f' % summa)
                i = i + 1
            print('массив ВРЕМЯ cформирована')

        # дописываем значение если разные длина массива время не совпадает
        if len(time) == len(GSM_A):
            pass
        else:
            time.append(time[len(time)-1])

        print('Колонка\t', ' \t' * 4, '\tДлина массива')
        print(name_column,  ' \t' * 2, len(GSM_A))
        print(name_column_2,' \t' * 2, len(GSM_B))
        print(name_column_3, ' \t' * 2, len(Zadanie))
        print(name_column_4, ' \t' * 2, len(time))
        print('Кол-во строк во всех СSV:', number_row_in_all_csv_file)
              # (0)    (1)     (2)     (3)
        return GSM_A, GSM_B, Zadanie, time, number_row_in_all_csv_file

    data_from_file = read_data_from_file(op, GSM_A_column, 'ГСМ-А.Текущее положение', GSM_B_column,
                                         'ГСМ-Б.Текущее положение', Zadanie_column, 'Значение развертки. Положение ГСМ',
                                         time_column, 'time')

    # отрисовка окна для графиков
    fig = plt.figure(figsize=(6, 6))

    point_f = 10

    first = []
    second = []
    third = []
    fourth = []

    i=0
    for z in range(len(data_from_file[3])):
        if i < len(data_from_file[3]):
            fourth.append(data_from_file[3][i])
            i = i + point_f
    print('4', len(fourth), len(data_from_file[3]))

    i = 0
    for z in range(len(data_from_file[0])):
        if i < len(data_from_file[0]):
            first.append(data_from_file[0][i])
            second.append(data_from_file[1][i])
            third.append(data_from_file[2][i])
            i = i + point_f

    print('1', len(first), len(data_from_file[3]))
    print('2', len(second), len(data_from_file[3]))
    print('3', len(third), len(data_from_file[3]))

    i = 0
    with open('test_2.txt', 'w', newline='') as csv_out:
        w = csv.writer(csv_out, delimiter=';')
        for z in range(len(first)):
            w.writerow((fourth[i], first[i], second[i], third[i]))
            i = i + 1

    # отрисовка 1 графика
    ax = fig.add_subplot(211, facecolor='#FFFFCC')
    # line, = ax.plot(data_from_file[3][1::point_f], data_from_file[0][1::point_f], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
    # line1, = ax.plot(data_from_file[3][1::point_f], data_from_file[1][1::point_f], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
    # line2, = ax.plot(data_from_file[3][1::point_f], data_from_file[2][1::point_f], lw=1, color='black', label="Задание")   # задание
    line, = ax.plot(fourth, first, lw=2, color='b', label="ГСМ-А")  # ГСМ-А
    line1, = ax.plot(fourth, second, lw=2, color='r', label="ГСМ-Б")  # ГСМ-Б
    line2, = ax.plot(fourth, third, lw=1, color='black', label="Задание")  # задание

    ax.set_xlabel('Время, c')
    ax.set_ylabel('ГСМ, мм')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
    plt.title('Шаги\Скачки_РБМК')

    # шаг осей
    # ax.xaxis.set_major_locator(ticker.LinearLocator(10))
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(30))

    # отрисовка легенды
    fig.legend((line, line1, line2), ('ГСМ-А', 'ГСМ-Б', 'Задание'))

    # отрисовка 2 графика
    ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
    line02, = ax2.plot(fourth, first, lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
    line12, = ax2.plot(fourth, second, lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
    line22, = ax2.plot(fourth, third, lw=1, color='black', label="Задание")   # задание
    # line12, = ax2.plot(data_from_file[3], data_from_file[1], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
    # line22, = ax2.plot(data_from_file[3], data_from_file[2], lw=1, color='black', label="Задание")   # задание
    ax2.set_xlabel('Время, c')
    ax2.set_ylabel('ГСМ, мм')
    ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # функция выделения_новая
    def onselect(xmin, xmax):
        print(xmin, xmax)
        indmin, indmax = np.searchsorted(fourth, (float(xmin), float(xmax)))  # получение минимального и максимального
        print(indmin, indmax)
        indmax = min(len(fourth) - 1, indmax)
        # print(indmin, indmax)

        thisx = fourth[indmin:indmax]             # новые данные для значений "время"
        thisx_new = []                              # формирование нового массива значений "время"
        for zz in range(len(thisx)):
              thisx_new.append(zz*0.01)
        thisy0 = np.array(first[indmin:indmax])             # новые данные для значений "ГСМ-А")
        thisy1 = np.array(second[indmin:indmax])             # новые данные для значений "ГСМ-Б"
        thisy2 = np.array(third[indmin:indmax])             # новые данные для значений "Задание"
        line02.set_data(thisx_new, thisy0)               # перерисовка графика Задание
        # line12.set_data(thisx_new, thisy1)               # перерисовка графика Задание
        # line22.set_data(thisx_new, thisy2)               # перерисовка графика Задание
        ax2.set_xlim(thisx_new[0], thisx_new[-1])           # перерисовка масштаба осей X
        ax2.set_ylim(thisy2.min()-1, thisy2.max()+1)      # перерисовка масштаба осей Y от Задания
        fig.canvas.draw()

    # set useblit True on gtkagg for enhanced performance
    span = SpanSelector(ax, onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))

    # функция - отображения графиков 1 чек-бокс
    def func(label):
        if label == 'ГСМ-А':
            line.set_visible(not line.get_visible())
        elif label == 'ГСМ-Б':
            line1.set_visible(not line1.get_visible())
        elif label == 'Задание':
            line2.set_visible(not line2.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 1
    rax = plt.axes([0.0, 0.5, 0.1, 0.08])       # положение чекбокса - x,y, х1,y1 - размер окна
    check = CheckButtons(rax, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
    check.on_clicked(func)

    # функция - отображения графиков 2 чек-бокс
    def func_2(label):
        if label == 'ГСМ-А':
            line02.set_visible(not line02.get_visible())
        elif label == 'ГСМ-Б':
            line12.set_visible(not line12.get_visible())
        elif label == 'Задание':
            line22.set_visible(not line22.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 2
    rax_2 = plt.axes([0.0, 0.01, 0.1, 0.08])    # положение чекбокса - x,y, х1,y1 - размер окна
    check_2 = CheckButtons(rax_2, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
    check_2.on_clicked(func_2)


    with open(log_name, 'a', newline='') as csv_out:
        csv_out.write('время работы функции ШАГИ: %.2f cек\n' % float(time.time() - start_program))
    print('время работы функции ШАГИ: %.2f cек' % float(time.time() - start_program))

    plt.show()

# функция построения графика "Скорости"
def grath_velosity(event):
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('Программа Скорости запущена:' + time.strftime('%Y_%m_%d_%H:%M:%S') + '\n')

    def openCSV(event, name_direction):
        op = askopenfiles(title=name_direction, filetypes=[('CSV files', '*.csv'), ], initialdir='')
        return op

    op = openCSV(event, 'Открыть CSV файл')

    start_program = time.time()

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
            print('Колонка', name_column, 'не найдена. !!!!!!!!!!:')
        else:
            print(name_column, '  колонка номер :', n)
        infile.close()
        return n

    # поиск номеров колонок из файла csv
    print('*'*50)
    GSM_A_column = find_column('ГСМ-А.Текущее положение')-1  # ГСМ-А.Текущее положение
    GSM_B_column = find_column('ГСМ-Б.Текущее положение')-1  # ГСМ-Б.Текущее положение
    time_column = find_column('time')-1   # время

    # функция создания массива данных из оригинальных файлов
    def read_data_from_file(name_file_CSV, GSM_A_column, name_column, GSM_B_column, name_column_2,
                            time_column, name_column_4):
        number_row_in_all_csv_file = 0
        GSM_A = []
        GSM_B = []
        time = []
        temp_time = []
        # запись данных
        for zz in range(len(name_file_CSV)):               # отсавлена возможность для выбора нескольких файлов
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
                    summa = summa + (temp_time[i + 1] - temp_time[i]) / 1000
                    time.append(summa)
                else:
                    summa = summa + (1 + (temp_time[i + 1] - temp_time[i]) / 1000)
                    time.append(summa)
                i = i + 1
            print('массив ВРЕМЯ cформирована')

        # дописываем значение если разные длина массива время не совпадает
        if len(time) == len(GSM_A):
            pass
        else:
            time.append(time[len(time)-1])

        print('Колонка\t', ' \t' * 4, '\tДлина массива')
        print(name_column,  ' \t' * 2, len(GSM_A))
        print(name_column_2,' \t' * 2, len(GSM_B))
        print(name_column_4, ' \t' * 2, len(time))
        print('Кол-во строк во всех СSV:', number_row_in_all_csv_file)
              # (0)    (1)     (2)     (3)
        return GSM_A, GSM_B, time, number_row_in_all_csv_file

    data_from_file = read_data_from_file(op, GSM_A_column, 'ГСМ-А.Текущее положение', GSM_B_column,
                                         'ГСМ-Б.Текущее положение',time_column, 'time')

    # отрисовка окна для графиков
    fig = plt.figure(figsize=(6, 6))

    # отрисовка 1 графика
    ax = fig.add_subplot(211, facecolor='#FFFFCC')
    line, = ax.plot(data_from_file[2], data_from_file[0], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
    line1, = ax.plot(data_from_file[2], data_from_file[1], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
    ax.set_xlabel('Время, c')
    ax.set_ylabel('ГСМ, мм')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
    plt.title('Скорости')

    # шаг осей
    # ax.xaxis.set_major_locator(ticker.LinearLocator(10))
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(30))

    # отрисовка легенды
    fig.legend((line, line1), ('ГСМ-А', 'ГСМ-Б', ))

    # отрисовка 2 графика
    ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
    line02, = ax2.plot(data_from_file[2], data_from_file[0], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
    line12, = ax2.plot(data_from_file[2], data_from_file[1], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
    ax2.set_xlabel('Время, c')
    ax2.set_ylabel('ГСМ, мм')
    ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # функция выделения
    def onselect(xmin, xmax):
        indmin, indmax = np.searchsorted(data_from_file[2], (xmin, xmax))  # получение минимального и максимального
                                                                  # элемента для значений  dataf[0] - "время"
        indmax = min(len(data_from_file[2]) - 1, indmax)
        thisx = data_from_file[2][indmin:indmax]             # новые данные для значений "время"
        thisx_new = []                              # формирование нового массива значений "время"
        for zz in range(len(thisx)):
              thisx_new.append(zz*0.01)
        thisy0 = np.array(data_from_file[0][indmin:indmax])    # новые данные для значений "ГСМ-А")
        thisy1 = np.array(data_from_file[1][indmin:indmax])           # новые данные для значений "ГСМ-А"
        # thisy2 = np.array(data_from_file[2][indmin:indmax])             # новые данные для значений "Задание"
        line02.set_data(thisx_new, thisy0)               # перерисовка графика Задание
        line12.set_data(thisx_new, thisy1)               # перерисовка графика Задание
        # line22.set_data(thisx_new, thisy2)               # перерисовка графика Задание
        ax2.set_xlim(thisx_new[0], thisx_new[-1])           # перерисовка масштаба осей X
        ax2.set_ylim(thisy1.min()-1, thisy1.max()+1)      # перерисовка масштаба осей Y от Задания
        fig.canvas.draw()

    # set useblit True on gtkagg for enhanced performance
    span = SpanSelector(ax, onselect, 'horizontal', useblit=True, rectprops=dict(alpha=0.5, facecolor='red'))

    # функция - отображения графиков 1 чек-бокс
    def func(label):
        if label == 'ГСМ-А':
            line.set_visible(not line.get_visible())
        elif label == 'ГСМ-Б':
            line1.set_visible(not line1.get_visible())
        # elif label == 'Задание':
        #     line2.set_visible(not line2.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 1
    rax = plt.axes([0.0, 0.5, 0.1, 0.08])       # положение чекбокса - x,y, х1,y1 - размер окна
    check = CheckButtons(rax, ('ГСМ-А', 'ГСМ-Б'), (True, True))
    check.on_clicked(func)

    # функция - отображения графиков 2 чек-бокс
    def func_2(label):
        if label == 'ГСМ-А':
            line02.set_visible(not line02.get_visible())
        elif label == 'ГСМ-Б':
            line12.set_visible(not line12.get_visible())
        # elif label == 'Задание':
        #     line22.set_visible(not line22.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 2
    rax_2 = plt.axes([0.0, 0.01, 0.1, 0.08])    # положение чекбокса - x,y, х1,y1 - размер окна
    check_2 = CheckButtons(rax_2, ('ГСМ-А', 'ГСМ-Б'), (True, True))
    check_2.on_clicked(func_2)


    with open(log_name, 'a', newline='') as csv_out:
        csv_out.write('время работы функции Скорости: %.2f cек\n' % float(time.time() - start_program))
    print('время работы функции ШАГИ: %.2f cек' % float(time.time() - start_program))

    plt.show()

# функция построения графика "Сравнение энкод/ОЗ одной стороны"
def eq_enc(event):

    OZ_A_name_column = 'ОЗ ГСМ-А.Текущее положение'  # ОЗ ГСМ-А.Текущее положение
    OZ_B_name_column = 'ОЗ ГСМ-Б.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение
    GSM_name_column = 'ГСМ.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение
    time_column = "миллисекунды"

    fields = [OZ_A_name_column, OZ_B_name_column, time_column, GSM_name_column]

    # функция чтения данных из csv
    def reading_data(namedirection):
        opened_csv_files = fd.askopenfiles(title=namedirection, filetypes=[('CSV files', '*.csv'), ], initialdir='')

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

        print(time.time()-start_read)

        # print(data_out.head)
        # print(len(temp_time_2))

        return data_out, temp_time_2, name_TG

    data_1_ch = reading_data('Открыть CSV файл 1 канала')
    data_2_ch = reading_data('Открыть CSV файл 2 канала')

    print('1 канал', data_1_ch[0].shape)
    print('2 канал', data_2_ch[0].shape)

    # функция рисования графиков
    def draw(name, name_column, OZ_1, OZ_2):
        fig, ax = plt.subplots()
        point_f = 10                                        #

        # print(OZ_1[1][1::point_f], OZ_1[0][name_column][1::point_f])

        fdfd = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        fdfd_2 = [11, 22, 33, 44, 55, 66, 77, 88, 99]

        print(len(OZ_1[1][1::point_f]), len(list(OZ_1[0][name_column][1::point_f])))
        print(type(OZ_1[1][1::point_f]), type(list(OZ_1[0][name_column][1::point_f])))

        qqq = []
        www = []

        out_file = 'test.txt'
        i=0
        with open(out_file, 'w', newline='') as csv_out:
            w = csv.writer(csv_out, delimiter=';')
            for z in range(len(OZ_1[1][1::point_f])):
                w.writerow((OZ_1[1][1::point_f][i], list(OZ_1[0][name_column][1::point_f][i])))
                qqq.append(OZ_1[1][1::point_f][i])
                www.append(list(OZ_1[0][name_column][1::point_f])[i])
                i = i+1

        line, = ax.plot((qqq, www), lw=0.5, color='b', label="ОЗ_1_А")  #
        # line, = ax.plot(OZ_1[1][1::point_f], list(OZ_1[0][name_column][1::point_f]), lw=0.5, color='b', label="ОЗ_1_А")  #
        # line1, = ax.plot(OZ_2[1][1::point_f], OZ_2[0][name_column][1::point_f], lw=0.5, color='r', label="ОЗ_1_Б")  #
        fig.suptitle('ТГ:' + name, fontsize='large')
        ax.set_xlabel('Время, c')
        ax.set_ylabel('ОЗ, мм')
        ax.grid(linestyle='--', linewidth=0.5, alpha=.85)

        # для вспомогательной оси
        ax2 = ax.twinx()
        # line2, = ax2.plot(OZ_2[1][1::(point_f*2)], OZ_2[0][GSM_name_column][1::(point_f*2)], lw=0.5, color='g', label="ГСМ")  #
        ax2.set_ylabel('ГСМ, мм')
        # ax.legend((line, line1, line2), ('1 канал', '2 канал', GSM_name_column))

    draw1 = draw((str(data_1_ch[2]) + ', Сторона А'), OZ_A_name_column, data_1_ch, data_2_ch)

    # draw2 = draw((str(data_1_ch[2]) + ', Сторона Б'), OZ_B_name_column, data_1_ch, data_2_ch)

    plt.show()

# функция построения графика показаний ОЗ "Одного канала"
def one_channel(event):

    OZ_A_name_column = 'ОЗ ГСМ-А.Текущее положение'  # ОЗ ГСМ-А.Текущее положение
    OZ_B_name_column = 'ОЗ ГСМ-Б.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение
    GSM_name_column = 'ГСМ.Текущее положение'  # ОЗ ГСМ-Б.Текущее положение
    time_column = "миллисекунды"

    fields = [OZ_A_name_column, OZ_B_name_column, time_column, GSM_name_column]

    # функция чтения данных из csv
    def reading_data(namedirection):
        opened_csv_files = fd.askopenfiles(title=namedirection, filetypes=[('CSV files', '*.csv'), ], initialdir='')

        #определение номера канала из названия файла
        name_ch = str(opened_csv_files)
        name_temp = name_ch = name_ch.split('/')
        if int(name_ch[len(name_ch)-1][3]) == 1:
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

        print(time.time()-start_read)

        # print(data_out.head)
        # print(len(temp_time_2))

        return data_out, temp_time_2, name_ch, name_TG

    data_ch = reading_data('Открыть CSV файл одного канала')

    name_draw = data_ch[2]
    name_TG = data_ch[3]

    print('1 канал', data_ch[0].shape)

    # функция рисования графиков
    fig, ax = plt.subplots()
    point_f = 10                                        #

    line, = ax.plot(data_ch[1][1::point_f], data_ch[0][OZ_A_name_column][1::point_f],
                    lw=0.5, color='b', label="ОЗ_А")
    line1, = ax.plot(data_ch[1][1::point_f], data_ch[0][OZ_B_name_column][1::point_f],
                     lw=0.5, color='r', label="ОЗ_Б")
    fig.suptitle('ТГ:' + str(name_TG) +', ' + str(name_draw), fontsize='large')
    ax.set_xlabel('Время, c')
    ax.set_ylabel('ОЗ, мм')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # для вспомогательной оси
    ax2 = ax.twinx()
    line2, = ax2.plot(data_ch[1][1::(point_f*2)], data_ch[0][GSM_name_column][1::(point_f*2)],
                      lw=0.5, color='g', label="ГСМ")
    ax2.set_ylabel('ГСМ, мм')
    ax.legend((line, line1, line2), ('ОЗ_А', 'ОЗ_Б', GSM_name_column))

    # функция - отображения графиков 1 чек-бокс
    def func(label):
        if label == 'ОЗ_А':
            line.set_visible(not line.get_visible())
        elif label == 'ОЗ_Б':
            line1.set_visible(not line1.get_visible())
        elif label == 'ГСМ':
            line2.set_visible(not line2.get_visible())
        plt.draw()

    # работа со списком чек-боксов отображающих графики 1
    rax = plt.axes([0.0, 0.2, 0.1, 0.08])       # положение чекбокса - x,y, х1,y1 - размер окна
    check = CheckButtons(rax, ('ОЗ_А', 'ОЗ_Б', 'ГСМ'), (True, True, True))
    check.on_clicked(func)

    plt.show()

# функция закрытия  окна приложения
def quit():
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('*'*50 + '\n')
    root.quit()  # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

if __name__ == '__main__':
    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('*'*50 + '\n')
        csv_out.write('Программа GRATH запущена:' + time.strftime('%Y_%m_%d_%H:%M:%S') + '\n')
    root = Tk()
    root.minsize()
    root.title('Скачки/Cкорости')

    # кнопка СКАЧКИ
    butSTEP = Button(root, text="Скачки/Шаги", width=30)
    butSTEP.grid(row=0, column=0)
    butSTEP.bind('<ButtonRelease-1>', grath_stepper)

    # кнопка СКОРОСТИ
    butVel = Button(root, text="Скорости", width=30)
    butVel.grid(row=0, column=1)
    butVel.bind('<ButtonRelease-1>', grath_velosity)

    # кнопка сравнение энкодеров по одной стороне
    but_Enc = Button(root, text="Сравнение энкод\n одной стороны", width=30)
    but_Enc.grid(row=1, column=0)
    but_Enc.bind('<ButtonRelease-1>', eq_enc)

    # кнопка вывод показаний энкодрера сторона А.
    but_one_channel = Button(root, text="Показания ОЗ по одному каналу", width=30)
    but_one_channel.grid(row=1, column=1)
    but_one_channel.bind('<ButtonRelease-1>', one_channel)

    # вывод кнопки Закрыть  в окно приложения
    B4 = Button(root, text='Закрыть', command=quit)
    B4.grid(column=2, row=2)

    root.mainloop()
