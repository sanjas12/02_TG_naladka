import numpy as np
import matplotlib.pyplot as plt
import time
from matplotlib.widgets import SpanSelector
from tkinter.filedialog import * # для askopenfilename
import csv

count = 0
# функция построения графика "шаги\скачки\степпера"
def grath_stepper(event):
    start_program = time.time()

    log_name = 'log.txt'
    with open(log_name, 'a') as csv_out:
        csv_out.write('Программа Шаги РБМК запущена:' + time.strftime('%Y_%m_%d_%H:%M:%S') + '\n')

    def openCSV(event, name_direction):
        op = askopenfiles(title=name_direction, filetypes=[('CSV files', '*.csv'), ], initialdir='')
        return op

    op = openCSV(event, 'Открыть CSV файл')

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
    GSM_A_column = find_column('ГСМ. Текущее положение')  # ГСМ-А.Текущее положение
    # GSM_B_column = find_column('ГСМ-Б.Текущее положение')-1  # ГСМ-Б.Текущее положение
    Zadanie_column = find_column('ГСМ. Заданное конечное значение регулятора')-1   # Значение развертки. Положение ГСМ
    time_column = find_column('time')-1   # время

    # функция создания массива данных из оригинальных файлов
    def read_data_from_file(name_file_CSV, GSM_A_column, name_column, Zadanie_column, name_column_3, time_column, name_column_4):
        number_row_in_all_csv_file = 0
        GSM_A = []
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
                    GSM_A.append(float(row[GSM_A_column - 1]))  # ГСМ-А
                    # GSM_B.append(float(row[GSM_B_column - 1]))  # ГСМ-Б
                    Zadanie.append(float(row[Zadanie_column]))  # ОЗ ГСМ-А
                    if time_column > 0:
                        time.append(float(row[time_column - 1]))  # время из CSV, если есть колонка время
                    else:
                        temp_time.append(float(row[6]))  # время для расчета
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

        print('Колонка\t', ' ' * 20, '\tДлина массива')
        print('-'*30)
        print(name_column,  ' '*(35-len(name_column)), len(GSM_A))
        # print(name_column_2,' \t' * 2, len(GSM_B))
        print(name_column_3, ' '*(35-len(name_column_3)), len(Zadanie))
        print(name_column_4, ' '*(35-len(name_column_4)), len(time))
        print('Кол-во строк во всех СSV:', number_row_in_all_csv_file)
              # (0)    (1)     (2)     (3)
        return GSM_A, Zadanie, time, number_row_in_all_csv_file

    data_from_file = read_data_from_file(op, GSM_A_column, 'ГСМ-А.Текущее положение', Zadanie_column, 'Значение развертки. Положение ГСМ',
                                         time_column, 'time')

    # отрисовка окна для графиков
    fig = plt.figure(figsize=(6, 6))

    # отрисовка 1 графика
    ax = fig.add_subplot(211, facecolor='#FFFFCC')
    line, = ax.plot(data_from_file[2], data_from_file[0], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
    line1, = ax.plot(data_from_file[2], data_from_file[1], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
    # line2, = ax.plot(data_from_file[3], data_from_file[2], lw=1, color='black', label="Задание")   # задание
    ax.set_xlabel('Время, c')
    ax.set_ylabel('ГСМ, мм')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # шаг осей
    # ax.xaxis.set_major_locator(ticker.LinearLocator(10))
    # ax.xaxis.set_major_locator(ticker.MultipleLocator(30))

    # отрисовка легенды
    ax.legend((line, line1,), ('ГСМ', 'Задание'))

    # отрисовка 2 графика
    ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
    line02, = ax2.plot(data_from_file[2], data_from_file[0], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
    line12, = ax2.plot(data_from_file[2], data_from_file[1], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
    # line22, = ax2.plot(data_from_file[3], data_from_file[2], lw=1, color='black', label="Задание")   # задание
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
        thisy1 = np.array(data_from_file[1][indmin:indmax])    # новые данные для значений "Задание"
        # thisy2 = np.array(data_from_file[2][indmin:indmax])  # новые данные для значений "Задание"
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

    # функция - отображения графиков 2 чек-бокс
    def func_2(label):
        if label == 'ГСМ-А':
            line02.set_visible(not line02.get_visible())
        elif label == 'ГСМ-Б':
            line12.set_visible(not line12.get_visible())
        elif label == 'Задание':
            line22.set_visible(not line22.get_visible())
        plt.draw()

    with open(log_name, 'a', newline='') as csv_out:
        csv_out.write('время работы функции ШАГИ РБМК: %.2f cек\n' % float(time.time() - start_program))
    print('время работы функции ШАГИ РБМК: %.2f cек' % float(time.time() - start_program))

    plt.show()

if __name__ == '__main__':
    root = Tk()
    root.minsize()
    root.title('Скачки')

    # кнопка СКАЧКИ
    butSTEP = Button(root, text="Скачки/Шаги ", width=30)
    butSTEP.grid(row=0, column=0)
    butSTEP.bind('<ButtonRelease-1>', grath_stepper)

    root.mainloop()
