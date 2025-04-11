import os
import sys
import numpy as np
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
    QMainWindow,
    QCheckBox,
    QScrollArea
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
        self.checkboxes = {}  # Словарь для хранения чекбоксов
        self.line_visibility = {}  # Словарь для отслеживания видимости линий

        self.vline = None
        self.annotation = None
        self.cid = None
        self.ax1 = None
        self.ax2 = None
        
        self.base_colors = ['b', 'g', 'r', 'c', 'm', 'purple', 'k']
        self.secondary_colors = self.base_colors[::-1]
        
        self.init_ui()
        self.plot_graphs()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle('Графики')
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Панель управления
        control_panel = QGroupBox("Управление")
        control_layout = QVBoxLayout()
        
        self.points_combobox = QComboBox()
        self.points_combobox.addItems(['10', '100', '1000'])
        self.points_combobox.setCurrentText(str(self.step))
        
        self.points_label = QLabel(f'Всего точек: {len(self.data)}')
        
        update_button = QPushButton('Обновить графики')
        update_button.clicked.connect(self.update_graphs)
        
        # Создаем область с прокруткой для чекбоксов
        scroll = QScrollArea()
        # scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # Добавляем чекбоксы для сигналов
        self.signals_group = QGroupBox("Видимость сигналов")
        self.signals_layout = QVBoxLayout()
        
        # Сначала добавляем чекбоксы для основной оси
        if self.base_axe:
            primary_label = QLabel("Основная ось:")
            self.signals_layout.addWidget(primary_label)
            for signal in self.base_axe:
                cb = QCheckBox(signal)
                cb.setChecked(True)
                cb.stateChanged.connect(self.toggle_signal_visibility)
                self.signals_layout.addWidget(cb)
                self.checkboxes[signal] = cb
                self.line_visibility[signal] = True
        
        # Затем добавляем чекбоксы для вторичной оси
        if self.secondary_axe:
            secondary_label = QLabel("\nВторичная ось:")
            self.signals_layout.addWidget(secondary_label)
            for signal in self.secondary_axe:
                cb = QCheckBox(signal)
                cb.setChecked(True)
                cb.stateChanged.connect(self.toggle_signal_visibility)
                self.signals_layout.addWidget(cb)
                self.checkboxes[signal] = cb
                self.line_visibility[signal] = True
        
        self.signals_group.setLayout(self.signals_layout)
        scroll_layout.addWidget(self.signals_group)
        scroll.setWidget(scroll_content)
        
        control_layout.addWidget(QLabel('Шаг выборки:'))
        control_layout.addWidget(self.points_combobox)
        control_layout.addWidget(self.points_label)
        control_layout.addWidget(update_button)
        control_layout.addWidget(scroll)
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
        
        main_layout.addWidget(control_panel, stretch=1)
        main_layout.addWidget(graph_panel, stretch=4)

    def toggle_signal_visibility(self, state: int) -> None:
        """Переключение видимости сигнала при изменении состояния чекбокса."""
        sender = self.sender()
        signal_name = sender.text()
        self.line_visibility[signal_name] = sender.isChecked()
        self.update_graphs()

    def update_graphs(self) -> None:
        """Обновление графиков при изменении параметров."""
        self.step = int(self.points_combobox.currentText())
        self.plot_graphs()
        self.canvas.draw()

    def plot_graphs(self) -> None:
        """Построение графиков данных с учетом видимости сигналов."""
        self.figure.clear()
        self.set_graph_title()
        
        if self.data.empty:
            self.figure.text(0.5, 0.5, 'Нет данных для отображения', 
                           ha='center', va='center')
            self.canvas.draw()
            return
            
        ax1 = self.figure.add_subplot()
        self.lines_list = []  # Очищаем список линий
        
        # Построение графиков основной оси
        if self.base_axe:
            for signal in self.base_axe:
                if signal in self.data.columns and self.line_visibility.get(signal, True):
                    line, = ax1.plot(self.data[self.x_axe][::self.step], 
                                   self.data[signal][::self.step], 
                                   lw=2, 
                                   label=signal)
                    self.lines_list.append(line)
            
            ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)
            ax1.set_ylabel(',\n'.join([s for s in self.base_axe if self.line_visibility.get(s, True)]))
            ax1.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_X))
            ax1.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_Y))
            if any(self.line_visibility.get(s, False) for s in self.base_axe):
                ax1.legend(loc='upper left')
            ax1.set_xlabel(self.x_axe, loc='right')
        
        # Построение графиков вторичной оси
        if self.secondary_axe:
            ax2 = ax1.twinx()
            
            for i, signal in enumerate(self.secondary_axe):
                if signal in self.data.columns and self.line_visibility.get(signal, True):
                    line, = ax2.plot(self.data[self.x_axe][::self.step], 
                                    self.data[signal][::self.step], 
                                    ls='-.', 
                                    lw=2, 
                                    label=signal, 
                                    color=self.secondary_colors[i % len(self.secondary_colors)])
                    self.lines_list.append(line)
            
            visible_secondary = [s for s in self.secondary_axe if self.line_visibility.get(s, True)]
            if visible_secondary:
                ax2.tick_params(axis='y', labelcolor='b')
                ax2.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_X))
                ax2.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_Y))
                ax2.set_ylabel(f',\n'.join(visible_secondary), color='b')
                ax2.legend(loc='upper right')
        
        # Поворот меток оси X
        for tick in ax1.get_xticklabels():
            tick.set_rotation(15)
        
        self.figure.tight_layout()
        self.canvas.draw()

        self.ax1 = ax1  # Сохраняем ссылку на основную ось
        if self.secondary_axe:
            self.ax2 = ax2  # Сохраняем ссылку на вторичную ось
        else:
            self.ax2 = None

        # Создаем вертикальную линию и аннотацию
        self.vline = self.ax1.axvline(x=0, color='k', lw=1, ls='--', visible=False)
        self.annotation = self.figure.text(
            0.75, 0.1, '', 
            transform=self.figure.transFigure,
            bbox=dict(boxstyle="round", fc="w", alpha=0.9),
            fontsize=8
        )
        self.annotation.set_visible(False)

        # Подключаем обработчик движения мыши
        if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
        self.cid = self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)


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


    def on_mouse_move(self, event):
        if self.vline is None or self.annotation is None:
            return

        # Проверяем, находится ли курсор в области графика
        axes = [self.ax1]
        if self.ax2 is not None:
            axes.append(self.ax2)
        if event.inaxes not in axes:
            self.vline.set_visible(False)
            self.annotation.set_visible(False)
            self.canvas.draw_idle()
            return

        # Находим ближайшую точку данных
        x = event.xdata
        x_data = self.data[self.x_axe].values
        if len(x_data) == 0:
            return
        idx = np.abs(x_data - x).argmin()
        x_val = x_data[idx]

        # Обновляем вертикальную линию
        self.vline.set_xdata([x_val])
        self.vline.set_visible(True)

        # Формируем текст аннотации
        text_lines = []
        for signal in self.base_axe + self.secondary_axe:
            if signal in self.data.columns and self.line_visibility.get(signal, False):
                y_val = self.data[signal].iloc[idx]
                text_lines.append(f'{signal}: {y_val:.2f}')

        # Обновляем аннотацию
        if text_lines:
            self.annotation.set_text('\n'.join(text_lines))
            self.annotation.set_visible(True)
        else:
            self.annotation.set_visible(False)

        self.canvas.draw_idle()

def main():
    
    df = pd.DataFrame()
    number_point = 15
    first_signal = 'ГСМ-А. Очень длинный сигнал'
    
    
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