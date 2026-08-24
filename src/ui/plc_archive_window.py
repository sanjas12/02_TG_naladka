from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple

import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
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
    ComparisonResult,
    PlkEvent,
    compare_events,
    load_plk_archive,
)

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class PlkArchiveWindow(QMainWindow):
    """Сравнение синхронизированных архивов двух каналов PLK."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.channel_1: List[PlkEvent] = []
        self.channel_2: List[PlkEvent] = []
        self._plotted_events: List[Tuple[PlkEvent, int]] = []
        self._annotation = None

        self.setWindowTitle("Анализ архивов PLK")
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
            logger.error("Ошибка чтения архива PLK", exc_info=True)
            QMessageBox.critical(self, "Ошибка архива PLK", str(error))

    def _refresh_plot(self) -> None:
        if not self.channel_1 or not self.channel_2:
            return
        result = compare_events(
            self.channel_1, self.channel_2, tolerance_ms=self.tolerance.value()
        )
        self._draw_timeline(result)

    def _draw_timeline(self, result: ComparisonResult) -> None:
        self.figure.clear()
        axis = self.figure.add_subplot(111)
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
        axis.set_xlabel("Дата и время")
        axis.grid(axis="x", color="#d1d5db", alpha=0.6)
        locator = mdates.AutoDateLocator(minticks=5, maxticks=12)
        axis.xaxis.set_major_locator(locator)
        axis.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
        axis.legend(loc="upper right")

        deltas = [abs(pair.delta_ms) for pair in result.pairs]
        max_delta = max(deltas) if deltas else 0
        self.summary.setText(
            f"Канал 1: {len(self.channel_1)} | Канал 2: {len(self.channel_2)} | "
            f"пар: {len(result.pairs)} | расхождений: "
            f"{len(result.only_channel_1) + len(result.only_channel_2)} | "
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

    def _on_hover(self, mouse_event) -> None:
        if (
            not self._annotation
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
            self._annotation.set_visible(False)
            self.canvas.draw_idle()
            return
        event, channel_y = nearest
        self._annotation.xy = (mdates.date2num(event.timestamp), channel_y)
        timestamp_text = f"{event.timestamp:%Y-%m-%d %H:%M:%S.%f}"[:-3]
        self._annotation.set_text(
            f"{timestamp_text}\n{event.message}\nЗначение: {event.value}"
        )
        self._annotation.set_visible(True)
        self.canvas.draw_idle()
