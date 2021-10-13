import numpy as np
import matplotlib.pyplot as plt
import time
#import mplcursors
from matplotlib.widgets import CheckButtons
from matplotlib.widgets import Cursor

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

fig, ax = plt.subplots()
line, = ax.plot(dataf[0], dataf[1], lw=2,  color='b', label="ГСМ-А")       # ГСМ-А
line1, = ax.plot(dataf[0], dataf[2], lw=2, color='r', label="ГСМ-Б")       # ГСМ-Б
line2, = ax.plot(dataf[0], dataf[3], lw=1, color='black', label="Задание")   # задание
ax.set_xlabel('Время, c')
ax.set_ylabel('ГСМ, мм')
ax.grid(linestyle='--', linewidth=0.5, alpha=.85)
fig.legend((line, line1, line2), ('ГСМ-А', 'ГСМ-Б', 'Задание'), bbox_to_anchor=(0.3, 0.88))  # надпись названия графиков

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

# функция - отображения графиков
def func(label):
    if label == 'ГСМ-А':
        line.set_visible(not line.get_visible())
    elif label == 'ГСМ-Б':
        line1.set_visible(not line1.get_visible())
    elif label == 'Задание':
        line2.set_visible(not line2.get_visible())
    plt.draw()

# работа со списком чек-боксов отображающих графики
rax = plt.axes([0.05, 0.4, 0.1, 0.15])
check = CheckButtons(rax, ('ГСМ-А', 'ГСМ-Б', 'Задание'), (True, True, True))
check.on_clicked(func)

cursor = Cursor(ax, useblit=True, horizOn=False, color='red', linewidth=2)

print('время работы программы: %.2f cек' %float(time.time()-start_program))

plt.show()