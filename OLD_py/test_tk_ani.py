import matplotlib.pyplot as plt
from tkinter.filedialog import *    # для окна приложения и для TK()
from matplotlib.figure import Figure
from numpy import arange
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt                  # для анимации
import matplotlib.animation as animation            # для анимации
import numpy as np
import time

# создание окна программы
root = Tk()
root.minsize(width=800, height=400)
root.title('ПТИ_tk')

# f = Figure(figsize=(1, 1), dpi=100)
# a = f.add_subplot(111)              # размер 111- размер в попугаях
# t = arange(0.0, 3.0, 0.01)        # от 0 до 3 с шагом 0.01
# s = 2*t                           # функция для отображения

# создаине 1 и 2 графика
fig, ax = plt.subplots()                #
line, = ax.plot([], [], color='blue', ls='solid', lw=1.5)
line_2, = ax.plot([], [], color='red', ls='solid', lw=1.5)      # вид, тип , цвет графика lw=2 - толшина линии
ax.grid()                                           # отрисовка сетки
ax.set_title('Tk embedding')                 # название графика
ax.set_xlabel('время')                       # название оси
ax.set_ylabel('температура')

xdata, ydata = [], []                   # массив данных для X и Y для 1 графика
xdata_2, ydata_2 = [], []               # массив данных для X и Y для 2 графика


# отрисовка осей и подписей к ним
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.show()
canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)   # положение окна с осями

# отрисовка инструментов для работы с графикой
toolbar = NavigationToolbar2TkAgg(canvas, root)
toolbar.update()
canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

# функция закрытия приложения
def quit():
    root.quit()  # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

# функция генерации данных для графика
def data_gen(t=0):
    cnt = 0
    while cnt < 1000:
        time.sleep(1)
        cnt += 1
        cnt = np.random.randint(0, 30)
        cnt_2 = np.random.randint(20, 80)
        t += 0.5
        # yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)
        yield t, cnt, cnt_2,

# функция для начального состояния графика
def init():
    ax.set_ylim(0, 100)                 # лимиты по оси Y
    ax.set_xlim(0, 60)                 # лимиты по оси Y
    del xdata[:]                        # очистка массива исходных данных для X для 1 графика
    del ydata[:]                        # очистка массива исходных данных для Y для 1 графика
    del xdata_2[:]                      # очистка массива исходных данных для X для 2 графика
    del ydata_2[:]                      # очистка массива исходных данных для Y для 2 графика
    line.set_data(xdata, ydata)         # в качестве данных для 1 графика будут xdata и ydata
    line_2.set_data(xdata_2, ydata_2)     # в качестве данных для 1 графика будут xdata и ydata
    return line, line_2,

# функция для обновления графика
def run(data):
    # update the data
    t, y, y_2 = data
    xdata.append(t)
    ydata.append(y)
    xdata_2.append(t)
    ydata_2.append(y_2)
    xmin, xmax = ax.get_xlim()              # изменение масштаба по оси Х во времени
    if t >= xmax:
        ax.set_xlim(xmin+60, xmax+60)
        ax.figure.canvas.draw()
    line.set_data(xdata, ydata)
    line_2.set_data(xdata_2, ydata_2)
    return line, line_2,

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=100,
                              repeat=False, init_func=init)

# вывод кнопки Закрыть  в окно приложения
B1 = Button(master=root, text='Закрыть', command=quit)
B1.place(x=150, y=120)

# plt.show()

root.mainloop()
