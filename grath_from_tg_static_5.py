from tkinter import filedialog as fd
import pandas as pd
import time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import SpanSelector
from tkinter.filedialog import *

# функция построения графика "шаги\скачки\степпера"
def grath_stepper(event):

    GSM_A_column = 'ГСМ-А.Текущее положение'  # ГСМ-А.Текущее положение
    GSM_B_column = 'ГСМ-Б.Текущее положение'  # ГСМ-Б.Текущее положение
    Zadanie_column = 'Значение развертки. Положение ГСМ'   # Значение развертки. Положение ГСМ
    time_column = 'миллисекунды'   # время

    fields = [GSM_A_column, GSM_B_column, Zadanie_column, time_column]

    opened_csv_files = fd.askopenfiles(title='Открыть CSV файл с ШАГАМИ', filetypes=[('CSV files', '*.csv'), ], initialdir='')

    # определение номера канала из названия файла
    name_ch = str(opened_csv_files)
    name_temp = name_ch = name_ch.split('/')
    if int(name_ch[len(name_ch) - 1][3]) == 1:
        name_ch = '1 канал'
    else:
        name_ch = '2 канал'

    # определение номера ТГ из названия файла
    name_TG = int(name_temp[len(name_temp) - 1][2])

    time_data = []

    for file_ in opened_csv_files:
        df = pd.read_csv(file_, header=0, delimiter=';', usecols=fields)

    # поиск количества строк
    num_rows = len(df.index)

    # довабление новой колонки Время
    # df['time'] = None
    # print(df.head)

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
    point_f = 1

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(211, facecolor='#FFFFCC')
    line, = ax.plot(time_data[1::point_f], df[GSM_A_column][1::point_f],
                    linewidth=2, color='b', label="ГСМ-А")  # ГСМ-А
    line1, = ax.plot(time_data[1::point_f], df[GSM_B_column][1::point_f],
                     linewidth=2, color='r', label="ГСМ-Б")  # ГСМ-Б
    line2, = ax.plot(time_data[1::point_f], df[Zadanie_column][1::point_f],
                     lw=1, color='black', label="Задание")  # Задание

    ax.set_xlabel('Время, c')
    ax.set_ylabel('ГСМ, мм')
    ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
    plt.title('ТГ-' + str(name_TG) +', ' + str(name_ch), fontsize='large')

    # отрисовка легенды
    fig.legend((line, line1, line2), ('ГСМ-А', 'ГСМ-Б', 'Задание'))

    # отрисовка 2 графика
    ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
    line02, = ax2.plot(time_data[1::point_f], df[GSM_A_column][1::point_f], lw=2, color='b', label="ГСМ-А")  # ГСМ-А
    line12, = ax2.plot(time_data[1::point_f], df[GSM_B_column][1::point_f], lw=2, color='r', label="ГСМ-Б")  # ГСМ-Б
    line22, = ax2.plot(time_data[1::point_f], df[Zadanie_column][1::point_f], lw=1, color='black', label="Задание")  # задание
    ax2.set_xlabel('Время, c')
    ax2.set_ylabel('ГСМ, мм')
    ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)

    # функция выделения_старая
    def onselect(xmin, xmax):
        print('*'*20)
        print('от курсора', xmin, xmax)
        indmin, indmax = np.searchsorted(time_data,
                                         (float(xmin), float(xmax)))  # получение минимального и максимального
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
        line12.set_data(thisx_new, thisy1)               # перерисовка графика "ГСМ-Б"
        line22.set_data(thisx_new, thisy2)               # перерисовка графика Задание
        print(thisx_new[0], thisx_new[-1])
        ax2.set_xlim(thisx_new[0], thisx_new[-1])  # перерисовка масштаба осей X
        ax2.set_ylim(thisy2.min() - 1, thisy2.max() + 1)  # перерисовка масштаба осей Y от Задания
        print('*' * 20)
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
    rax = plt.axes([0.0, 0.5, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
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
    rax_2 = plt.axes([0.0, 0.01, 0.1, 0.08])  # положение чекбокса - x,y, х1,y1 - размер окна
    check_2 = CheckButtons(rax_2, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
    check_2.on_clicked(func_2)

    plt.show()

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

    root.mainloop()
