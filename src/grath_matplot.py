import os
import sys
from typing import List, Optional
from PyQt5.QtWidgets import (
    QApplication, 
    QComboBox, 
    QHBoxLayout,
    QLabel,
    QGroupBox,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QMainWindow
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import random
import pandas as pd
from matplotlib.widgets import CheckButtons
import matplotlib.ticker as ticker
# Определяем путь к директории config в зависимости от текущего местоположения
# if getattr(sys, 'frozen', False):
#     # Если программа запущена как исполняемый файл
#     config_dir = os.path.join(os.path.dirname(sys.executable), 'config')
# else:
#     # Если программа запущена как скрипт
#     config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../config'))
# sys.path.append(config_dir)
from config.config import COMMON_TIME, TICK_MARK_COUNT_X, TICK_MARK_COUNT_Y


class WindowGrath(QMainWindow):
    """
    Класс для отображения графиков данных с возможностью настройки.
    
    Args:
        data (pd.DataFrame): DataFrame с данными для построения графиков
        base_axe (List[str]): Список сигналов для основной оси Y
        secondary_axe (List[str]): Список сигналов для вторичной оси Y
        x_axe (str, optional): Название столбца для оси X. По умолчанию COMMON_TIME
        step (int, optional): Шаг выборки данных. По умолчанию 1
        filename (str, optional): Имя файла с данными для заголовка. По умолчанию None
    """
    
    def __init__(self, 
                 data: pd.DataFrame, 
                 base_axe: List[str], 
                 secondary_axe: List[str],
                 x_axe: Optional[str] = None, 
                 step: int = 1, 
                 filename: Optional[str] = None) -> None:
        super().__init__()
        self.filename = filename
        self.data = data
        self.step = int(step)
        self.base_axe = base_axe
        self.secondary_axe = secondary_axe
        self.x_axe = x_axe or COMMON_TIME
        self.label_list = []
        self.lines_list = []
        
        # Цвета для графиков
        self.base_colors = ['b', 'g', 'r', 'c', 'm', 'purple', 'k']
        self.secondary_colors = self.base_colors[::-1]
        
        self.init_ui()
        self.plot_graphs()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle('Графики')
        self.setMinimumSize(800, 600)
        
        # Создаем основной виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Панель управления
        control_panel = QGroupBox("Управление")
        control_layout = QVBoxLayout()
        
        self.points_combobox = QComboBox()
        self.points_combobox.addItems(['1', '10', '100', '1000', '10000'])
        self.points_combobox.setCurrentText(str(self.step))
        
        self.points_label = QLabel(f'Всего точек: {len(self.data)}')
        
        update_button = QPushButton('Обновить графики')
        update_button.clicked.connect(self.update_graphs)
        
        control_layout.addWidget(QLabel('Шаг выборки:'))
        control_layout.addWidget(self.points_combobox)
        control_layout.addWidget(self.points_label)
        control_layout.addWidget(update_button)
        control_layout.addStretch()
        control_panel.setLayout(control_layout)
        
        # Панель с графиками
        graph_panel = QGroupBox("Графики")
        graph_layout = QVBoxLayout()
        
        self.figure = plt.figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        
        graph_layout.addWidget(self.canvas)
        graph_layout.addWidget(self.toolbar)
        graph_panel.setLayout(graph_layout)
        
        # Добавляем панели в основной layout
        main_layout.addWidget(control_panel, stretch=1)
        main_layout.addWidget(graph_panel, stretch=4)

    def update_graphs(self) -> None:
        """Обновление графиков при изменении параметров."""
        self.step = int(self.points_combobox.currentText())
        self.plot_graphs()
        self.canvas.draw()

    def set_line_visibility(self, label: str) -> None:
        """Переключение видимости линии графика по метке."""
        try:
            index = self.label_list.index(label)
            self.lines_list[index].set_visible(not self.lines_list[index].get_visible())
            self.canvas.draw()
        except ValueError:
            print(f"Метка {label} не найдена")

    def plot_graphs(self) -> None:
        """Построение графиков данных."""
        self.figure.clear()
        self.set_graph_title()
        
        if self.data.empty:
            self.figure.text(0.5, 0.5, 'Нет данных для отображения', 
                           ha='center', va='center')
            self.canvas.draw()
            return
            
        ax1 = self.figure.add_subplot()
        
        # Построение графиков основной оси
        if self.base_axe:
            for signal in self.base_axe:
                if signal in self.data.columns:
                    ax1.plot(self.data[self.x_axe][::self.step], 
                            self.data[signal][::self.step], 
                            lw=2, 
                            label=signal)
            
            ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)
            ax1.set_ylabel(',\n'.join(self.base_axe))
            ax1.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_X))
            ax1.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_Y))
            ax1.legend(loc='upper left')
            ax1.set_xlabel(self.x_axe, loc='right')
        
        # Построение графиков вторичной оси
        if self.secondary_axe:
            ax2 = ax1.twinx()
            
            for i, signal in enumerate(self.secondary_axe):
                if signal in self.data.columns:
                    ax2.plot(self.data[self.x_axe][::self.step], 
                            self.data[signal][::self.step], 
                            ls='-.', 
                            lw=2, 
                            label=signal, 
                            color=self.secondary_colors[i % len(self.secondary_colors)])
            
            ax2.tick_params(axis='y', labelcolor='b')
            ax2.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_X))
            ax2.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_Y))
            ax2.set_ylabel(f',\n'.join(self.secondary_axe), color='b')
            ax2.legend(loc='upper right')
        
        # Поворот меток оси X
        for tick in ax1.get_xticklabels():
            tick.set_rotation(15)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def set_graph_title(self) -> None:
        """Установка заголовка графика на основе имени файла."""
        if not self.filename:
            title = 'Не выбран файл с данными'
        else:
            # Определение типа данных по имени файла
            if 'ШУР' in self.filename:
                index = self.filename.rfind('ШУР')
                title = f'ТГ:{self.filename[index+3]}, Канал:{self.filename[index+4]}'
            elif 'ШСП' in self.filename:
                index = self.filename.rfind('ШСП')
                title = f'ШСП:{self.filename[index+3]}, Канал:{self.filename[index+4]}'
            elif 'ТГ' in self.filename:
                index = self.filename.rfind('ТГ')
                title = f'ТГ:{self.filename[index+2]}, Канал:{self.filename[index+3]}'
            else:
                title = 'Тестовый файл'
            
            title += f', Точки: {len(self.data)//self.step}'
        
        self.figure.suptitle(title, y=1.02)

def main():
    """Функция для тестирования класса WindowGrath."""
    df = pd.DataFrame()
    number_point = 15
    first_signal = 'ГСМ-А. Очень длинный сигнал'
    
    # Генерация тестовых данных
    df[first_signal] = [random.randint(300, 321) for _ in range(number_point)]
    df['ГСМ-Б'] = [random.randint(300, 321) for _ in range(number_point)]
    df['ОЗ-А'] = [random.random() for _ in range(number_point)]
    df['ОЗ-Б'] = [random.random() for _ in range(number_point)]
    df[COMMON_TIME] = [i for i in range(number_point)]
    
    y1 = ['ОЗ-А', 'ОЗ-Б']
    y2 = [first_signal, 'ГСМ-Б']
    
    app = QApplication(sys.argv)
    window = WindowGrath(
        df, 
        base_axe=y1, 
        secondary_axe=y2, 
        x_axe=COMMON_TIME, 
        filename='E:/ТГ41-2021-06-25_134810_14099.csv.gz'
    )
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()