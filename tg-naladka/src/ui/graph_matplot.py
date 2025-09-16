from __future__ import annotations

import sys
import random
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import *
from logic.regulator_analyzer import RegulatorAnalyzer


class WindowGraph(QMainWindow):
    """
    Класс для отображения графиков данных с возможностью настройки.

    Args:
        data (pd.DataFrame): DataFrame с данными для построения графиков.
        base_signals (List[str]): Список сигналов для основной оси Y.
        secondary_signals (List[str]): Список сигналов для вторичной оси Y.
        time_signals (str): Название столбца для оси X.
        step (int, optional): Шаг выборки данных. По умолчанию 10.
        filename (str, optional): Имя файла с данными для заголовка. По умолчанию None.
        enable_button: Можно ли активировать кнопку "АНАЛИЗА"
    """

    

    def __init__(
        self,
        data: pd.DataFrame,
        base_signals: List[str],
        secondary_signals: List[str],
        time_signals: str,
        filenames: List[str],
        step: int = 10,
        enable_analys: bool = False,
    ) -> None:
        super().__init__()


        self.data = data
        self.base_signals = base_signals
        self.secondary_signals = secondary_signals
        self.time_signals = time_signals
        self.step = int(step)
        self.filenames = filenames
        self.enable_analys = enable_analys
        
        if self.enable_analys:
            self.analyzer = RegulatorAnalyzer(self.data[COMMON_TIME].to_numpy(),
                                            self.data[GSM_A_CUR].to_numpy(),
                                            self.data[GSM_B_CUR].to_numpy(),
                                            self.data[ANALYS_AIM].to_numpy(),
                                            self.filenames,
                                            )

        self.lines_list: List = []
        self.checkboxes: dict[str, QCheckBox] = {}
        self.line_visibility: dict[str, bool] = {}

        self.vline = None
        self.annotation = None
        self.cid = None
        self.ax1 = None
        self.ax2 = None

        # Цвета для графиков
        self.base_colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
        ]
        self.secondary_colors = [
            "#17becf",
            "#bcbd22",
            "#7f7f7f",
            "#aec7e8",
            "#ffbb78",
            "#98df8a",
        ]

        self.init_ui()
        self.plot_graphs()
        self._save_plot()

    def init_ui(self) -> None:
        """Инициализация пользовательского интерфейса."""
        self.setWindowTitle("Графики")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Панель настройки
        control_panel = QGroupBox("Панель настройки")
        control_layout = QVBoxLayout()

        # GroupBox "Шаг выборки"
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

        # GroupBox "Видимость сигналов"
        visibility_group = QGroupBox("Видимость сигналов")
        visibility_layout = QVBoxLayout()
        self._add_signal_checkboxes(visibility_layout)
        visibility_layout.addStretch()
        visibility_group.setLayout(visibility_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # чтобы растягивалась по размеру
        scroll_area.setWidget(visibility_group)


        # GroupBox для анализа регулятора
        regulator_group = QGroupBox("Анализ регулятора ГСМ")
        regulator_layout = QVBoxLayout()
        analyze_button = QPushButton("Анализ регулятора")
        analyze_button.setEnabled(self.enable_analys)
        analyze_button.clicked.connect(self.analyze_regulator)
        regulator_layout.addWidget(analyze_button)
        regulator_group.setLayout(regulator_layout)

        control_layout.addWidget(sampling_group, stretch=1)
        control_layout.addWidget(scroll_area, stretch=6)
        control_layout.addWidget(regulator_group, stretch=1)

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

    def _add_signal_checkboxes(self, layout: QVBoxLayout) -> None:
        """Добавляет чекбоксы для сигналов основной и вторичной осей."""
        if self.base_signals:
            layout.addWidget(QLabel("Основная ось:"))
            for signal in self.base_signals:
                cb = QCheckBox(signal)
                cb.setChecked(True)
                cb.stateChanged.connect(self.toggle_signal_visibility)
                layout.addWidget(cb)
                self.checkboxes[signal] = cb
                self.line_visibility[signal] = True

        if self.secondary_signals:
            layout.addWidget(QLabel("\nВспомогательная ось:"))
            for signal in self.secondary_signals:
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
            f"Кол-во отображаемых данных: {len(self.data) // self.step}"
        )
        self.plot_graphs()
        self.canvas.draw()
        self._save_plot()

    def plot_graphs(self) -> None:
        """Построение графиков данных с учетом видимости сигналов."""
        self.figure.clear()
        self.set_graph_title()

        if self.data.empty:
            self.figure.text(
                0.5,
                0.5,
                "Нет данных для отображения",
                ha="center",
                va="center",
            )
            self.canvas.draw()
            return

        ax1 = self.figure.add_subplot()
        self.lines_list = []
        ax2 = None

        # Основные сигналы
        for signal in self.base_signals:
            if signal in self.data.columns and self.line_visibility.get(signal, True):
                (line,) = ax1.plot(
                    self.data[self.time_signals][:: self.step],
                    self.data[signal][:: self.step],
                    lw=2,
                    label=signal,
                )
                self.lines_list.append(line)

        ax1.grid(linestyle="--", linewidth=0.5, alpha=0.85)
        ax1.set_ylabel(
            ",\n".join(
                [s for s in self.base_signals if self.line_visibility.get(s, True)]
            )
        )
        ax1.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_X))
        ax1.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_Y))
        if any(self.line_visibility.get(s, False) for s in self.base_signals):
            ax1.legend(loc="upper left")
        ax1.set_xlabel(self.time_signals, loc="right")

        # Вторичные сигналы
        if self.secondary_signals:
            ax2 = ax1.twinx()
            for i, signal in enumerate(self.secondary_signals):
                if signal in self.data.columns and self.line_visibility.get(
                    signal, True
                ):
                    (line,) = ax2.plot(
                        self.data[self.time_signals][:: self.step],
                        self.data[signal][:: self.step],
                        ls="-.",
                        lw=2,
                        label=signal,
                        color=self.secondary_colors[i % len(self.secondary_colors)],
                    )
                    self.lines_list.append(line)

            visible_secondary = [
                s for s in self.secondary_signals if self.line_visibility.get(s, True)
            ]
            if visible_secondary:
                ax2.tick_params(axis="y", labelcolor="b")
                ax2.xaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_X))
                ax2.yaxis.set_major_locator(ticker.MaxNLocator(TICK_MARK_COUNT_Y))
                ax2.set_ylabel(f",\n".join(visible_secondary), color="b")
                ax2.legend(loc="upper right")

        for tick in ax1.get_xticklabels():
            tick.set_rotation(15)

        self.figure.tight_layout()
        self.canvas.draw()

        self.ax1 = ax1
        self.ax2 = ax2

        # Вертикальная линия и аннотация
        self.vline = self.ax1.axvline(x=0, color="k", lw=1, ls="--", visible=False)
        self.annotation = self.figure.text(
            0.75,
            0.05,
            "",
            transform=self.figure.transFigure,
            bbox=dict(boxstyle="round", fc="w", alpha=0.9, ec="0.5"),
            fontsize=8,
            fontfamily="monospace",
        )
        self.annotation.set_visible(False)

        if self.cid is not None:
            self.canvas.mpl_disconnect(self.cid)
        # self.cid = self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)

    def set_graph_title(self) -> None:
        """Установка заголовка графика на основе имени файла."""
        filename = self.filenames[0]
        if not filename:
            title = "Не выбран файл с данными"
        elif "ШУР" in filename: 
            idx = filename.find("ШУР") 
            title = f"ТГ-{filename[idx+3]}/ШУР-{filename[idx+4]}"
        elif "ТГ" in filename:
            idx = filename.find("ТГ") 
            title = f"ТГ-{filename[idx+2]}/ШУР-{filename[idx+3]}"
        elif "ШСП" in filename:
            title = f"ШСП-{filename[2:3]}"
        else:
            title = "Тестовый файл"

        self.figure.suptitle(title, y=1.02)

    def on_mouse_move(self, event) -> None:
        """Обработчик перемещения мыши по графику."""
        if self.vline is None or self.annotation is None:
            return

        axes = [self.ax1]
        if self.ax2 is not None:
            axes.append(self.ax2)

        if event.inaxes not in axes:
            self.vline.set_visible(False)
            self.annotation.set_visible(False)
            self.canvas.draw_idle()
            return

        x = event.xdata
        if x is None:
            self.vline.set_visible(False)
            self.annotation.set_visible(False)
            self.canvas.draw_idle()
            return

        x_series = self.data[self.time_signals]
        if len(x_series) == 0:
            return

        idx: Optional[int] = None
        vline_x = x
        try:
            x_numeric = pd.to_numeric(x_series, errors="coerce").to_numpy()
            if not np.isnan(x_numeric).all():
                idx = int(np.nanargmin(np.abs(x_numeric - x)))
                vline_x = x_numeric[idx]
        except Exception:
            idx = None

        if idx is None:
            idx = int(min(max(round(x), 0), len(x_series) - 1))

        if not (0 <= idx < len(x_series)):
            return

        x_val = x_series.iloc[idx]

        self.vline.set_xdata([vline_x])
        self.vline.set_visible(True)

        text_lines = [f"Время: {self.format_time(x_val)}"]
        for signal in self.base_signals + self.secondary_signals:
            if signal in self.data.columns and self.line_visibility.get(signal, False):
                y_val = self.data[signal].iloc[idx]
                text_lines.append(f"{signal}: {y_val:.2f}")

        if text_lines:
            self.annotation.set_text("\n".join(text_lines))
            self.annotation.set_visible(True)
        else:
            self.annotation.set_visible(False)

        self.canvas.draw_idle()

    def format_time(self, timestamp) -> str:
        """Форматирует время для отображения в аннотации."""
        if isinstance(timestamp, pd.Timestamp):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        if isinstance(timestamp, (int, float)):
            return str(timedelta(seconds=float(timestamp)))
        return str(timestamp)

    def analyze_regulator(self) -> None:
        """Обработчик нажатия кнопки анализа регулятора."""
        print("Запуск анализа регулятора...")
        # print(self.analyzer.get_analysis_report())
        self.analyzer.save_to_pdf()

    def _save_plot(self) -> None:
        """Сохранение графика в PNG для вставки в PDF.

        Сохраняет изображение в папку <PROJECT_ROOT>/reports по умолчанию.
        Обновляет атрибут self.saved_plot_path с полным путём к сохранённому файлу.
        """
        try:
            os.makedirs(REPORT_DIR, exist_ok=True)
            # Сохраняем текущую фигуру
            self.figure.savefig(PLOT_FILENAME, bbox_inches="tight", dpi=150)
            print(f"Plot saved to {PLOT_FILENAME}")
        except Exception as e:
            # Простая обработка ошибок — вывести в консоль. GUI-логирование можно добавить позже.
            print(f"Ошибка при сохранении графика: {e}")

def main() -> None:
    df = pd.DataFrame()
    number_data = 10000
    x = np.linspace(0, 10, number_data)

    # Сигнал с шумом
    first_signal = "Очень                                          длинный сигнал"
    noise_strength = 0.1
    clean_signal = np.piecewise(
        x, [x <= 8, x > 8], [250, lambda t: 250 - 2.5 * (t - 8)]
    )
    noise = np.random.normal(0, noise_strength, len(x))
    noisy_signal = clean_signal + noise
    df[first_signal] = noisy_signal

    # Задание ГСМ
    reference_jump_values = [
        0,
        10,
        20,
        10,
        30,
        10,
        60,
        10,
        100,
        110,
        100,
        120,
        100,
        150,
        100,
        200,
        210,
        200,
        220,
        200,
        250,
        200,
        300,
        320,
        300,
        10,
        0,
    ]
    jump_times = np.linspace(0, 10, len(reference_jump_values), endpoint=False)
    step_graph = np.zeros_like(x)
    for time, val in zip(jump_times, reference_jump_values):
        step_graph[x >= time] = val
    df["ГСМ-А.Текущее положение"] = step_graph

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

    y1 = [first_signal, "ГСМ-А.Текущее положение", "Значение развертки. Положение ГСМ"]
    y2 = ["ОЗ-А", "ОЗ-Б"]

    app = QApplication(sys.argv)
    window = WindowGraph(
        data=df,
        base_signals=y1,
        secondary_signals=y2,
        time_signals=COMMON_TIME,
        enable_analys=False,
        filenames=["E:/User/Temp/ТГ41-2021-06-25_134810_14099.csv.gz",
                   "E:/User/Temp/ТГ41-2021-06-25_134914_14099.csv.gz"]
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
