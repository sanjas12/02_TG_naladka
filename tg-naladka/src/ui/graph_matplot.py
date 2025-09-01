from pathlib import Path
import sys
import numpy as np
import random
from datetime import datetime, timedelta
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
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import COMMON_TIME, TICK_MARK_COUNT_X, TICK_MARK_COUNT_Y

class WindowGraph(QMainWindow):
    """
    Класс для отображения графиков данных с возможностью настройки.
    
    Args:
        data (pd.DataFrame): DataFrame с данными для построения графиков
        base_signals (List[str]): Список сигналов для основной оси Y
        secondary_signals (List[str]): Список сигналов для вторичной оси Y
        time_signals (str, optional): Название столбца для оси X. По умолчанию COMMON_TIME
        step (int, optional): Шаг выборки данных. По умолчанию 1
        filename (str, optional): Имя файла с данными для заголовка. По умолчанию None
    """
    
    def __init__(self, 
                 data: pd.DataFrame, 
                 base_signals: List[str], 
                 secondary_signals: List[str],
                 time_signals: str, 
                 step: int = 10, 
                 filename: Optional[str] = None) -> None:
        super().__init__()
        self.data = data
        self.base_signals = base_signals
        self.secondary_signals = secondary_signals
        self.time_signals = time_signals
        # print(f"{self.data=}")
        # print(f"{base_signals=}")
        # print(f"{secondary_signals=}")
        # print(f"{time_signals=}")
        self.label_list = []
        self.lines_list = []
        self.checkboxes = {}  # Словарь для хранения чекбоксов
        self.line_visibility = {}  # Словарь для отслеживания видимости линий
        self.step = int(step)
        self.filename = filename

        self.vline = None
        self.annotation = None
        self.cid = None
        self.ax1 = None
        self.ax2 = None
        
        # Цвета для графиков
        self.base_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                           '#9467bd', '#8c564b', '#e377c2']
        self.secondary_colors = ['#17becf', '#bcbd22', '#7f7f7f', 
                               '#aec7e8', '#ffbb78', '#98df8a']
        
        self.init_ui()
        self.plot_graphs()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle('Графики')
        # self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Панель настройки
        control_panel = QGroupBox("Панелль настройки")
        control_layout = QVBoxLayout()
            
            # GroupBox "Шаг выборки"
        sampling_group = QGroupBox('Шаг выборки')
        sampling_layout = QVBoxLayout()

        self.points_combobox = QComboBox()
        self.points_combobox.addItems(['1', '10', '100', '1000'])
        self.points_combobox.setCurrentText(str(self.step))
        
        self.points_all = QLabel(f'Кол-во исходных данных: {len(self.data)}')
        self.points_label = QLabel(f'Кол-во отображаемых данных: {len(self.data)//self.step}')
        
        update_button = QPushButton('Обновить графики')
        update_button.clicked.connect(self.update_graphs)
        
        sampling_layout.addWidget(self.points_combobox)
        sampling_layout.addWidget(self.points_all)
        sampling_layout.addWidget(self.points_label)
        sampling_layout.addWidget(update_button)

        sampling_group.setLayout(sampling_layout)

            # GroupBox "Видимость сигналов"
        visibility_group = QGroupBox("Видимость сигналов")
        visibility_layout = QVBoxLayout()

        scroll = QScrollArea()
        # scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        # scroll_layout = QVBoxLayout(scroll_content)
                
        if self.base_signals:    # Сначала добавляем чекбоксы для основной оси
            primary_label = QLabel("Основная ось:")
            visibility_layout.addWidget(primary_label)
            for signal in self.base_signals:
                cb = QCheckBox(signal)
                cb.setChecked(True)
                cb.stateChanged.connect(self.toggle_signal_visibility)
                visibility_layout.addWidget(cb)
                self.checkboxes[signal] = cb
                self.line_visibility[signal] = True
        
        if self.secondary_signals:  # Затем добавляем чекбоксы для вторичной оси
            secondary_label = QLabel("\nВспомогательная ось:")
            visibility_layout.addWidget(secondary_label)
            for signal in self.secondary_signals:
                cb = QCheckBox(signal)
                cb.setChecked(True)
                cb.stateChanged.connect(self.toggle_signal_visibility)
                visibility_layout.addWidget(cb)
                self.checkboxes[signal] = cb
                self.line_visibility[signal] = True
        
        # scroll_layout.addWidget(regulator_group)
        # scroll_layout.addStretch(1)  # Добавляем растягивающее пространство
        scroll.setWidget(scroll_content)
        visibility_layout.addWidget(scroll)
        visibility_group.setLayout(visibility_layout)
        
            # GroupBox для анализа регулятора
        regulator_group = QGroupBox("Анализ регулятора ГСМ")
        regulator_layout = QVBoxLayout()

        analyze_button = QPushButton("Анализ регулятора")
        analyze_button.clicked.connect(self.analyze_regulator)

        regulator_layout.addWidget(analyze_button)
        regulator_group.setLayout(regulator_layout)

        control_layout.addWidget(sampling_group)
        control_layout.addWidget(visibility_group)
        control_layout.addWidget(regulator_group)
        
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
        if isinstance(sender, QCheckBox):
            signal_name = sender.text()
            self.line_visibility[signal_name] = sender.isChecked()
            self.update_graphs()
        else:
            return

    def update_graphs(self) -> None:
        """Обновление графиков при изменении параметров."""
        self.step = int(self.points_combobox.currentText())
        self.points_label.setText(f'Кол-во отображаемых данных: {len(self.data)//self.step}')
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
        ax2 = None
        
        # Построение графиков основной оси
        if self.base_signals:
            for signal in self.base_signals:
                if signal in self.data.columns and self.line_visibility.get(signal, True):
                    line, = ax1.plot(self.data[self.time_signals][::self.step], 
                                   self.data[signal][::self.step], 
                                   lw=2, 
                                   label=signal)
                    self.lines_list.append(line)
            
            ax1.grid(linestyle='--', linewidth=0.5, alpha=.85)
            ax1.set_ylabel(',\n'.join([s for s in self.base_signals if self.line_visibility.get(s, True)]))
            ax1.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_X))
            ax1.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_Y))
            if any(self.line_visibility.get(s, False) for s in self.base_signals):
                ax1.legend(loc='upper left')
            ax1.set_xlabel(self.time_signals, loc='right')
        
        # Построение графиков вторичной оси
        if self.secondary_signals:
            ax2 = ax1.twinx()
            
            for i, signal in enumerate(self.secondary_signals):
                if signal in self.data.columns and self.line_visibility.get(signal, True):
                    line, = ax2.plot(self.data[self.time_signals][::self.step], 
                                    self.data[signal][::self.step], 
                                    ls='-.', 
                                    lw=2, 
                                    label=signal, 
                                    color=self.secondary_colors[i % len(self.secondary_colors)])
                    self.lines_list.append(line)
            
            visible_secondary = [s for s in self.secondary_signals if self.line_visibility.get(s, True)]
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
        self.ax2 = ax2  # Может быть None, если вторичной оси нет

        # Создаем вертикальную линию и аннотацию
        self.vline = self.ax1.axvline(x=0, color='k', lw=1, ls='--', visible=False)
        
        self.annotation = self.figure.text(
            0.75, 0.05, '',  # Переместим ниже
            transform=self.figure.transFigure,
            bbox=dict(boxstyle="round", fc="w", alpha=0.9, ec="0.5"),
            fontsize=8,
            fontfamily='monospace'  # Для лучшей читаемости числовых значений
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
        if x is None:
            self.vline.set_visible(False)
            self.annotation.set_visible(False)
            self.canvas.draw_idle()
            return

        x_series = self.data[self.time_signals]
        if len(x_series) == 0:
            return

        # Пытаемся привести X к числовому виду, иначе используем индексную систему координат
        idx = None
        vline_x = x
        try:
            x_numeric = pd.to_numeric(x_series, errors='coerce').to_numpy()
            if not np.isnan(x_numeric).all():
                idx = int(np.nanargmin(np.abs(x_numeric - x)))
                vline_x = x_numeric[idx]
        except Exception:
            idx = None

        if idx is None:
            idx = int(min(max(round(x), 0), len(x_series) - 1))

        x_val = x_series.iloc[idx]

        # Обновляем вертикальную линию
        self.vline.set_xdata([vline_x])
        self.vline.set_visible(True)

        # Формируем текст аннотации
        # text_lines = [f"Время: {x_val:.2f}"]  # Добавляем значение времени
        text_lines = [f"Время: {self.format_time(x_val)}"]  # Используем функцию форматирования
        for signal in self.base_signals + self.secondary_signals:
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

    def format_time(self, timestamp):
        """Форматирует время для отображения в аннотации"""
        if isinstance(timestamp, pd.Timestamp):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        if isinstance(timestamp, (int, float)):
            return str(timedelta(seconds=float(timestamp)))
        return str(timestamp)

    def analyze_regulator(self):
        """Обработчик нажатия кнопки анализа регулятора"""
        print("Запуск анализа регулятора...")

def main():
    
    df = pd.DataFrame()
    
    number_data = 10000

    x = np.linspace(0, 10, number_data)
    
    # Нууууууу Очень длинный сигнал
    first_signal = 'Нууууууу Очень длинный сигнал'
    noise_strength = 0.1
    clean_signal = np.piecewise(x, [x <= 8, x > 8], [250, lambda x: 250 - 2.5*(x - 8)])
    noise = np.random.normal(0, noise_strength, len(x))
    noisy_signal = clean_signal + noise
    df[first_signal] = noisy_signal 

    # Задание ГСМ - имитация,  как в каком-то САРЗе, кол-во скачков 26 
    reference_jump_values = [0, 10, 20, 10, 30, 10, 60, 10, 100, 110, 100, 120, 100, 150, 100, 200, 210, 
                200, 220, 200, 250, 200, 300, 320, 300, 10, 0]
    jump_times = np.linspace(0, 10, len(reference_jump_values), endpoint=False)
    step_graph = np.zeros_like(x)
    for _, (time, val) in enumerate(zip(jump_times, reference_jump_values)):
        step_graph[x >= time] = val  
    df['Задание. ГСМ-Б'] = step_graph

    # Положение ГСМ - имитация 
    T = 0.3  # Постоянная времени (сек)
    dt = 0.01  # Шаг дискретизации (сек)
    noise_std = 0.01 * np.max(reference_jump_values)  # Уровень шума (1%)
    
    # Инициализация
    real_position = np.zeros_like(x)
    current_ref = 0

    df['Положение. ГСМ-Б'] = step_graph

    # дополнительные графики
    df['ОЗ-А'] = [5 + random.randint(-1, 1) for _ in x]
    df['ОЗ-Б'] = [0 + random.randint(-1, 1) for _ in x]
    
    # время
    start_time = datetime.strptime("2018-03-09 14:29:18,560", "%Y-%m-%d %H:%M:%S,%f")
    timestamps = []
    for i in np.linspace(0, 100, number_data):
        delta = timedelta(seconds=float(i))
        new_time = start_time + delta
        # Форматирование с миллисекундами
        timestamps.append(new_time.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3])


    df[COMMON_TIME] = timestamps
    
    y1 = [first_signal, 'ГСМ-Б']
    y2 = ['ОЗ-А', 'ОЗ-Б']
    
    app = QApplication(sys.argv)
    window = WindowGraph(
        data=df, 
        base_signals=y1, 
        secondary_signals=y2, 
        time_signals=COMMON_TIME, 
        filename='E:/ТГ41-2021-06-25_134810_14099.csv.gz'
    )
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()