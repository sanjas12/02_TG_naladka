from __future__ import annotations

import logging
import random
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.text import Annotation, Text
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config.config as cfg  # noqa: E402
from logic.regulator_analyzer import RegulatorAnalyzer  # noqa: E402

logger = logging.getLogger(__name__)


class WindowGraph(QMainWindow):
    """
    Класс для отображения графиков данных с возможностью настройки.

    Args:
        data (pd.DataFrame): DataFrame с данными для построения графиков.
        selected_signals (List[str]): Сигналы, каждый со своей осью Y.
        time_signals (str): Название столбца для оси X.
        step (int, optional): Шаг выборки данных. По умолчанию 10.
        filename (str, optional): Имя файла с данными для заголовка.
        enable_button: Можно ли активировать кнопку "АНАЛИЗА"
    """

    def __init__(
        self,
        data: pd.DataFrame,
        selected_signals: List[str],
        time_signals: str,
        filenames: List[str],
        step: int = 10,
        enable_analys: bool = False,
    ) -> None:
        super().__init__()
        logger.info(
            f"WindowGraph.__init__: данных={len(data)}, signals={selected_signals}, "
            f"step={step}, "
            f"enable_analys={enable_analys}, files={filenames}"
        )

        self.data = data
        self.selected_signals = selected_signals
        self.time_signals = time_signals
        self.step = int(step)
        self.filenames = filenames
        self.enable_analys = enable_analys
        self.save_path_plot: Optional[Path] = None

        self.analyzer: RegulatorAnalyzer

        self.lines_list: List = []
        self.checkboxes: dict[str, QCheckBox] = {}
        self.line_visibility: dict[str, bool] = {}

        self.vline = None
        self.annotation: Optional[plt.Artist] = None
        self.marker_labels: dict[str, Annotation] = {}
        self.marker_index: Optional[int] = None
        self.marker_dragging = False
        self.marker_cids: list[int] = []
        self.date_label: Optional[Text] = None
        self.x_is_datetime = False
        self.datetime_values: Optional[pd.Series] = None
        self.displayed_data_indices = np.array([], dtype=int)
        self.ax1: Optional[plt.Axes] = None
        self.signal_axes: dict[str, plt.Axes] = {}

        # Цвета для графиков
        self.signal_colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
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
        control_panel.setMinimumWidth(280)
        control_panel.setMaximumWidth(360)

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
        """Добавляет чекбоксы выбранных сигналов."""
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
            visible = sender.isChecked()
            self.line_visibility[signal_name] = visible
            logger.info(
                "toggle_signal_visibility: сигнал=%r, видимость=%s",
                signal_name,
                visible,
            )
            self.update_graphs()

    def update_graphs(self) -> None:
        """Обновление графиков при изменении параметров."""
        old_step = self.step
        self.step = int(self.points_combobox.currentText())
        self.points_label.setText(
            f"Кол-во отображаемых данных: {len(self.data) // self.step}"
        )
        logger.info(
            f"update_graphs: шаг {old_step} -> {self.step}, "
            f"отображается {len(self.data) // self.step} точек, "
            f"сигналы={self.selected_signals}"
        )
        self.plot_graphs()
        self.canvas.draw()
        self._save_plot()

    def plot_graphs(self) -> None:
        """Построение графиков данных с учетом видимости сигналов."""
        logger.debug("plot_graphs: начало, строк=%d, шаг=%d", len(self.data), self.step)
        self.figure.clear()
        self.date_label = None
        for cid in self.marker_cids:
            self.canvas.mpl_disconnect(cid)
        self.marker_cids.clear()
        self.set_graph_title()

        if self.data.empty:
            logger.warning("plot_graphs: данные пусты, график не построен")
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
        self.signal_axes = {}

        # При больших данных, который не родные QP
        if len(self.data) > 1_000_000:
            adjusted_step = len(self.data) // 1000
            logger.info(
                "plot_graphs: большой датасет (%d строк), шаг скорректирован %d -> %d",
                len(self.data),
                self.step,
                adjusted_step,
            )
            self.step = adjusted_step

        visible_signals = [
            signal
            for signal in self.selected_signals
            if signal in self.data.columns and self.line_visibility.get(signal, True)
        ]
        plot_x = self._prepare_plot_x()
        self.displayed_data_indices = self._build_display_indices(plot_x)
        displayed_indices = self.displayed_data_indices
        for axis_index, signal in enumerate(visible_signals):
            axis = ax1 if axis_index == 0 else ax1.twinx()
            color = self.signal_colors[
                self.selected_signals.index(signal) % len(self.signal_colors)
            ]
            if axis_index > 0:
                axis.spines["right"].set_visible(False)
                axis.spines["left"].set_visible(True)
                axis.spines["left"].set_position(("outward", axis_index * 65))
                axis.yaxis.set_label_position("left")
                axis.yaxis.tick_left()
                axis.patch.set_visible(False)

            axis.spines["left"].set_color(color)
            axis.tick_params(axis="y", colors=color)
            axis.set_ylabel(signal, color=color)
            axis.yaxis.set_major_locator(ticker.MaxNLocator(cfg.TICK_MARK_COUNT_Y))

            if signal in self.data.columns and self.line_visibility.get(signal, True):
                (line,) = axis.plot(
                    plot_x.iloc[displayed_indices],
                    self.data[signal].iloc[displayed_indices],
                    lw=2,
                    label=signal,
                    color=color,
                )
                self.lines_list.append(line)
                self.signal_axes[signal] = axis

        self._synchronize_similar_y_axes(visible_signals)

        ax1.grid(axis="x", color="#d1d5db", alpha=0.6)
        ax1.grid(axis="y", linestyle="--", linewidth=0.5, alpha=0.6)
        self._configure_x_axis(ax1)
        if self.lines_list:
            ax1.legend(handles=self.lines_list, loc="upper left")

        for tick in ax1.get_xticklabels():
            tick.set_rotation(0)
            tick.set_horizontalalignment("center")

        ax1.callbacks.connect("xlim_changed", self._on_x_limits_changed)

        self._adjust_plot_layout(len(visible_signals))
        self.canvas.draw()

        self.ax1 = ax1

        # Вертикальная линия и аннотация
        assert self.ax1 is not None
        x_min, x_max = self.ax1.get_xlim()
        self.vline = self.ax1.axvline(
            x=(x_min + x_max) / 2,
            color="k",
            lw=1,
            ls="--",
            visible=False,
        )
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
        self._create_marker_labels()
        self.marker_cids = [
            self.canvas.mpl_connect("button_press_event", self.on_marker_press),
            self.canvas.mpl_connect("motion_notify_event", self.on_marker_move),
            self.canvas.mpl_connect("button_release_event", self.on_marker_release),
        ]
        if self.marker_index is not None:
            self._set_marker_from_index(self.marker_index)

        logger.debug(
            f"plot_graphs: завершено, всего линий на графике: {len(self.lines_list)}"
        )

    def _prepare_plot_x(self) -> pd.Series:
        """Распознаёт даты, не меняя порядок точек графика."""
        source = self.data[self.time_signals]
        self.x_is_datetime = False
        self.datetime_values = None
        if pd.api.types.is_datetime64_any_dtype(source):
            self.x_is_datetime = True
            self.datetime_values = pd.to_datetime(source)
            return pd.Series(np.arange(len(source), dtype=float), index=source.index)
        if pd.api.types.is_numeric_dtype(source):
            return source

        normalized = source.astype(str).str.replace(",", ".", regex=False)
        parsed = pd.to_datetime(
            normalized,
            errors="coerce",
            dayfirst=True,
            format="mixed",
        )
        if len(parsed) and parsed.notna().mean() >= 0.95:
            self.x_is_datetime = True
            self.datetime_values = parsed
            return pd.Series(np.arange(len(source), dtype=float), index=source.index)
        return source

    def _build_display_indices(self, plot_x: pd.Series) -> np.ndarray:
        """Сохраняет исходную последовательность отсчётов."""
        return np.arange(len(plot_x), dtype=int)[:: self.step]

    def _configure_x_axis(self, axis: plt.Axes) -> None:
        """Применяет единое оформление оси X."""
        axis.xaxis.set_minor_locator(ticker.NullLocator())
        axis.xaxis.set_major_locator(ticker.LinearLocator(11))
        axis.xaxis.get_offset_text().set_visible(False)
        if not self.x_is_datetime:
            axis.set_xlabel(self.time_signals)
            return

        date_label = axis.annotate(
            "",
            xy=(1.0, 0.0),
            xycoords="axes fraction",
            xytext=(0, -42),
            textcoords="offset points",
            ha="right",
            va="top",
            fontsize=8.5,
            fontweight="bold",
            color="#374151",
            annotation_clip=False,
        )
        self.date_label = date_label
        self._update_datetime_x_axis(axis)

    def _on_x_limits_changed(self, axis: plt.Axes) -> None:
        """Обновляет подписи времени после изменения масштаба."""
        if self.x_is_datetime:
            self._update_datetime_x_axis(axis)

    def _update_datetime_x_axis(self, axis: plt.Axes) -> None:
        """Оформляет время, диапазон и отдельную строку даты как в PLC-анализе."""
        x_min, x_max = axis.get_xlim()
        start_time = self._timestamp_at_plot_position(min(x_min, x_max))
        end_time = self._timestamp_at_plot_position(max(x_min, x_max))
        if start_time is None or end_time is None:
            return
        visible_seconds = abs((end_time - start_time).total_seconds())
        axis.xaxis.set_major_formatter(
            ticker.FuncFormatter(
                lambda value, _position: self._format_datetime_tick_at_position(
                    value, visible_seconds
                )
            )
        )
        axis.set_xlabel(
            f"Дата и время (диапазон: {self._format_time_delta(visible_seconds)})"
        )

        date_label = self.date_label
        if date_label is None:
            return
        start_date = min(start_time, end_time).date()
        end_date = max(start_time, end_time).date()
        if start_date == end_date:
            text = f"Дата: {start_date:%d.%m.%Y}"
        else:
            text = f"Дата: {start_date:%d.%m.%Y} — {end_date:%d.%m.%Y}"
        date_label.set_text(text)

    def _timestamp_at_plot_position(self, value: float) -> Optional[pd.Timestamp]:
        """Интерполирует время для подписи, не затрагивая кривую."""
        datetime_values = self.datetime_values
        if datetime_values is None or datetime_values.empty:
            return None
        valid = datetime_values.notna().to_numpy()
        if not valid.any():
            return None
        positions = np.arange(len(datetime_values), dtype=float)[valid]
        timestamps_ns = datetime_values[valid].astype("int64").to_numpy(dtype=float)
        clamped_value = min(max(value, positions[0]), positions[-1])
        timestamp_ns = np.interp(clamped_value, positions, timestamps_ns)
        return pd.Timestamp(round(timestamp_ns))

    def _format_datetime_tick_at_position(
        self, value: float, visible_seconds: float
    ) -> str:
        """Подбирает точность времени по видимому диапазону."""
        timestamp = self._timestamp_at_plot_position(value)
        if timestamp is None:
            return ""
        if visible_seconds <= 10:
            return timestamp.strftime("%H:%M:%S.%f")[:-3]
        if visible_seconds <= 600:
            return timestamp.strftime("%H:%M:%S")
        if visible_seconds <= 86400:
            return timestamp.strftime("%H:%M")
        return timestamp.strftime("%d.%m %H:%M")

    @staticmethod
    def _format_time_delta(seconds: float) -> str:
        """Форматирует диапазон так же, как анализ архивов PLC."""
        total_milliseconds = round(seconds * 1000)
        hours, remainder = divmod(total_milliseconds, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        whole_seconds, milliseconds = divmod(remainder, 1000)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"
        if minutes:
            return f"{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"
        return f"{whole_seconds}.{milliseconds:03d} с"

    def _adjust_plot_layout(self, visible_signal_count: Optional[int] = None) -> None:
        """Адаптирует отступ и расстояние шкал к числу сигналов."""
        if visible_signal_count is None:
            visible_signal_count = len(self.signal_axes)

        figure_width = max(self.figure.get_figwidth(), 1.0)
        figure_height = max(self.figure.get_figheight(), 1.0)
        extra_axes = max(visible_signal_count - 1, 0)

        # При большом числе сигналов сжимаем шаг между шкалами,
        # но оставляем подписи читаемыми и не отдаём им больше 50% ширины.
        axis_spacing_points = 65.0
        if extra_axes:
            available_points = max((figure_width * 0.5 - 0.85) * 72.0, 0.0)
            axis_spacing_points = min(65.0, max(36.0, available_points / extra_axes))

        axes = list(self.signal_axes.values())
        for axis_index, axis in enumerate(axes[1:], start=1):
            axis.spines["left"].set_position(
                ("outward", axis_index * axis_spacing_points)
            )
        for axis_index, label in enumerate(self.marker_labels.values()):
            label.set_position((-axis_index * axis_spacing_points, 0))

        # Место под подписи и цветные шкалы Y не должно
        # расти вместе с шириной развёрнутого окна.
        left_inches = 0.85 + extra_axes * axis_spacing_points / 72.0
        left = min(max(left_inches / figure_width, 0.06), 0.52)
        right = max(1.0 - 0.2 / figure_width, left + 0.2)
        bottom_inches = 0.9 if self.x_is_datetime else 0.65
        bottom = min(max(bottom_inches / figure_height, 0.055), 0.2)
        top = max(1.0 - 0.35 / figure_height, bottom + 0.2)
        self.figure.subplots_adjust(left=left, right=right, bottom=bottom, top=top)

    def resizeEvent(self, event: Any) -> None:  # noqa: N802
        """Пересчитывает отступы при изменении размера окна."""
        super().resizeEvent(event)
        if self.signal_axes:
            self._adjust_plot_layout()
            self.canvas.draw_idle()

    def _synchronize_similar_y_axes(self, visible_signals: List[str]) -> None:
        """Выравнивает шкалы Y сигналов с близкими диапазонами.

        Общие границы и одинаковая цена деления обеспечивают
        одинаковую высоту для одного и того же значения. Существенно
        разные масштабы остаются независимыми.
        """
        ranges: dict[str, tuple[float, float]] = {}
        for signal in visible_signals:
            values = pd.to_numeric(self.data[signal], errors="coerce").to_numpy(
                dtype=float
            )
            finite_values = values[np.isfinite(values)]
            if finite_values.size:
                ranges[signal] = (
                    float(np.min(finite_values)),
                    float(np.max(finite_values)),
                )

        groups: list[list[str]] = []
        for signal, signal_range in ranges.items():
            matching_groups = [
                group
                for group in groups
                if any(
                    self._y_ranges_are_similar(signal_range, ranges[other])
                    for other in group
                )
            ]
            if not matching_groups:
                groups.append([signal])
                continue

            target_group = matching_groups[0]
            target_group.append(signal)
            for redundant_group in matching_groups[1:]:
                target_group.extend(redundant_group)
                groups.remove(redundant_group)

        for group in groups:
            if len(group) < 2:
                continue
            common_min = min(ranges[signal][0] for signal in group)
            common_max = max(ranges[signal][1] for signal in group)
            common_span = common_max - common_min
            padding = (
                common_span * 0.05
                if common_span > 0
                else max(abs(common_min), 1) * 0.05
            )
            for signal in group:
                axis = self.signal_axes[signal]
                axis.set_ylim(common_min - padding, common_max + padding)
                axis.yaxis.set_major_locator(ticker.MaxNLocator(cfg.TICK_MARK_COUNT_Y))

    @staticmethod
    def _y_ranges_are_similar(
        first: tuple[float, float], second: tuple[float, float]
    ) -> bool:
        """Определяет, можно ли без потери читаемости объединить шкалы."""
        first_span = max(first[1] - first[0], np.finfo(float).eps)
        second_span = max(second[1] - second[0], np.finfo(float).eps)
        if max(first_span, second_span) / min(first_span, second_span) > 4:
            return False

        gap = max(first[0], second[0]) - min(first[1], second[1])
        return gap <= max(first_span, second_span) * 0.25

    def set_graph_title(self) -> None:
        """Установка заголовка графика на основе имени файла."""
        filename = self.filenames[0]

        patterns: List[Any] = [
            # "ШУР41" -> ТГ-4/ШУР-1
            (r"ШУР(\d)(\d)", lambda m: f"ТГ-{m.group(1)}/ШУР-{m.group(2)}"),
            # "ТГ41" -> ТГ-4/ШУР-1
            (r"ТГ(\d)(\d)", lambda m: f"ТГ-{m.group(1)}/ШУР-{m.group(2)}"),
            # "ШСП1" -> ШСП-1
            (r"ШСП(\d+)", lambda m: f"ШСП-{m.group(1)}"),
        ]

        if not filename:
            title = "Не выбран файл с данными"
        else:
            for pattern, formatter in patterns:
                if match := re.search(pattern, filename):
                    title = formatter(match)
                    break
            else:
                title = "Тестовый файл"

        logger.debug(f"set_graph_title: файл={filename!r} -> заголовок={title!r}")
        self.figure.suptitle(title, y=1.02)

    def _create_marker_labels(self) -> None:
        """Создаёт цветную метку значения для каждой оси Y."""
        self.marker_labels = {}
        axes = list(self.signal_axes.items())
        for axis_index, (signal, axis) in enumerate(axes):
            color = self.signal_colors[
                self.selected_signals.index(signal) % len(self.signal_colors)
            ]
            label = axis.annotate(
                "",
                xy=(0, 0),
                xycoords=axis.get_yaxis_transform(),
                xytext=(-axis_index * 65, 0),
                textcoords="offset points",
                ha="center",
                va="center",
                color=color,
                fontsize=8,
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, alpha=0.9),
                annotation_clip=False,
                zorder=10,
            )
            label.set_visible(False)
            self.marker_labels[signal] = label

    def _toolbar_is_busy(self) -> bool:
        """Проверяет, не включено ли масштабирование или панорамирование."""
        return bool(self.toolbar.mode)

    def on_marker_press(self, event: Any) -> None:
        """Ставит маркер и начинает его перетаскивание."""
        if event.button != 1 or self._toolbar_is_busy():
            return
        if event.inaxes not in self.signal_axes.values() or event.xdata is None:
            return
        self.marker_dragging = True
        self._set_marker_from_x(float(event.xdata))

    def on_marker_move(self, event: Any) -> None:
        """Перемещает маркер при удерживании левой кнопки мыши."""
        if not self.marker_dragging or event.xdata is None:
            return
        if event.inaxes not in self.signal_axes.values():
            return
        self._set_marker_from_x(float(event.xdata))

    def on_marker_release(self, event: Any) -> None:
        """Завершает перетаскивание маркера."""
        if event.button == 1:
            self.marker_dragging = False

    def _set_marker_from_x(self, x: float) -> None:
        """Привязывает маркер к ближайшей отображаемой точке."""
        if not self.lines_list:
            return
        try:
            displayed_x = np.asarray(
                self.lines_list[0].get_xdata(orig=False), dtype=float
            )
        except (TypeError, ValueError):
            logger.debug("Не удалось преобразовать ось X", exc_info=True)
            return
        finite = np.isfinite(displayed_x)
        if not finite.any():
            return
        displayed_index = int(
            np.nanargmin(np.where(finite, np.abs(displayed_x - x), np.nan))
        )
        if displayed_index >= len(self.displayed_data_indices):
            return
        data_index = int(self.displayed_data_indices[displayed_index])
        self._set_marker_from_index(data_index, float(displayed_x[displayed_index]))

    def _set_marker_from_index(
        self, index: int, vline_x: Optional[float] = None
    ) -> None:
        """Обновляет линию, время и метки всех осей Y."""
        if self.vline is None or self.annotation is None or self.data.empty:
            return
        index = min(max(index, 0), len(self.data) - 1)
        self.marker_index = index
        x_val = self.data[self.time_signals].iloc[index]
        if vline_x is None:
            line_x = np.asarray(self.lines_list[0].get_xdata(orig=False), dtype=float)
            if not len(line_x) or not len(self.displayed_data_indices):
                return
            displayed_index = int(
                np.argmin(np.abs(self.displayed_data_indices - index))
            )
            vline_x = float(line_x[displayed_index])
        self.vline.set_xdata([vline_x])
        self.vline.set_visible(True)
        self.annotation.set_text(f"Время: {self.format_time(x_val)}")
        self.annotation.set_visible(True)
        for signal, label in self.marker_labels.items():
            value = pd.to_numeric(
                pd.Series([self.data[signal].iloc[index]]), errors="coerce"
            ).iloc[0]
            if pd.isna(value):
                label.set_visible(False)
                continue
            label.xy = (0, float(value))
            label.set_text(f"{float(value):.3f}")
            label.set_visible(True)
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
        if not self.enable_analys:
            self.dialog_box("Недостаточно сигналов для анализа регулятора")
            return

        required_columns = {
            self.time_signals,
            cfg.GSM_A_CUR,
            cfg.GSM_B_CUR,
            cfg.ANALYS_AIM,
        }
        missing_columns = required_columns.difference(self.data.columns)
        if missing_columns:
            self.dialog_box(
                "Не найдены сигналы для анализа:\n" + "\n".join(sorted(missing_columns))
            )
            return

        try:
            logger.debug("Инициализация RegulatorAnalyzer")
            self.analyzer = RegulatorAnalyzer(
                self.data[self.time_signals].to_numpy(),
                self.data[cfg.GSM_A_CUR].to_numpy(),
                self.data[cfg.GSM_B_CUR].to_numpy(),
                self.data[cfg.ANALYS_AIM].to_numpy(),
                self.filenames,
                dt=0.01,
                jump_threshold=cfg.JUMP_THRESHOLD_MM,
                max_jump_threshold=cfg.MAX_JUMP_THRESHOLD_MM,
                plot_file=self.save_path_plot,
            )
            logger.info(f"analyze_regulator: запуск анализа, файлы={self.filenames}")
            self.analyzer.save_to_pdf()
            self.dialog_box(
                f"Анализ регулятора успешно завершён\nОтчет сохранен в {cfg.PDF_FILENAME}"
            )
        except (OSError, TypeError, ValueError, IndexError) as exc:
            logger.exception("analyze_regulator: ошибка при выполнении анализа")
            QMessageBox.critical(self, "Ошибка анализа регулятора", str(exc))

    def _build_plot_filename(self) -> Path:
        """Формирует путь для сохранения графика на основе имён сигналов."""
        base = Path(cfg.PLOT_FILENAME)

        def sanitize(name: str) -> str:
            """Убирает символы, недопустимые в именах файлов."""
            return re.sub(r"[^\w\-]", "_", name).strip("_")

        signals_part = "_".join(sanitize(s) for s in self.selected_signals if s)

        new_stem = f"{signals_part}_" if signals_part else base.stem
        return base.with_name(new_stem + base.suffix)

    def _save_plot(self) -> None:
        """Сохранение графика в PNG для вставки в PDF."""
        self.save_path_plot = self._build_plot_filename()
        marker_artists = [self.vline, self.annotation, *self.marker_labels.values()]
        previous_visibility = [
            artist.get_visible() if artist is not None else False
            for artist in marker_artists
        ]
        try:
            for artist in marker_artists:
                if artist is not None:
                    artist.set_visible(False)
            self.figure.savefig(self.save_path_plot, bbox_inches="tight", dpi=150)
            logger.info(f"_save_plot: график сохранён -> {self.save_path_plot}")
        except Exception:
            logger.exception("_save_plot: ошибка при сохранении графика")
        finally:
            for artist, was_visible in zip(marker_artists, previous_visibility):
                if artist is not None:
                    artist.set_visible(was_visible)

    def dialog_box(self, text: str) -> None:
        QMessageBox.information(self, "TG_info", text, QMessageBox.StandardButton.Ok)


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
    df[cfg.COMBINED_TIME] = timestamps

    y1 = [first_signal, "ГСМ-А.Текущее положение", "Значение развертки. Положение ГСМ"]
    y2 = ["ОЗ-А", "ОЗ-Б"]

    app = QApplication(sys.argv)
    window = WindowGraph(
        data=df,
        selected_signals=y1 + y2,
        time_signals=cfg.COMBINED_TIME,
        enable_analys=False,
        filenames=[
            "E:/User/Temp/ТГ41-2021-06-25_134810_14099.csv.gz",
            "E:/User/Temp/ТГ41-2021-06-25_134914_14099.csv.gz",
        ],
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
