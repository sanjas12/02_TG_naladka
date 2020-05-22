import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

data = np.genfromtxt("TG12.csv", skip_header=2, delimiter=';')
time = data[:, 1]                           # массив данных из файла (второй столбец из tg.csv)
pressure = data[:, 40]       # массив данных из файла (второй столбец ГСМ-А)
pressure_2 = data[:, 41]     # ГСМ-Б

def data_gen(t=0):
    cnt = 0
    while True:
        cnt += 1
        print(time[cnt], pressure[cnt])
        yield time[cnt], pressure[cnt], pressure_2[cnt]

def init():
    ax.set_ylim(-1.1, 10)
    ax.set_xlim(0, 10)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
line_2, = ax.plot([], [], lw=1)
ax.grid()
xdata, ydata, y_2data = [], [], []

def run(data):
    # update the data
    t, y, y_2 = data         # data - выход фунции data_gen
    xdata.append(t)
    ydata.append(y)
    y_2data.append(y_2)
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    if t >= xmax:
        ax.set_xlim(xmin, 2 * xmax)
    if y >= ymax or y_2 >= ymax:
        ax.set_ylim(ymin, 2 * ymax)
        # ax.figure.canvas.draw()
    line.set_data(xdata, ydata)
    line_2.set_data(xdata,y_2data)
    return line,line_2

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=1,
repeat=False, init_func=init)

plt.show()
