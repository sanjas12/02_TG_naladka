from __future__ import annotations

import logging
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseButton, MouseEvent
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.text import Annotation, Text
from PyQt5.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from logic.plc_archive_analyzer import (
    BinarySignalPoint,
    CategoricalSignalPoint,
    ComparisonResult,
    NumericSignalPoint,
    PlkEvent,
    compare_events,
    extract_binary_signal,
    extract_categorical_signal,
    extract_numeric_signal,
    load_plk_archive,
)

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ERROR_CODE_SIGNAL = "Код ошибки по приоритету (младшая часть)"
LEADING_CHANNEL_SIGNAL = "Канал ведущий"
WORK_MODE_SIGNAL = "Режим работы"
ERROR_CODE_MAX = 66000
MIN_TIME_WINDOW_SECONDS = 1.0


class PlkArchiveWindow(QMainWindow):
    """Сравнение синхронизированных архивов двух каналов PLC."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.channel_1: List[PlkEvent] = []
        self.channel_2: List[PlkEvent] = []
        self._plotted_events: List[Tuple[PlkEvent, int]] = []
        self._numeric_badges: List[
            Tuple[Axes, Sequence[NumericSignalPoint], Annotation]
        ] = []
        self._annotation: Optional[Annotation] = None
        self._time_axis: Optional[Axes] = None
        self._date_label: Optional[Text] = None
        self._adjusting_time_limits = False
        self._adjusting_y_limits = False
        self._measurement_points: List[float] = []
        self._measurement_artists: List[Artist] = []
        self._measurement_axes: List[Axes] = []
        self._dragging_measurement_index: Optional[int] = None

        self.setWindowTitle("Анализ архивов PLC")
        self.resize(1280, 760)
        self._setup_ui()
        self._load_default_archives()

    def _setup_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        files_group = QGroupBox("Исходные архивы")
        files_layout = QGridLayout(files_group)
        self.channel_1_path = QLineEdit()
        self.channel_2_path = QLineEdit()
        self.channel_1_path.setReadOnly(True)
        self.channel_2_path.setReadOnly(True)
        button_1 = QPushButton("Выбрать…")
        button_2 = QPushButton("Выбрать…")
        button_1.clicked.connect(lambda: self._select_file(1))
        button_2.clicked.connect(lambda: self._select_file(2))
        files_layout.addWidget(QLabel("Канал 1:"), 0, 0)
        files_layout.addWidget(self.channel_1_path, 0, 1)
        files_layout.addWidget(button_1, 0, 2)
        files_layout.addWidget(QLabel("Канал 2:"), 1, 0)
        files_layout.addWidget(self.channel_2_path, 1, 1)
        files_layout.addWidget(button_2, 1, 2)
        layout.addWidget(files_group)

        controls = QHBoxLayout()
        controls.addWidget(QLabel("Допуск синхронизации, мс:"))
        self.tolerance = QSpinBox()
        self.tolerance.setRange(0, 60000)
        self.tolerance.setValue(100)
        self.tolerance.setSingleStep(10)
        self.tolerance.valueChanged.connect(self._refresh_plot)
        controls.addWidget(self.tolerance)
        controls.addSpacing(20)
        self.measurement_button = QPushButton("Измерить Δt")
        self.measurement_button.setCheckable(True)
        self.measurement_button.toggled.connect(self._toggle_time_measurement)
        controls.addWidget(self.measurement_button)
        self.clear_measurement_button = QPushButton("Очистить")
        self.clear_measurement_button.setEnabled(False)
        self.clear_measurement_button.clicked.connect(
            lambda: self._clear_time_measurement()
        )
        controls.addWidget(self.clear_measurement_button)
        self.measurement_status = QLabel("")
        controls.addWidget(self.measurement_status)
        controls.addSpacing(20)
        self.summary = QLabel("Выберите два архива")
        controls.addWidget(self.summary)
        controls.addStretch()
        layout.addLayout(controls)

        self.figure = Figure(figsize=(12, 6), constrained_layout=True)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, 1)
        self.canvas.mpl_connect("motion_notify_event", self._on_hover)
        self.canvas.mpl_connect("motion_notify_event", self._on_measurement_drag)
        self.canvas.mpl_connect("button_release_event", self._on_view_changed)
        self.canvas.mpl_connect("scroll_event", self._on_view_changed)
        self.canvas.mpl_connect("button_press_event", self._on_measurement_click)

    def _load_default_archives(self) -> None:
        log_root = PROJECT_ROOT / "input" / "Logs"
        files = sorted(log_root.rglob("*.csv")) if log_root.is_dir() else []
        if len(files) >= 2:
            self._load_channel(1, files[0], refresh=False)
            self._load_channel(2, files[1], refresh=True)

    def _select_file(self, channel: int) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            f"Выбор архива канала {channel}",
            str(PROJECT_ROOT / "input" / "Logs"),
            "Архивы (*.csv *.txt);;Все файлы (*.*)",
        )
        if filename:
            self._load_channel(channel, Path(filename))

    def _load_channel(self, channel: int, path: Path, refresh: bool = True) -> None:
        try:
            events = load_plk_archive(path)
            if not events:
                raise ValueError(f"В файле {path.name} нет событий")
            if channel == 1:
                self.channel_1 = events
                self.channel_1_path.setText(str(path))
            else:
                self.channel_2 = events
                self.channel_2_path.setText(str(path))
            if refresh:
                self._refresh_plot()
        except (OSError, ValueError) as error:
            logger.error("Ошибка чтения архива PLC", exc_info=True)
            QMessageBox.critical(self, "Ошибка архива PLC", str(error))

    def _refresh_plot(self) -> None:
        if not self.channel_1 or not self.channel_2:
            return
        try:
            signal_1, events_1 = extract_numeric_signal(
                self.channel_1, ERROR_CODE_SIGNAL
            )
            signal_2, events_2 = extract_numeric_signal(
                self.channel_2, ERROR_CODE_SIGNAL
            )
            leading_1, events_1 = extract_binary_signal(
                events_1, LEADING_CHANNEL_SIGNAL
            )
            leading_2, events_2 = extract_binary_signal(
                events_2, LEADING_CHANNEL_SIGNAL
            )
            work_modes_1, events_1 = extract_categorical_signal(
                events_1, WORK_MODE_SIGNAL
            )
            work_modes_2, events_2 = extract_categorical_signal(
                events_2, WORK_MODE_SIGNAL
            )
            result = compare_events(
                events_1, events_2, tolerance_ms=self.tolerance.value()
            )
            self._draw_timeline(
                result,
                signal_1,
                signal_2,
                leading_1,
                leading_2,
                work_modes_1,
                work_modes_2,
            )
        except ValueError as error:
            logger.error("Ошибка числового сигнала архива PLC", exc_info=True)
            QMessageBox.critical(self, "Ошибка архива PLC", str(error))

    def _draw_timeline(
        self,
        result: ComparisonResult,
        signal_1: List[NumericSignalPoint],
        signal_2: List[NumericSignalPoint],
        leading_1: List[BinarySignalPoint],
        leading_2: List[BinarySignalPoint],
        work_modes_1: List[CategoricalSignalPoint],
        work_modes_2: List[CategoricalSignalPoint],
    ) -> None:
        self._clear_time_measurement(redraw=False)
        self.figure.clear()
        signal_axis_1, axis, signal_axis_2 = self.figure.subplots(
            3,
            1,
            sharex=True,
            gridspec_kw={"height_ratios": [1, 1.5, 1]},
        )
        self._measurement_axes = [signal_axis_1, axis, signal_axis_2]
        timeline_end = max(
            self.channel_1[-1].timestamp,
            self.channel_2[-1].timestamp,
        )
        badge_1 = self._draw_numeric_signal(
            signal_axis_1,
            signal_1,
            "Канал 1",
            "#2563eb",
            label_offset=6,
            timeline_end=timeline_end,
        )
        badge_2 = self._draw_numeric_signal(
            signal_axis_2,
            signal_2,
            "Канал 2",
            "#9333ea",
            label_offset=-12,
            timeline_end=timeline_end,
        )
        self._numeric_badges = []
        if badge_1 is not None:
            self._numeric_badges.append((signal_axis_1, signal_1, badge_1))
        if badge_2 is not None:
            self._numeric_badges.append((signal_axis_2, signal_2, badge_2))
        signal_axis_2.invert_yaxis()
        mode_categories = self._work_mode_categories(work_modes_1, work_modes_2)
        mode_axis_1 = signal_axis_1.twinx()
        mode_axis_2 = signal_axis_2.twinx()
        self._draw_work_mode_signal(
            mode_axis_1,
            work_modes_1,
            mode_categories,
            timeline_end,
            "Канал 1",
            "#047857",
        )
        self._draw_work_mode_signal(
            mode_axis_2,
            work_modes_2,
            mode_categories,
            timeline_end,
            "Канал 2",
            "#c2410c",
        )
        signal_axis_1.set_zorder(mode_axis_1.get_zorder() + 1)
        signal_axis_1.patch.set_visible(False)
        signal_axis_2.set_zorder(mode_axis_2.get_zorder() + 1)
        signal_axis_2.patch.set_visible(False)
        leading_axis = axis.twinx()
        self._draw_leading_channel_signal(
            leading_axis, leading_1, leading_2, timeline_end
        )
        axis.set_zorder(leading_axis.get_zorder() + 1)
        axis.patch.set_visible(False)
        axis.axhline(0, color="#374151", linewidth=1.2)

        for pair in result.pairs:
            axis.plot(
                [pair.channel_1.timestamp, pair.channel_2.timestamp],
                [1, -1],
                color="#94a3b8",
                alpha=0.35,
                linewidth=0.7,
                zorder=1,
            )

        matched_1 = [pair.channel_1.timestamp for pair in result.pairs]
        matched_2 = [pair.channel_2.timestamp for pair in result.pairs]
        axis.scatter(
            matched_1,
            [1] * len(matched_1),
            s=15,
            color="#0f766e",
            label="Совпали",
            zorder=3,
        )
        axis.scatter(matched_2, [-1] * len(matched_2), s=15, color="#0f766e", zorder=3)
        axis.scatter(
            [event.timestamp for event in result.only_channel_1],
            [1] * len(result.only_channel_1),
            s=22,
            color="#dc2626",
            marker="x",
            label="Только в канале 1",
            zorder=4,
        )
        axis.scatter(
            [event.timestamp for event in result.only_channel_2],
            [-1] * len(result.only_channel_2),
            s=22,
            color="#d97706",
            marker="x",
            label="Только в канале 2",
            zorder=4,
        )

        self._plotted_events = (
            [(pair.channel_1, 1) for pair in result.pairs]
            + [(pair.channel_2, -1) for pair in result.pairs]
            + [(event, 1) for event in result.only_channel_1]
            + [(event, -1) for event in result.only_channel_2]
        )
        axis.set_yticks([-1, 0, 1])
        axis.set_yticklabels(["Канал 2", "Время", "Канал 1"])
        axis.set_ylim(-1.6, 1.6)
        self._lock_y_axis(signal_axis_1, (0, ERROR_CODE_MAX))
        self._lock_y_axis(mode_axis_1, mode_axis_1.get_ylim())
        self._lock_y_axis(axis, (-1.6, 1.6))
        self._lock_y_axis(leading_axis, (-1.2, 1.2))
        self._lock_y_axis(signal_axis_2, (ERROR_CODE_MAX, 0))
        self._lock_y_axis(mode_axis_2, mode_axis_2.get_ylim())
        axis.grid(axis="x", color="#d1d5db", alpha=0.6)
        axis.tick_params(axis="x", labelbottom=True)
        axis.set_xlabel("Дата и время")
        signal_axis_2.tick_params(axis="x", labelbottom=False)
        signal_axis_2.set_xlabel("")
        for date_axis in (
            signal_axis_1,
            mode_axis_1,
            axis,
            leading_axis,
            signal_axis_2,
            mode_axis_2,
        ):
            date_axis.xaxis.get_offset_text().set_visible(False)
        date_label = axis.text(
            1.0,
            -0.13,
            "",
            transform=axis.transAxes,
            ha="right",
            va="top",
            fontsize=8.5,
            fontweight="bold",
            color="#374151",
            clip_on=False,
        )
        self._date_label = date_label
        self._time_axis = signal_axis_2
        for shared_axis in (signal_axis_1, axis, signal_axis_2):
            shared_axis.callbacks.connect(
                "xlim_changed",
                lambda changed_axis, target_axis=signal_axis_2: (
                    self._on_time_limits_changed(target_axis, changed_axis.get_xlim())
                ),
            )
        self._update_time_axis(signal_axis_2)
        self._update_numeric_badges(signal_axis_2.get_xlim())
        self._update_date_label(signal_axis_2.get_xlim())
        event_handles, event_labels = axis.get_legend_handles_labels()
        leading_handles, leading_labels = leading_axis.get_legend_handles_labels()
        axis.legend(
            event_handles + leading_handles,
            event_labels + leading_labels,
            loc="upper right",
        )

        deltas = [abs(pair.delta_ms) for pair in result.pairs]
        max_delta = max(deltas) if deltas else 0
        self.summary.setText(
            f"Канал 1: {len(self.channel_1)} | Канал 2: {len(self.channel_2)} | "
            f"пар: {len(result.pairs)} | расхождений: "
            f"{len(result.only_channel_1) + len(result.only_channel_2)} | "
            f"точек кода: {len(signal_1)}/{len(signal_2)} | "
            f"ведущий: {len(leading_1)}/{len(leading_2)} | "
            f"режим: {len(work_modes_1)}/{len(work_modes_2)} | "
            f"макс. сдвиг: {max_delta:.0f} мс"
        )
        annotation = axis.annotate(
            "",
            xy=(0, 0),
            xytext=(12, 16),
            textcoords="offset points",
            bbox={"boxstyle": "round", "fc": "white", "alpha": 0.95},
            arrowprops={"arrowstyle": "->"},
        )
        annotation.set_visible(False)
        self._annotation = annotation
        self.canvas.draw_idle()

    def _update_time_axis(
        self, axis: Axes, limits: Optional[Tuple[float, float]] = None
    ) -> None:
        """Ограничивает приближение одной секундой и подбирает деления времени."""
        if self._adjusting_time_limits:
            return

        x_min, x_max = limits if limits is not None else axis.get_xlim()
        visible_seconds = abs(x_max - x_min) * 24 * 60 * 60
        if visible_seconds < MIN_TIME_WINDOW_SECONDS:
            center = (x_min + x_max) / 2
            half_window = MIN_TIME_WINDOW_SECONDS / (2 * 24 * 60 * 60)
            x_min = center - half_window
            x_max = center + half_window
            visible_seconds = MIN_TIME_WINDOW_SECONDS
            self._adjusting_time_limits = True
            try:
                axis.set_xlim(x_min, x_max)
            finally:
                self._adjusting_time_limits = False

        axis.xaxis.set_minor_locator(ticker.NullLocator())

        if visible_seconds <= MIN_TIME_WINDOW_SECONDS * 1.001:
            axis.xaxis.set_major_locator(mdates.MicrosecondLocator(interval=100000))
            axis.xaxis.set_major_formatter(
                ticker.FuncFormatter(
                    lambda value, _position: mdates.num2date(value).strftime(
                        "%H:%M:%S.%f"
                    )[:-3]
                )
            )
        elif visible_seconds <= 60:
            subminute_intervals = (0.5, 1, 2, 5, 10)
            interval = next(
                value for value in subminute_intervals if visible_seconds / value <= 12
            )
            if interval == 0.5:
                axis.xaxis.set_major_locator(mdates.MicrosecondLocator(interval=500000))
            else:
                axis.xaxis.set_major_locator(
                    mdates.SecondLocator(interval=int(interval))
                )
                axis.xaxis.set_minor_locator(mdates.MicrosecondLocator(interval=500000))
            axis.xaxis.set_major_formatter(
                ticker.FuncFormatter(
                    lambda value, _position: mdates.num2date(value).strftime(
                        "%H:%M:%S.%f"
                    )[:-3]
                )
            )
        elif visible_seconds <= 300:
            second_intervals = (1, 2, 5, 10, 15, 30)
            interval = next(
                value for value in second_intervals if visible_seconds / value <= 12
            )
            axis.xaxis.set_major_locator(mdates.SecondLocator(interval=interval))
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        elif visible_seconds <= 7200:
            minute_intervals = (1, 2, 5, 10, 15, 30)
            visible_minutes = visible_seconds / 60
            interval = next(
                value for value in minute_intervals if visible_minutes / value <= 12
            )
            axis.xaxis.set_major_locator(mdates.MinuteLocator(interval=interval))
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            locator = mdates.AutoDateLocator(minticks=5, maxticks=12)
            axis.xaxis.set_major_locator(locator)
            axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))

    def _on_view_changed(self, _mouse_event: MouseEvent) -> None:
        """Обновляет формат времени после завершения масштабирования и прокрутки."""
        was_dragging_measurement = self._dragging_measurement_index is not None
        self._dragging_measurement_index = None
        if was_dragging_measurement:
            self._render_time_measurement()
        time_axis = self._time_axis
        if time_axis is None:
            return
        self._update_time_axis(time_axis)
        self._update_numeric_badges(time_axis.get_xlim())
        self._update_date_label(time_axis.get_xlim())
        self.canvas.draw_idle()

    def _toggle_time_measurement(self, enabled: bool) -> None:
        """Включает выбор двух временных точек или очищает измерение."""
        self._clear_time_measurement(redraw=True)
        if enabled:
            self.measurement_status.setText("Выберите начало")

    def _clear_time_measurement(self, redraw: bool = True) -> None:
        """Удаляет линии, заливку и информационный блок измерения."""
        self._remove_measurement_artists()
        self._measurement_points.clear()
        self._dragging_measurement_index = None
        self.clear_measurement_button.setEnabled(False)
        self.measurement_status.setText(
            "Выберите начало" if self.measurement_button.isChecked() else ""
        )
        if redraw:
            self.canvas.draw_idle()

    def _remove_measurement_artists(self) -> None:
        """Удаляет только графические элементы, сохраняя выбранные точки."""
        for artist in self._measurement_artists:
            with suppress(ValueError):
                artist.remove()
        self._measurement_artists.clear()

    def _on_measurement_click(self, mouse_event: MouseEvent) -> None:
        """Устанавливает начальный и конечный маркеры измерения времени."""
        if (
            not self.measurement_button.isChecked()
            or mouse_event.button != MouseButton.LEFT
            or mouse_event.inaxes is None
            or mouse_event.xdata is None
            or bool(self.toolbar.mode)
        ):
            return

        marker_index = self._measurement_marker_at(mouse_event)
        if marker_index is not None:
            self._dragging_measurement_index = marker_index
            self.measurement_status.setText("Перемещение маркера…")
            return

        if len(self._measurement_points) == 2:
            self._clear_time_measurement(redraw=False)

        self._measurement_points.append(mouse_event.xdata)
        self._render_time_measurement()
        self.canvas.draw_idle()

    def _measurement_marker_at(self, mouse_event: MouseEvent) -> Optional[int]:
        """Находит маркер рядом с курсором с допуском десять пикселей."""
        axis = mouse_event.inaxes
        if axis is None or mouse_event.x is None:
            return None
        distances = [
            abs(axis.transData.transform((timestamp, 0))[0] - mouse_event.x)
            for timestamp in self._measurement_points
        ]
        if not distances:
            return None
        nearest_index = min(range(len(distances)), key=distances.__getitem__)
        return nearest_index if distances[nearest_index] <= 10 else None

    def _on_measurement_drag(self, mouse_event: MouseEvent) -> None:
        """Перемещает выбранный маркер и пересчитывает дельту в реальном времени."""
        marker_index = self._dragging_measurement_index
        if (
            marker_index is None
            or mouse_event.inaxes is None
            or mouse_event.xdata is None
        ):
            return
        self._measurement_points[marker_index] = mouse_event.xdata
        self._render_time_measurement()
        self.canvas.draw_idle()

    def _render_time_measurement(self) -> None:
        """Перерисовывает маркеры, захваты и выбранный временной интервал."""
        self._remove_measurement_artists()
        middle_axis = self._measurement_axes[1]
        colors = ("#e11d48", "#7c3aed")
        labels = ("A", "B")

        for index, timestamp in enumerate(self._measurement_points):
            marker_color = colors[index]
            for axis in self._measurement_axes:
                line = axis.axvline(
                    timestamp,
                    color=marker_color,
                    linewidth=1.5,
                    linestyle="--",
                    zorder=8,
                )
                self._measurement_artists.append(line)
            (handle,) = middle_axis.plot(
                [timestamp],
                [0],
                marker="o",
                markersize=7,
                color=marker_color,
                markeredgecolor="white",
                zorder=9,
            )
            self._measurement_artists.append(handle)
            marker_label = middle_axis.annotate(
                labels[index],
                xy=(timestamp, 0),
                xytext=(0, 8),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=marker_color,
                fontweight="bold",
                fontsize=8,
                zorder=9,
            )
            self._measurement_artists.append(marker_label)

        if len(self._measurement_points) == 1:
            self.measurement_status.setText("Выберите конец")
        elif len(self._measurement_points) == 2:
            self._complete_time_measurement()
        self.clear_measurement_button.setEnabled(bool(self._measurement_points))

    def _complete_time_measurement(self) -> None:
        """Подсвечивает выбранный интервал и выводит рассчитанную дельту."""
        start, end = self._measurement_points
        interval_start, interval_end = sorted((start, end))
        for axis in self._measurement_axes:
            span = axis.axvspan(
                interval_start,
                interval_end,
                color="#f59e0b",
                alpha=0.12,
                zorder=0.5,
            )
            self._measurement_artists.append(span)

        start_time = mdates.num2date(start).replace(tzinfo=None)
        end_time = mdates.num2date(end).replace(tzinfo=None)
        delta_seconds = abs(end - start) * 24 * 60 * 60
        text = (
            f"Начало: {self._format_measurement_time(start_time)}\n"
            f"Конец: {self._format_measurement_time(end_time)}\n"
            f"Δt: {self._format_time_delta(delta_seconds)}"
        )

        middle_axis = self._measurement_axes[1]
        annotation = middle_axis.annotate(
            text,
            xy=(end, 0),
            xytext=(16, -28),
            textcoords="offset points",
            ha="left",
            va="top",
            fontsize=8.5,
            bbox={
                "boxstyle": "round,pad=0.35",
                "fc": "white",
                "ec": "#7c3aed",
                "alpha": 0.97,
            },
            arrowprops={"arrowstyle": "->", "color": "#7c3aed"},
            annotation_clip=False,
            zorder=10,
        )
        self._measurement_artists.append(annotation)
        self.measurement_status.setText(
            f"Δt: {self._format_time_delta(delta_seconds)} — перетащите A или B"
        )

    @staticmethod
    def _format_measurement_time(value: datetime) -> str:
        return f"{value:%Y-%m-%d %H:%M:%S.%f}"[:-3]

    @staticmethod
    def _format_time_delta(seconds: float) -> str:
        """Форматирует длительность с точностью до миллисекунд."""
        total_milliseconds = round(seconds * 1000)
        hours, remainder = divmod(total_milliseconds, 3_600_000)
        minutes, remainder = divmod(remainder, 60_000)
        whole_seconds, milliseconds = divmod(remainder, 1000)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"
        if minutes:
            return f"{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"
        return f"{whole_seconds}.{milliseconds:03d} с"

    def _on_time_limits_changed(
        self, time_axis: Axes, limits: Tuple[float, float]
    ) -> None:
        """Обновляет формат времени и индикаторы кодов при изменении X."""
        self._update_time_axis(time_axis, limits)
        self._update_numeric_badges(time_axis.get_xlim())
        self._update_date_label(time_axis.get_xlim())

    def _update_date_label(self, limits: Tuple[float, float]) -> None:
        """Сохраняет дату под средней осью при любом масштабе времени."""
        date_label = self._date_label
        if date_label is None:
            return

        x_min, x_max = sorted(limits)
        start_date = mdates.num2date(x_min).date()
        end_date = mdates.num2date(x_max).date()
        if start_date == end_date:
            label = f"Дата: {start_date:%d.%m.%Y}"
        else:
            label = f"Дата: {start_date:%d.%m.%Y} — {end_date:%d.%m.%Y}"
        date_label.set_text(label)

    def _update_numeric_badges(self, limits: Tuple[float, float]) -> None:
        """Показывает значение кода ошибки на правой границе видимого участка."""
        _, x_max = limits
        for _axis, points, badge in self._numeric_badges:
            visible_points = [
                point for point in points if mdates.date2num(point.timestamp) <= x_max
            ]
            if not visible_points:
                badge.set_visible(False)
                continue

            current_point = visible_points[-1]
            badge.xy = (0.985, current_point.value)
            badge.set_text(f"Код: {current_point.value:g}")
            badge.set_visible(True)

    def _lock_y_axis(self, axis: Axes, limits: Tuple[float, float]) -> None:
        """Фиксирует диапазон Y при масштабировании и перемещении графика."""
        axis.set_ylim(*limits)
        axis.callbacks.connect(
            "ylim_changed",
            lambda changed_axis, fixed_limits=limits: self._restore_y_limits(
                changed_axis, fixed_limits
            ),
        )

    def _restore_y_limits(self, axis: Axes, limits: Tuple[float, float]) -> None:
        """Возвращает зафиксированный Y-диапазон после действий навигации."""
        if self._adjusting_y_limits:
            return
        current_limits = axis.get_ylim()
        if current_limits == limits:
            return

        self._adjusting_y_limits = True
        try:
            axis.set_ylim(*limits)
        finally:
            self._adjusting_y_limits = False

    @staticmethod
    def _draw_numeric_signal(
        axis: Axes,
        points: Sequence[NumericSignalPoint],
        channel_name: str,
        color: str,
        label_offset: int,
        timeline_end: datetime,
    ) -> Optional[Annotation]:
        axis.set_ylabel(f"{channel_name}\nКод ошибки")
        axis.set_ylim(0, ERROR_CODE_MAX)
        axis.set_yticks([0, 22000, 44000, ERROR_CODE_MAX])
        axis.grid(color="#d1d5db", alpha=0.6)
        axis.ticklabel_format(axis="y", style="plain", useOffset=False)
        if not points:
            axis.text(
                0.5,
                0.5,
                "Сигнал отсутствует",
                ha="center",
                va="center",
                transform=axis.transAxes,
            )
            return None
        signal_times = [point.timestamp for point in points]
        signal_values = [point.value for point in points]
        if timeline_end > signal_times[-1]:
            signal_times.append(timeline_end)
            signal_values.append(signal_values[-1])
        axis.step(
            signal_times,
            signal_values,
            where="post",
            color=color,
            linewidth=1.4,
        )
        axis.scatter(
            [point.timestamp for point in points],
            [point.value for point in points],
            color=color,
            s=13,
            zorder=3,
        )
        horizontal_offsets = PlkArchiveWindow._label_horizontal_offsets(points)
        for point, horizontal_offset in zip(points, horizontal_offsets):
            value_label = f"{point.value:g}"
            axis.annotate(
                value_label,
                xy=(point.timestamp, point.value),
                xytext=(horizontal_offset, label_offset),
                textcoords="offset points",
                ha="center",
                va="bottom" if label_offset > 0 else "top",
                color=color,
                fontsize=7.5,
                bbox={
                    "boxstyle": "round,pad=0.12",
                    "fc": "white",
                    "ec": "none",
                    "alpha": 0.85,
                },
                arrowprops=(
                    {
                        "arrowstyle": "-",
                        "color": color,
                        "alpha": 0.55,
                        "linewidth": 0.6,
                    }
                    if horizontal_offset
                    else None
                ),
                zorder=4,
            )
        badge = axis.annotate(
            "",
            xy=(0.985, signal_values[-1]),
            xycoords=("axes fraction", "data"),
            xytext=(-4, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            color="white",
            fontsize=9,
            fontweight="bold",
            bbox={
                "boxstyle": "round,pad=0.3",
                "fc": color,
                "ec": "white",
                "linewidth": 0.8,
                "alpha": 0.95,
            },
            zorder=6,
        )
        return badge

    @staticmethod
    def _draw_leading_channel_signal(
        axis: Axes,
        channel_1: Sequence[BinarySignalPoint],
        channel_2: Sequence[BinarySignalPoint],
        timeline_end: datetime,
    ) -> None:
        """Рисует состояние ведущего канала относительно центральной оси."""
        axis.set_ylim(-1.2, 1.2)
        axis.set_yticks([-1, 0, 1])
        axis.set_yticklabels(["Канал 2 ведущий", "Пассивный", "Канал 1 ведущий"])
        axis.set_ylabel("Канал ведущий")
        axis.grid(False)

        if channel_1:
            times_1 = [point.timestamp for point in channel_1] + [timeline_end]
            values_1 = [1 if point.active else 0 for point in channel_1]
            values_1.append(values_1[-1])
            axis.step(
                times_1,
                values_1,
                where="post",
                color="#2563eb",
                linewidth=2,
                label="Ведущий: канал 1",
                zorder=2,
            )
            axis.fill_between(
                times_1,
                0,
                values_1,
                step="post",
                color="#2563eb",
                alpha=0.1,
                zorder=1,
            )

        if channel_2:
            times_2 = [point.timestamp for point in channel_2] + [timeline_end]
            values_2 = [-1 if point.active else 0 for point in channel_2]
            values_2.append(values_2[-1])
            axis.step(
                times_2,
                values_2,
                where="post",
                color="#9333ea",
                linewidth=2,
                label="Ведущий: канал 2",
                zorder=2,
            )
            axis.fill_between(
                times_2,
                0,
                values_2,
                step="post",
                color="#9333ea",
                alpha=0.1,
                zorder=1,
            )

    @staticmethod
    def _work_mode_categories(
        channel_1: Sequence[CategoricalSignalPoint],
        channel_2: Sequence[CategoricalSignalPoint],
    ) -> List[str]:
        """Создаёт одинаковый порядок режимов для осей обоих каналов."""
        preferred_order = ["ОСТАНОВ", "РАЗВОРОТ (Исходное)", "РПК (Наладка)"]
        observed = {point.state for point in channel_1} | {
            point.state for point in channel_2
        }
        categories = [state for state in preferred_order if state in observed]
        categories.extend(sorted(observed - set(categories)))
        return categories

    @staticmethod
    def _draw_work_mode_signal(
        axis: Axes,
        points: Sequence[CategoricalSignalPoint],
        categories: Sequence[str],
        timeline_end: datetime,
        channel_name: str,
        color: str,
    ) -> None:
        """Рисует режим работы на категориальной вспомогательной оси."""
        axis.set_ylabel(f"Режим работы\n{channel_name}", color=color)
        axis.tick_params(axis="y", colors=color, labelsize=8)
        axis.spines["right"].set_color(color)
        axis.grid(False)

        if not categories:
            axis.set_ylim(-0.5, 0.5)
            axis.set_yticks([])
            return

        levels = {state: index for index, state in enumerate(categories)}
        axis.set_ylim(-0.35, len(categories) - 0.65)
        axis.set_yticks(list(range(len(categories))))
        axis.set_yticklabels(categories)
        if not points:
            return

        times = [point.timestamp for point in points]
        values = [levels[point.state] for point in points]
        marker_count = len(times)
        if timeline_end > times[-1]:
            times.append(timeline_end)
            values.append(values[-1])
        axis.step(
            times,
            values,
            where="post",
            color=color,
            linewidth=1.8,
            linestyle="--",
            marker="s",
            markersize=3.5,
            markevery=range(marker_count),
            zorder=2,
        )

    @staticmethod
    def _label_horizontal_offsets(
        points: Sequence[NumericSignalPoint],
    ) -> List[int]:
        """Разводит подписи близких по времени точек влево и вправо."""
        if not points:
            return []

        timestamps = [point.timestamp for point in points]
        time_span = (max(timestamps) - min(timestamps)).total_seconds()
        cluster_window = max(time_span * 0.015, 0.25)
        offsets: List[int] = []
        cluster_start = timestamps[0]
        position_in_cluster = 0

        for timestamp in timestamps:
            distance = (timestamp - cluster_start).total_seconds()
            if distance > cluster_window:
                cluster_start = timestamp
                position_in_cluster = 0

            if position_in_cluster == 0:
                offsets.append(0)
            else:
                magnitude = ((position_in_cluster + 1) // 2) * 18
                direction = -1 if position_in_cluster % 2 else 1
                offsets.append(direction * magnitude)
            position_in_cluster += 1

        return offsets

    def _on_hover(self, mouse_event: MouseEvent) -> None:
        annotation = self._annotation
        if (
            annotation is None
            or mouse_event.inaxes is None
            or mouse_event.xdata is None
        ):
            return
        axis = mouse_event.inaxes
        x_min, x_max = axis.get_xlim()
        tolerance = (x_max - x_min) * 0.008
        nearest = min(
            self._plotted_events,
            key=lambda item: abs(
                mdates.date2num(item[0].timestamp) - mouse_event.xdata
            ),
            default=None,
        )
        if (
            nearest is None
            or abs(mdates.date2num(nearest[0].timestamp) - mouse_event.xdata)
            > tolerance
        ):
            annotation.set_visible(False)
            self.canvas.draw_idle()
            return
        event, channel_y = nearest
        annotation.xy = (mdates.date2num(event.timestamp), channel_y)
        timestamp_text = f"{event.timestamp:%Y-%m-%d %H:%M:%S.%f}"[:-3]
        annotation.set_text(
            f"{timestamp_text}\n{event.message}\nЗначение: {event.value}"
        )
        annotation.set_visible(True)
        self.canvas.draw_idle()
