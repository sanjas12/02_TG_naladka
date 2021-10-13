import numpy as np
import matplotlib.pyplot as plt
import time
#import mplcursors
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Cursor
from matplotlib.widgets import SpanSelector

start_program = time.time()

# присвоение номеров колонок из файла TG.csv
GSM_A_column = 39
GSM_B_column = 40
time_column = 1       #  если есть колонка которая специально подготовлена в EXCEL
Zadanie_column = 60

data = np.genfromtxt("TG12.csv", skip_header=1, delimiter=';')
GSM_A = data[:, GSM_A_column]  # массив данных из файла TG.csv (39 столбец  - ГСМ-А)
GSM_B = data[:, GSM_B_column]
time_d = data[:, time_column]
time_to_function = data[:, time_column]
Zadanie = data[:, Zadanie_column]

# функция создание колонки time
def time_column():
    time_column_new = []
    i = 0
    for zz in time_to_function:
        if i==0:
            time_column_new.append(0)
        else:
            time_column_new.append(time_to_function[i]-time_to_function[i-1])
        i = i + 1
    return time_column_new

# функция создание массива "реальных" данных ГСМ-А без учета простоя ГСМ
def real_GSM():
    i = 0
    shift = 30       # смещение
    for zz in range(len(GSM_A)):
        if float(GSM_A[i+1])-float(GSM_A[i]) == 0:
            # print(GSM_A[i], GSM_A[i+1], )
            i = i + 1
        else:
            break
    real_GSM_A = GSM_A[i - shift:len(GSM_A)]
    real_GSM_B = GSM_B[i - shift:len(GSM_A)]
    real_Zadanie = Zadanie[i - shift:len(GSM_A)]
    time_2 = time_d[i-shift:len(GSM_A)]
    print('количество исходных строчек: ', len(GSM_A))
    print('номер строки с которой начинается изменения ГСМ:', i - 1)
    print('количество строчек для графиков: ', len(real_GSM_A))
    return time_2, real_GSM_A, real_GSM_B, real_Zadanie

dataf = real_GSM()  # выход функции real_GSM - реальные данные массива

# отрисовка окна для графиков
fig = plt.figure(figsize=(6, 6))

# отрисовка 1 графика
ax = fig.add_subplot(211, facecolor='#FFFFCC')
line, = ax.plot(dataf[0], dataf[1], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
line1, = ax.plot(dataf[0], dataf[2], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
line2, = ax.plot(dataf[0], dataf[3], lw=1, color='black', label="Задание")   # задание
ax.set_xlabel('Время, c')
ax.set_ylabel('ГСМ, мм')
ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
fig.legend((line, line1, line2), ('ГСМ-А', 'ГСМ-Б', 'Задание'), bbox_to_anchor=(0.3, 1))  # надпись названия графиков

# отрисовка 2 графика
ax2 = fig.add_subplot(212, facecolor='#FFFFCC')
line02, = ax2.plot(dataf[0], dataf[1], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
line12, = ax2.plot(dataf[0], dataf[2], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
line22, = ax2.plot(dataf[0], dataf[3], lw=1, color='black', label="Задание")   # задание
ax2.set_xlabel('Время, c')
ax2.set_ylabel('ГСМ, мм')
ax2.grid(linestyle='--', linewidth=0.5, alpha=.85)

# функция выделения
def onselect(xmin, xmax):
    indmin, indmax = np.searchsorted(dataf[0], (xmin, xmax))  # получение минимального и максимального
                                                              # элемента для значений "время"
    # print (indmin,indmax)
    indmax = min(len(dataf[0]) - 1, indmax)
    thisx = dataf[0][indmin:indmax]             # новые данные для значений "время"
    # print (len(thisx))
    thisx_new = []                              # формирование нового массива значений "время"
    for zz in range(len(thisx)):
        # print (zz*0.01)
        thisx_new.append(zz*0.01)
    # print(len(thisx_new))
    thisy0 = dataf[1][indmin:indmax]            # новые данные для значений "ГСМ-А"
    thisy1 = dataf[2][indmin:indmax]            # новые данные для значений "ГСМ-А"
    thisy2 = dataf[3][indmin:indmax]             # новые данные для значений "Задание"
    line02.set_data(thisx_new, thisy0)               # перерисовка графика Задание
    line12.set_data(thisx_new, thisy1)               # перерисовка графика Задание
    line22.set_data(thisx_new, thisy2)               # перерисовка графика Задание
    ax2.set_xlim(thisx_new[0], thisx_new[-1])           # перерисовка масштаба осей X
    ax2.set_ylim(thisy2.min()-1, thisy2.max()+1)      # перерисовка масштаба осей Y от Задания
    fig.canvas.draw()

# set useblit True on gtkagg for enhanced performance
span = SpanSelector(ax, onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.5, facecolor='red'))

# создание курсоров для графика (ГСМ-А, ГСМ-Б, Задание)
#mplcursors.cursor(line)
#mplcursors.cursor(line1)
#mplcursors.cursor(line2)

#my_filename = "TG12_2.csv"

# функция - перестройки csv файла
def perestroika_csv():
    # так открывать файл лучше, через open в питон для ардуино стр.150
    # создание строки с добавление новой колонки 't'
    with open(my_filename, 'r') as my_csv:
        for row in my_csv:
            data_header = row
            data_header = data_header.split(';')
            print(data_header)
            print(type(data_header))
            print(len(data_header))
            data_header.insert(1, 't')
            print(data_header)
            print(len(data_header))
            break
    my_filename_out = 'TG_out.csv'
    # открыть файл csv для
    # with open(my_filename_out, 'w', newline='') as my_csv:

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

#  курсор
cursor = Cursor(ax2, useblit=True, horizOn=False, color='red', linewidth=2)

print('время работы программы: %.2f cек' %float(time.time()-start_program))

plt.show()