from __future__ import annotations
import sys
import os
import random
from pathlib import Path
from typing import List, Optional, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

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
    QScrollArea,
)
from PyQt5.QtCore import Qt

import pyqtgraph as pg

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (
    COMMON_TIME, GSM_A_CUR, GSM_B_CUR, ANALYS_AIM, REPORT_DIR, PLOT_FILENAME
)
from logic.regulator_analyzer import RegulatorAnalyzer


class WindowGraph(QMainWindow):
    """
    Класс для отображения графиков данных с возможностью настройки.
    Заменён matplotlib на pyqtgraph.

    Args:
        data: DataFrame с данными для построения графиков.
        selected_signals: Список сигналов для основной оси Y.
        time_signal: Название столбца для оси X.
        filenames: Список имён файлов с данными для вставки в отчет.
        step: Шаг выборки данных. По умолчанию 10.
        enable_analys: Можно ли активировать кнопку "АНАЛИЗА"
    """

    def __init__(
        self,
        data: pd.DataFrame,
        selected_signals: List[str],
        time_signal: str,
        filenames: List[str],
        step: int = 10,
        enable_analys: bool = False,
    ) -> None:
        super().__init__()
        self.data = data
        self.selected_signals = selected_signals
        self.time_signal = time_signal
        self.step = int(step)
        self.filenames = filenames
        self.enable_analys = enable_analys

        if self.enable_analys:
            self.analyzer = RegulatorAnalyzer(
                self.data[COMMON_TIME].to_numpy(),
                self.data[GSM_A_CUR].to_numpy(),
                self.data[GSM_B_CUR].to_numpy(),
                self.data[ANALYS_AIM].to_numpy(),
                self.filenames,
            )

        # Структуры для линий и видимости
        self.lines: Dict[str, pg.PlotDataItem] = {}
        self.line_visibility: Dict[str, bool] = {}
        self.checkboxes: Dict[str, QCheckBox] = {}

        # pyqtgraph элементы
        self.plot_widget: Optional[pg.GraphicsLayoutWidget] = None
        self.plot_item: Optional[pg.PlotItem] = None  # основная PlotItem
        self.secondary_view: Optional[pg.ViewBox] = None  # вторичный ViewBox
        self.vline: Optional[pg.InfiniteLine] = None
        self.annotation: Optional[pg.TextItem] = None
        self.saved_plot_path: Optional[str] = None

        # Цвета (hex) — подбираются для pyqtgraph
        self.base_colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", 
            "#9467bd", "#8c564b", "#e377c2"
        ]
        self.secondary_colors = [
            "#17becf", "#bcbd22", "#7f7f7f", 
            "#aec7e8", "#ffbb78", "#98df8a"
        ]

        self.init_ui()
        self.plot_graphs()
        self._save_plot()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса с использованием pyqtgraph."""
        self.setWindowTitle("Графики")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Панель настройки
        control_panel = QGroupBox("Панель настройки")
        control_layout = QVBoxLayout()

        # GroupBox "Шаг выборки"
        sampling_group = self._create_sampling_group()
        # GroupBox "Видимость сигналов"
        visibility_group = self._create_visibility_group()
        # GroupBox для анализа регулятора
        regulator_group = self._create_regulator_group()

        control_layout.addWidget(sampling_group, stretch=1)
        control_layout.addWidget(visibility_group, stretch=6)
        control_layout.addWidget(regulator_group, stretch=1)
        control_panel.setLayout(control_layout)

        # Панель с графиками (pyqtgraph)
        graph_panel = self._create_graph_panel()
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.plot_widget)
        graph_panel.setLayout(graph_layout)

        main_layout.addWidget(control_panel, stretch=1)
        main_layout.addWidget(graph_panel, stretch=4)

    def _create_sampling_group(self) -> QGroupBox:
        """Создает группу настроек выборки данных."""
        sampling_group = QGroupBox("Шаг выборки")
        sampling_layout = QVBoxLayout()
        
        self.points_combobox = QComboBox()
        self.points_combobox.addItems(["1", "10", "100", "1000"])
        self.points_combobox.setCurrentText(str(self.step))
        
        self.points_all = QLabel(f"Кол-во исходных данных: {len(self.data)}")
        self.points_label = QLabel(
            f"Кол-во отображаемых данных: {len(self.data) // self.step}"
        )
        
        update_button = QPushButton("Обновить графики")
        update_button.clicked.connect(self.update_graphs)
        
        sampling_layout.addWidget(self.points_combobox)
        sampling_layout.addWidget(self.points_all)
        sampling_layout.addWidget(self.points_label)
        sampling_layout.addWidget(update_button)
        sampling_group.setLayout(sampling_layout)
        
        return sampling_group

    def _create_visibility_group(self) -> QScrollArea:
        """Создает группу видимости сигналов со скроллом."""
        visibility_group = QGroupBox("Видимость сигналов")
        visibility_layout = QVBoxLayout()
        self._add_signal_checkboxes(visibility_layout)
        visibility_layout.addStretch()
        visibility_group.setLayout(visibility_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(visibility_group)
        
        return scroll_area

    def _create_regulator_group(self) -> QGroupBox:
        """Создает группу анализа регулятора."""
        regulator_group = QGroupBox("Анализ регулятора ГСМ")
        regulator_layout = QVBoxLayout()
        
        analyze_button = QPushButton("Анализ регулятора")
        analyze_button.setEnabled(self.enable_analys)
        analyze_button.clicked.connect(self.analyze_regulator)
        
        regulator_layout.addWidget(analyze_button)
        regulator_group.setLayout(regulator_layout)
        
        return regulator_group

    def _create_graph_panel(self) -> QGroupBox:
        """Создает панель с графиками."""
        graph_panel = QGroupBox("Графики")
        
        # GraphicsLayoutWidget позволяет иметь несколько ViewBox-ов
        self.plot_widget = pg.GraphicsLayoutWidget()
        self._setup_plot_widget()
        
        return graph_panel

    def _setup_plot_widget(self) -> None:
        """Настраивает виджет графика."""
        if self.plot_widget is None:
            return
            
        self.plot_widget.setBackground('w')
        
        # Создаём PlotItem (ось X общая)
        self.plot_item = self.plot_widget.addPlot(row=0, col=0)
        
        # Устанавливаем белый фон для ViewBox графика
        if self.plot_item.getViewBox():
            self.plot_item.getViewBox().setBackgroundColor('w')
        
        self.plot_item.showGrid(x=True, y=True, alpha=0.6)
        self.plot_item.setLabel("bottom", self.time_signal)

        # Инструменты аннотации
        self.vline = pg.InfiniteLine(
            angle=90, movable=False, 
            pen=pg.mkPen("k", style=Qt.DashLine)
        )
        self.plot_item.addItem(self.vline)
        self.vline.hide()

        self.annotation = pg.TextItem(
            anchor=(0, 1), border=pg.mkPen(0.5), 
            fill=(255, 255, 255, 200), color='k'
        )
        self.plot_item.addItem(self.annotation)
        self.annotation.hide()

        # подписка на события мыши
        proxy = pg.SignalProxy(
            self.plot_item.scene().sigMouseMoved, 
            rateLimit=60, 
            slot=self.on_mouse_move
        )

    def _add_signal_checkboxes(self, layout: QVBoxLayout) -> None:
        """Добавляет чекбоксы для сигналов основной и вторичной осей."""
        if self.selected_signals:
            layout.addWidget(QLabel("Сигналы:"))
            for signal in self.selected_signals:
                cb = QCheckBox(signal)
                cb.setChecked(True)
                cb.stateChanged.connect(self.toggle_signal_visibility)
                layout.addWidget(cb)
                self.checkboxes[signal] = cb
                self.line_visibility[signal] = True

    def toggle_signal_visibility(self, state: int) -> None:
        """Переключение видимости сигнала при изменении состояния чекбокса."""
        sender = self.sender()
        if isinstance(sender, QCheckBox):
            signal_name = sender.text()
            self.line_visibility[signal_name] = sender.isChecked()
            self.update_graphs()

    def update_graphs(self) -> None:
        """Обновление графиков при изменении параметров."""
        self.step = int(self.points_combobox.currentText())
        self.points_label.setText(
            f"Кол-во отображаемых данных: {max(1, len(self.data) // self.step)}"
        )
        self.plot_graphs()
        self._save_plot()

    def plot_graphs(self) -> None:
        """Построение графиков данных с учетом видимости сигналов (pyqtgraph)."""
        if self.plot_item is None:
            return
            
        # очистка предыдущих линий
        self.plot_item.clear()
        self._setup_plot_style()
        
        if self.data.empty:
            # показать текст вместо графика
            label = pg.TextItem(
                "Нет данных для отображения", 
                anchor=(0.5, 0.5), color='k'
            )
            self.plot_item.addItem(label)
            return

        # X используем индекс
        indices = np.arange(0, len(self.data), self.step, dtype=int)

        # Основные сигналы
        self.lines.clear()
        for i, signal in enumerate(self.selected_signals):
            if signal in self.data.columns and self.line_visibility.get(signal, True):
                y_data = self._get_signal_data(signal)
                pen = pg.mkPen(
                    color=self.base_colors[i % len(self.base_colors)], 
                    width=2
                )
                plotdata = self.plot_item.plot(indices, y_data, pen=pen, name=signal)
                self.lines[signal] = plotdata

        # Настройки легенды / подписи осей
        visible_main = [
            s for s in self.selected_signals 
            if self.line_visibility.get(s, False) and s in self.data.columns
        ]
        if visible_main:
            self.plot_item.getAxis("left").setLabel(", ".join(visible_main))

        # Подписываем title на основе файлов
        self.set_graph_title()

        # tight layout эквивалент — можно чуть подвинуть viewbox
        self.plot_item.enableAutoRange()

    def _setup_plot_style(self) -> None:
        """Настраивает стиль графика после очистки."""
        if self.plot_item is None:
            return
            
        # Восстанавливаем настройки белого фона после очистки
        if self.plot_item.getViewBox():
            self.plot_item.getViewBox().setBackgroundColor('w')
        
        axis_pen = pg.mkPen('k')
        text_pen = pg.mkPen('k')
        
        self.plot_item.getAxis('left').setPen(axis_pen)
        self.plot_item.getAxis('bottom').setPen(axis_pen)
        self.plot_item.getAxis('right').setPen(axis_pen)
        self.plot_item.getAxis('left').setTextPen(text_pen)
        self.plot_item.getAxis('bottom').setTextPen(text_pen)
        self.plot_item.getAxis('right').setTextPen(text_pen)
        
        # Восстанавливаем vline и annotation
        self.vline = pg.InfiniteLine(
            angle=90, movable=False, 
            pen=pg.mkPen("k", style=Qt.DashLine)
        )
        self.plot_item.addItem(self.vline)
        self.vline.hide()
        
        self.annotation = pg.TextItem(
            anchor=(0, 1), border=pg.mkPen(0.5), 
            fill=(255, 255, 255, 200), color='k'
        )
        self.plot_item.addItem(self.annotation)
        self.annotation.hide()

    def _get_signal_data(self, signal: str) -> np.ndarray:
        """Возвращает данные сигнала с обработкой ошибок."""
        try:
            return pd.to_numeric(
                self.data[signal].iloc[:: self.step], 
                errors="coerce"
            ).to_numpy()
        except Exception:
            return np.array([])

    def set_graph_title(self) -> None:
        """Установка заголовка графика на основе имени файла."""
        if self.plot_item is None:
            return
            
        filename = self.filenames[0] if self.filenames else ""
        if not filename:
            title = "Не выбран файл с данными"
        elif "ШУР" in filename:
            idx = filename.find("ШУР")
            # защититься от выхода за границы
            if len(filename) > idx + 4:
                title = f"ТГ-{filename[idx+3]}/ШУР-{filename[idx+4]}"
            else:
                title = filename
        elif "ТГ" in filename:
            idx = filename.find("ТГ")
            if len(filename) > idx + 3:
                title = f"ТГ-{filename[idx+2]}/ШУР-{filename[idx+3]}"
            else:
                title = filename
        elif "ШСП" in filename:
            title = f"ШСП-{filename[2:3]}" if len(filename) > 3 else filename
        else:
            title = "Тестовый файл"
        self.plot_item.setTitle(title, color='k')

    def on_mouse_move(self, evt: Any) -> None:
        """Обработчик перемещения мыши по графику."""
        if self.plot_item is None:
            return
            
        pos = evt[0]  # SignalProxy передаёт список, где первый элемент — QPointF
        if not self.plot_item.sceneBoundingRect().contains(pos):
            self.vline.hide()
            self.annotation.hide()
            return
            
        mouse_point = self.plot_item.vb.mapSceneToView(pos)
        x = mouse_point.x()
        if x is None:
            self.vline.hide()
            self.annotation.hide()
            return
            
        # индекс ближайшего значения
        idx = int(round(x))
        if idx < 0 or idx >= len(self.data):
            self.vline.hide()
            self.annotation.hide()
            return

        # показать вертикальную линию на позиции idx
        x_disp = idx
        self.vline.setValue(x_disp)
        self.vline.show()

        # формируем текст аннотации
        x_val = self.data[self.time_signal].iloc[idx]  # Исправлено: time_signal вместо time_signals
        text_lines = [f"Время: {self.format_time(x_val)}"]
        
        for signal in self.selected_signals + self.secondary_signals:
            if signal in self.data.columns and self.line_visibility.get(signal, False):
                try:
                    y_val = float(pd.to_numeric(
                        self.data[signal].iloc[idx], errors="coerce"
                    ))
                    text_lines.append(f"{signal}: {y_val:.2f}")
                except Exception:
                    text_lines.append(f"{signal}: -")
                    
        self.annotation.setText("\n".join(text_lines))
        
        # позиционируем аннотацию: справа вверху графика
        view_rect = self.plot_item.vb.viewRect()
        ann_x = view_rect.left() + 0.02 * view_rect.width()
        ann_y = view_rect.top() - 0.02 * view_rect.height()
        self.annotation.setPos(ann_x, ann_y)
        self.annotation.show()

    def format_time(self, timestamp: Any) -> str:
        """Форматирует время для отображения в аннотации."""
        if isinstance(timestamp, pd.Timestamp):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        if isinstance(timestamp, (int, float)):
            return str(timedelta(seconds=float(timestamp)))
        return str(timestamp)

    def analyze_regulator(self) -> None:
        """Обработчик нажатия кнопки анализа регулятора."""
        if self.enable_analys and hasattr(self, 'analyzer'):
            self.analyzer.save_to_pdf()

    def _save_plot(self) -> None:
        """
        Сохранение графика в PNG для.
        """
        if self.plot_widget is None:
            return
            
        try:
            os.makedirs(REPORT_DIR, exist_ok=True)
            out_path = Path(REPORT_DIR) / PLOT_FILENAME
            pixmap = self.plot_widget.grab()
            pixmap.save(str(out_path))
            self.saved_plot_path = str(out_path)
            print(f"Plot saved to {self.saved_plot_path}")
        except Exception as e:
            print(f"Ошибка при сохранении графика: {e}")


def main() -> None:
    """Основная функция для тестирования."""
    df = pd.DataFrame()
    number_data = 10000
    x = np.linspace(0, 10, number_data)

    # Сигнал с шумом
    first_signal = "Очень длинный сигнал"
    noise_strength = 0.1
    clean_signal = np.piecewise(
        x, [x <= 8, x > 8], [250, lambda t: 250 - 2.5 * (t - 8)]
    )
    noise = np.random.normal(0, noise_strength, len(x))
    noisy_signal = clean_signal + noise
    df[first_signal] = noisy_signal

    # Задание ГСМ
    reference_jump_values = [
        0, 10, 20, 10, 30, 10, 60, 10, 100, 110, 100, 120, 
        100, 150, 100, 200, 210, 200, 220, 200, 250, 200, 
        300, 320, 300, 10, 0
    ]
    jump_times = np.linspace(0, 10, len(reference_jump_values), endpoint=False)
    step_graph = np.zeros_like(x)
    for time, val in zip(jump_times, reference_jump_values):
        step_graph[x >= time] = val
    df[GSM_A_CUR] = step_graph
    df[GSM_B_CUR] = step_graph

    # Положение ГСМ (эмуляция)
    df["Значение развертки. Положение ГСМ"] = step_graph

    # Дополнительные графики
    df["ОЗ-А"] = [5 + random.randint(-1, 1) for _ in x]
    df["ОЗ-Б"] = [random.randint(-1, 1) for _ in x]

    # Время
    start_time = datetime.strptime("2018-03-09 14:29:18,560", "%Y-%m-%d %H:%M:%S,%f")
    timestamps = [
        (start_time + timedelta(seconds=float(i))).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        for i in np.linspace(0, 100, number_data)
    ]
    df[COMMON_TIME] = timestamps

    y1 = [
        first_signal,
        GSM_A_CUR,
        "Значение развертки. Положение ГСМ",
        GSM_B_CUR
    ]
    y2 = ["ОЗ-А", "ОЗ-Б"]
    
    app = QApplication(sys.argv)
    window = WindowGraph(
        data=df,
        selected_signals=y1 + y2,
        time_signal=COMMON_TIME,
        enable_analys=True,
        filenames=[
            "E:/User/Temp/ТГ41-2021-06-25_134810_14099.csv.gz",
            "E:/User/Temp/ТГ41-2021-06-25_134914_14099.csv.gz",
        ],
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()