from __future__ import annotations

import sys
import random
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import ViewBox

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
    QToolBar,
    QAction,
    QActionGroup,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QColor, QPen, QFont, QPolygon
from PyQt5.QtCore import QPoint, QRect

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import *
from logic.regulator_analyzer import RegulatorAnalyzer

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")

_SIGNAL_COLORS = [
    "#1f77b4", "#ff7f0e", "#2ca02c",
    "#d62728", "#9467bd", "#8c564b", "#e377c2",
    "#17becf", "#bcbd22", "#7f7f7f",
]

# ---------------------------------------------------------------------------
# Иконки рисуем программно — не нужны внешние файлы
# ---------------------------------------------------------------------------

def _make_icon(draw_fn, size: int = 28) -> QIcon:
    """Создаёт QIcon через функцию рисования на QPixmap."""
    px = QPixmap(size, size)
    px.fill(Qt.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.Antialiasing)
    draw_fn(p, size)
    p.end()
    return QIcon(px)


def _icon_pointer(p: QPainter, s: int) -> None:
    """Курсор / режим выделения."""
    pen = QPen(QColor("#333"), 1.8)
    p.setPen(pen)
    p.setBrush(QColor("#333"))
    pts = [QPoint(6, 4), QPoint(6, 20), QPoint(10, 16), QPoint(13, 22),
           QPoint(15, 21), QPoint(12, 15), QPoint(17, 15)]
    p.drawPolygon(QPolygon(pts))


def _icon_zoom_out(p: QPainter, s: int) -> None:
    pen = QPen(QColor("#333"), 2)
    p.setPen(pen)
    c, r = s // 2 - 2, s // 2 - 5
    p.drawEllipse(QPoint(c, c), r, r)
    p.drawLine(c + r - 1, c + r - 1, s - 4, s - 4)
    p.drawLine(c - 3, c, c + 3, c)


def _icon_zoom_in(p: QPainter, s: int) -> None:
    pen = QPen(QColor("#333"), 2)
    p.setPen(pen)
    c, r = s // 2 - 2, s // 2 - 5
    p.drawEllipse(QPoint(c, c), r, r)
    p.drawLine(c + r - 1, c + r - 1, s - 4, s - 4)
    p.drawLine(c - 3, c, c + 3, c)
    p.drawLine(c, c - 3, c, c + 3)


def _icon_zoom_rect(p: QPainter, s: int) -> None:
    """Масштабирование прямоугольником."""
    pen = QPen(QColor("#333"), 1.8)
    p.setPen(pen)
    c, r = s // 2 - 2, s // 2 - 5
    p.drawEllipse(QPoint(c, c), r, r)
    p.drawLine(c + r - 1, c + r - 1, s - 4, s - 4)
    # маленький прямоугольник внутри лупы
    pen2 = QPen(QColor("#1f77b4"), 1.4)
    p.setPen(pen2)
    p.drawRect(c - 3, c - 3, 5, 5)


def _icon_fit(p: QPainter, s: int) -> None:
    """Вписать всё в экран."""
    pen = QPen(QColor("#d62728"), 2)
    p.setPen(pen)
    m = 5
    p.drawRect(m, m, s - 2 * m, s - 2 * m)
    pen2 = QPen(QColor("#1f77b4"), 1.5)
    p.setPen(pen2)
    # диагональные стрелки к углам
    for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        cx, cy = s // 2, s // 2
        p.drawLine(cx, cy, cx + dx * 6, cy + dy * 6)


def _icon_pan(p: QPainter, s: int) -> None:
    """Перемещение (рука)."""
    pen = QPen(QColor("#333"), 1.6)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    # ладонь
    p.drawRoundedRect(8, 12, 12, 11, 2, 2)
    # пальцы
    for x in [9, 12, 15, 18]:
        p.drawLine(x, 12, x, 7)
    p.drawLine(8, 10, 6, 8)


def _icon_separator(p: QPainter, s: int) -> None:
    pass


def _icon_export(p: QPainter, s: int) -> None:
    """Экспорт / сохранить."""
    pen = QPen(QColor("#d62728"), 2)
    p.setPen(pen)
    m = 5
    # страница
    p.drawRect(m, m, s - 2 * m - 4, s - 2 * m)
    # стрелка вниз
    pen2 = QPen(QColor("#333"), 2)
    p.setPen(pen2)
    cx = s // 2 + 4
    p.drawLine(cx, 8, cx, 18)
    p.drawLine(cx - 3, 15, cx, 18)
    p.drawLine(cx + 3, 15, cx, 18)


def _icon_settings(p: QPainter, s: int) -> None:
    """Шестерёнка / настройки."""
    pen = QPen(QColor("#333"), 1.8)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    cx, cy, r = s // 2, s // 2, 5
    p.drawEllipse(QPoint(cx, cy), r, r)
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        x1 = int(cx + (r + 1) * math.cos(rad))
        y1 = int(cy + (r + 1) * math.sin(rad))
        x2 = int(cx + (r + 3) * math.cos(rad))
        y2 = int(cy + (r + 3) * math.sin(rad))
        p.drawLine(x1, y1, x2, y2)


# ---------------------------------------------------------------------------


class WindowGraph(QMainWindow):
    """
    Окно для отображения графиков данных с возможностью настройки.
    Каждый сигнал отображается на своей собственной независимой оси Y слева.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        signals: List[str],
        time_signals: str,
        filenames: List[str],
        step: int = 10,
        enable_analys: bool = False,
    ) -> None:
        super().__init__()

        self.data = data
        self.signals = signals
        self.time_signals = time_signals
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

        self.plot_items: Dict[str, pg.PlotDataItem] = {}
        self.checkboxes: Dict[str, QCheckBox] = {}
        self.line_visibility: Dict[str, bool] = {}

        self.vline: Optional[pg.InfiniteLine] = None
        self.annotation: Optional[pg.TextItem] = None
        self._x_numeric: Optional[np.ndarray] = None

        self._signal_viewboxes: Dict[str, ViewBox] = {}
        self._signal_axes: Dict[str, pg.AxisItem] = {}
        self._sync_connections: list = []

        # Текущий режим взаимодействия
        self._mode: str = "pan"  # "pan" | "zoom_rect"

        self.init_ui()
        self.plot_graphs()
        self._save_plot()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def init_ui(self) -> None:
        self.setWindowTitle("Графики")
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        main_layout.addWidget(self._build_control_panel(), stretch=1)

        # Обёртка: вертикальный toolbar + график
        graph_wrapper = QWidget()
        graph_h_layout = QHBoxLayout(graph_wrapper)
        graph_h_layout.setSpacing(0)
        graph_h_layout.setContentsMargins(0, 0, 0, 0)
        graph_h_layout.addWidget(self._build_toolbar())
        graph_h_layout.addWidget(self._build_graph_panel(), stretch=1)

        main_layout.addWidget(graph_wrapper, stretch=4)

    def _build_toolbar(self) -> QToolBar:
        """Вертикальная панель инструментов слева от графика."""
        tb = QToolBar()
        tb.setOrientation(Qt.Vertical)
        tb.setIconSize(QSize(28, 28))
        tb.setMovable(False)
        tb.setStyleSheet("""
            QToolBar {
                background: #f0f0f0;
                border-right: 1px solid #ccc;
                spacing: 2px;
                padding: 4px 2px;
            }
            QToolButton {
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 3px;
                margin: 1px;
            }
            QToolButton:hover {
                background: #dde8f5;
                border-color: #aac4e0;
            }
            QToolButton:checked {
                background: #c5d8f0;
                border-color: #6699cc;
            }
        """)

        # Группа эксклюзивных режимов
        mode_group = QActionGroup(self)
        mode_group.setExclusive(True)

        # — Режим перемещения (pan)
        act_pan = QAction(_make_icon(_icon_pan), "Перемещение", self)
        act_pan.setCheckable(True)
        act_pan.setChecked(True)
        act_pan.setToolTip("Перемещение (Pan)")
        act_pan.triggered.connect(lambda: self._set_mode("pan"))
        mode_group.addAction(act_pan)
        tb.addAction(act_pan)

        tb.addSeparator()

        # — Zoom out
        act_zout = QAction(_make_icon(_icon_zoom_out), "Уменьшить", self)
        act_zout.setToolTip("Уменьшить масштаб")
        act_zout.triggered.connect(self._zoom_out)
        tb.addAction(act_zout)

        # — Zoom in
        act_zin = QAction(_make_icon(_icon_zoom_in), "Увеличить", self)
        act_zin.setToolTip("Увеличить масштаб")
        act_zin.triggered.connect(self._zoom_in)
        tb.addAction(act_zin)

        # — Zoom rect (выделение прямоугольником)
        act_zrect = QAction(_make_icon(_icon_zoom_rect), "Масштаб прямоугольником", self)
        act_zrect.setCheckable(True)
        act_zrect.setToolTip("Масштабирование прямоугольником")
        act_zrect.triggered.connect(lambda: self._set_mode("zoom_rect"))
        mode_group.addAction(act_zrect)
        tb.addAction(act_zrect)

        tb.addSeparator()

        # — Вписать всё
        act_fit = QAction(_make_icon(_icon_fit), "Вписать", self)
        act_fit.setToolTip("Показать все данные")
        act_fit.triggered.connect(self._fit_all)
        tb.addAction(act_fit)

        # — Вписать по X
        act_fitx = QAction(_make_icon(_icon_pointer), "Вписать по X", self)
        act_fitx.setToolTip("Вписать по оси X")
        act_fitx.triggered.connect(self._fit_x)
        tb.addAction(act_fitx)

        tb.addSeparator()

        # — Экспорт PNG
        act_export = QAction(_make_icon(_icon_export), "Сохранить PNG", self)
        act_export.setToolTip("Сохранить график как PNG")
        act_export.triggered.connect(self._export_png)
        tb.addAction(act_export)

        # — Настройки вида
        act_cfg = QAction(_make_icon(_icon_settings), "Настройки", self)
        act_cfg.setToolTip("Настройки отображения")
        act_cfg.triggered.connect(self._open_view_settings)
        tb.addAction(act_cfg)

        self._toolbar = tb
        return tb

    def _build_control_panel(self) -> QGroupBox:
        panel = QGroupBox("Панель настройки")
        layout = QVBoxLayout()
        layout.addWidget(self._build_sampling_group(), stretch=1)
        layout.addWidget(self._build_visibility_scroll(), stretch=6)
        layout.addWidget(self._build_regulator_group(), stretch=1)
        panel.setLayout(layout)
        return panel

    def _build_sampling_group(self) -> QGroupBox:
        group = QGroupBox("Шаг выборки")
        layout = QVBoxLayout()

        self.points_combobox = QComboBox()
        self.points_combobox.addItems(["1", "10", "100", "1000"])
        self.points_combobox.setCurrentText(str(self.step))

        self.points_all_label = QLabel(f"Кол-во исходных данных: {len(self.data)}")
        self.points_label = QLabel(
            f"Кол-во отображаемых данных: {len(self.data) // self.step}"
        )

        update_button = QPushButton("Обновить графики")
        update_button.clicked.connect(self.update_graphs)

        for w in (self.points_combobox, self.points_all_label,
                  self.points_label, update_button):
            layout.addWidget(w)

        group.setLayout(layout)
        return group

    def _build_visibility_scroll(self) -> QScrollArea:
        group = QGroupBox("Видимость сигналов")
        layout = QVBoxLayout()
        self._add_signal_checkboxes(layout)
        layout.addStretch()
        group.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(group)
        return scroll

    def _build_regulator_group(self) -> QGroupBox:
        group = QGroupBox("Анализ регулятора ГСМ")
        layout = QVBoxLayout()
        analyze_button = QPushButton("Анализ регулятора")
        analyze_button.setEnabled(self.enable_analys)
        analyze_button.clicked.connect(self.analyze_regulator)
        layout.addWidget(analyze_button)
        group.setLayout(layout)
        return group

    def _build_graph_panel(self) -> QGroupBox:
        panel = QGroupBox("Графики")
        layout = QVBoxLayout()
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.showGrid(x=True, y=True, alpha=0.4)
        layout.addWidget(self.plot_widget)
        panel.setLayout(layout)
        return panel

    def _add_signal_checkboxes(self, layout: QVBoxLayout) -> None:
        layout.addWidget(QLabel("Сигналы:"))
        for i, signal in enumerate(self.signals):
            color = _SIGNAL_COLORS[i % len(_SIGNAL_COLORS)]
            cb = QCheckBox(signal)
            cb.setChecked(True)
            cb.setStyleSheet(f"color: {color};")
            cb.stateChanged.connect(self.toggle_signal_visibility)
            layout.addWidget(cb)
            self.checkboxes[signal] = cb
            self.line_visibility[signal] = True

    # ------------------------------------------------------------------
    # Toolbar actions
    # ------------------------------------------------------------------

    def _set_mode(self, mode: str) -> None:
        """Переключает режим взаимодействия с графиком."""
        self._mode = mode
        vb: ViewBox = self.plot_widget.getPlotItem().vb
        if mode == "pan":
            vb.setMouseMode(ViewBox.PanMode)
        elif mode == "zoom_rect":
            vb.setMouseMode(ViewBox.RectMode)

    def _zoom_in(self) -> None:
        self.plot_widget.getPlotItem().vb.scaleBy((0.7, 0.7))

    def _zoom_out(self) -> None:
        self.plot_widget.getPlotItem().vb.scaleBy((1.4, 1.4))

    def _fit_all(self) -> None:
        """Вписывает все данные по обеим осям."""
        self.plot_widget.getPlotItem().vb.autoRange()
        for vb in self._signal_viewboxes.values():
            vb.autoRange()

    def _fit_x(self) -> None:
        """Вписывает данные только по оси X."""
        x = self._get_x_numeric()
        if len(x) == 0:
            return
        self.plot_widget.getPlotItem().vb.setXRange(x.min(), x.max(), padding=0.02)

    def _export_png(self) -> None:
        """Открывает диалог экспорта pyqtgraph."""
        exporter = pg.exporters.ImageExporter(self.plot_widget.getPlotItem())
        exporter.export()  # показывает диалог сохранения

    def _open_view_settings(self) -> None:
        """Открывает встроенный диалог настроек pyqtgraph."""
        self.plot_widget.getPlotItem().ctrlMenu.popup(
            self._toolbar.mapToGlobal(self._toolbar.rect().topRight())
        )

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def toggle_signal_visibility(self) -> None:
        sender = self.sender()
        if isinstance(sender, QCheckBox):
            signal = sender.text()
            visible = sender.isChecked()
            self.line_visibility[signal] = visible
            if signal in self.plot_items:
                self.plot_items[signal].setVisible(visible)
            if signal in self._signal_axes:
                self._signal_axes[signal].setVisible(visible)

    def update_graphs(self) -> None:
        self.step = int(self.points_combobox.currentText())
        self.points_label.setText(
            f"Кол-во отображаемых данных: {len(self.data) // self.step}"
        )
        self.plot_graphs()
        self._save_plot()

    # ------------------------------------------------------------------
    # Plotting
    # ------------------------------------------------------------------

    def _get_x_numeric(self) -> np.ndarray:
        if self._x_numeric is not None:
            return self._x_numeric

        x_series = self.data[self.time_signals]
        numeric = pd.to_numeric(x_series, errors="coerce")

        if not numeric.isna().all():
            self._x_numeric = numeric.to_numpy(dtype=float)
            return self._x_numeric

        try:
            dt = pd.to_datetime(x_series, format="%Y-%m-%d %H:%M:%S,%f")
            self._x_numeric = (dt.astype("int64") // 10**9).to_numpy(dtype=float)
        except Exception:
            self._x_numeric = np.arange(len(x_series), dtype=float)

        return self._x_numeric

    def _remove_all_extra_axes(self) -> None:
        pw = self.plot_widget
        plot_item = pw.getPlotItem()

        for fn in self._sync_connections:
            try:
                plot_item.vb.sigResized.disconnect(fn)
            except Exception:
                pass
        self._sync_connections.clear()

        for vb in self._signal_viewboxes.values():
            try:
                pw.scene().removeItem(vb)
            except Exception:
                pass

        for ax in self._signal_axes.values():
            try:
                plot_item.layout.removeItem(ax)
            except Exception:
                pass

        self._signal_viewboxes.clear()
        self._signal_axes.clear()

    def plot_graphs(self) -> None:
        self.plot_items.clear()
        self._x_numeric = None

        pw = self.plot_widget
        pw.clear()
        self._remove_all_extra_axes()

        if self.data.empty:
            pw.setTitle("Нет данных для отображения")
            return

        self._set_graph_title()

        x_sampled = self._get_x_numeric()[:: self.step]
        plot_item: pg.PlotItem = pw.getPlotItem()
        plot_item.setLabel("bottom", self.time_signals)

        plot_item.hideAxis("left")
        plot_item.hideAxis("right")

        AXIS_COL_WIDTH = 70

        for i, signal in enumerate(self.signals):
            if signal not in self.data.columns:
                continue

            color = _SIGNAL_COLORS[i % len(_SIGNAL_COLORS)]
            y_sampled = self.data[signal].to_numpy(dtype=float)[:: self.step]
            pen = pg.mkPen(color=color, width=2)

            vb = ViewBox()
            plot_item.scene().addItem(vb)
            vb.setXLink(plot_item.vb)

            col_index = 1 - i
            plot_item.layout.setColumnMinimumWidth(col_index, AXIS_COL_WIDTH)

            ax = pg.AxisItem("left")
            ax.setLabel(signal, color=color)
            ax.setPen(pg.mkPen(color=color, width=1))
            ax.setTextPen(pg.mkPen(color=color))
            ax.linkToView(vb)
            plot_item.layout.addItem(ax, 2, col_index)
            ax.setVisible(self.line_visibility.get(signal, True))

            self._signal_viewboxes[signal] = vb
            self._signal_axes[signal] = ax

            def _make_sync(_vb: ViewBox, _pi: pg.PlotItem):
                def _sync():
                    _vb.setGeometry(_pi.vb.sceneBoundingRect())
                    _vb.linkedViewChanged(_pi.vb, _vb.XAxis)
                return _sync

            sync_fn = _make_sync(vb, plot_item)
            self._sync_connections.append(sync_fn)
            plot_item.vb.sigResized.connect(sync_fn)

            item = pg.PlotDataItem(x_sampled, y_sampled, pen=pen, name=signal)
            item.setVisible(self.line_visibility.get(signal, True))
            vb.addItem(item)
            self.plot_items[signal] = item

        # Применяем текущий режим
        self._set_mode(self._mode)

        self._add_legend(plot_item)
        self._setup_crosshair(plot_item)
        pw.scene().sigMouseMoved.connect(self.on_mouse_move)

        from PyQt5.QtCore import QTimer
        QTimer.singleShot(0, self._sync_all_viewboxes)

    def _sync_all_viewboxes(self) -> None:
        plot_item: pg.PlotItem = self.plot_widget.getPlotItem()
        rect = plot_item.vb.sceneBoundingRect()
        for vb in self._signal_viewboxes.values():
            vb.setGeometry(rect)
            vb.linkedViewChanged(plot_item.vb, vb.XAxis)

    def _add_legend(self, plot_item: pg.PlotItem) -> None:
        legend = plot_item.addLegend(offset=(10, 10))
        for signal, item in self.plot_items.items():
            if self.line_visibility.get(signal, True):
                legend.addItem(item, signal)

    def _setup_crosshair(self, plot_item: pg.PlotItem) -> None:
        self.vline = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen("k", width=1, style=Qt.DashLine),
        )
        self.vline.setVisible(False)
        plot_item.addItem(self.vline, ignoreBounds=True)

        self.annotation = pg.TextItem(
            text="",
            color="k",
            border=pg.mkPen("gray"),
            fill=pg.mkBrush(255, 255, 255, 220),
        )
        self.annotation.setFont(pg.Qt.QtGui.QFont("Courier", 8))
        self.annotation.setVisible(False)
        plot_item.addItem(self.annotation, ignoreBounds=True)

    def _set_graph_title(self) -> None:
        filename = self.filenames[0] if self.filenames else ""
        if not filename:
            title = "Не выбран файл с данными"
        elif (idx := filename.find("ШУР")) != -1:
            title = f"ТГ-{filename[idx + 3]}/ШУР-{filename[idx + 4]}"
        elif (idx := filename.find("ТГ")) != -1:
            title = f"ТГ-{filename[idx + 2]}/ШУР-{filename[idx + 3]}"
        elif "ШСП" in filename:
            title = f"ШСП-{filename[2:3]}"
        else:
            title = "Тестовый файл"
        self.plot_widget.setTitle(title)

    # ------------------------------------------------------------------
    # Mouse interaction
    # ------------------------------------------------------------------

    def on_mouse_move(self, pos) -> None:
        if self.vline is None or self.annotation is None:
            return

        plot_item: pg.PlotItem = self.plot_widget.getPlotItem()

        if not plot_item.sceneBoundingRect().contains(pos):
            self.vline.setVisible(False)
            self.annotation.setVisible(False)
            return

        x = plot_item.vb.mapSceneToView(pos).x()
        x_num = self._get_x_numeric()

        if len(x_num) == 0:
            return

        idx = int(np.nanargmin(np.abs(x_num - x)))
        self.vline.setPos(x_num[idx])
        self.vline.setVisible(True)

        x_val = self.data[self.time_signals].iloc[idx]
        text_lines = [f"Время: {self.format_time(x_val)}"]
        text_lines += [
            f"{signal}: {self.data[signal].iloc[idx]:.2f}"
            for signal in self.signals
            if signal in self.data.columns and self.line_visibility.get(signal, False)
        ]

        if len(text_lines) <= 1:
            self.annotation.setVisible(False)
            return

        self.annotation.setText("\n".join(text_lines))
        y_range = plot_item.vb.viewRange()[1]
        y_pos = y_range[0] + (y_range[1] - y_range[0]) * 0.05
        self.annotation.setPos(x_num[idx], y_pos)
        self.annotation.setVisible(True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def format_time(timestamp) -> str:
        if isinstance(timestamp, pd.Timestamp):
            return timestamp.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        if isinstance(timestamp, (int, float)):
            return str(timedelta(seconds=float(timestamp)))
        return str(timestamp)

    def analyze_regulator(self) -> None:
        self.analyzer.save_to_pdf()

    def _save_plot(self) -> None:
        try:
            os.makedirs(REPORT_DIR, exist_ok=True)
            exporter = pg.exporters.ImageExporter(self.plot_widget.getPlotItem())
            exporter.parameters()["width"] = 1500
            exporter.export(PLOT_FILENAME)
            print(f"Plot saved to {PLOT_FILENAME}")
        except Exception as e:
            print(f"Ошибка при сохранении графика: {e}")


# ----------------------------------------------------------------------
# Demo / entry point
# ----------------------------------------------------------------------

def main() -> None:
    number_data = 10_000
    x = np.linspace(0, 10, number_data)

    first_signal = "Очень длинный сигнал"
    clean_signal = np.piecewise(
        x, [x <= 8, x > 8], [250, lambda t: 250 - 2.5 * (t - 8)]
    )
    noisy_signal = clean_signal + np.random.normal(0, 0.1, number_data)

    reference_values = [
        0, 10, 20, 10, 30, 10, 60, 10, 100, 110,
        100, 120, 100, 150, 100, 200, 210, 200, 220,
        200, 250, 200, 300, 320, 300, 10, 0,
    ]
    jump_times = np.linspace(0, 10, len(reference_values), endpoint=False)
    step_graph = np.zeros_like(x)
    for t, val in zip(jump_times, reference_values):
        step_graph[x >= t] = val

    # список из 10 000 строк-меток времени, равномерно распределённых на интервале 100 секунд 
    # начиная с 2018-03-09 14:29:18,560 с шагом 10 мс
    start_time = datetime.strptime("2018-03-09 14:29:18,560", "%Y-%m-%d %H:%M:%S,%f")
    timestamps = [
        (start_time + timedelta(seconds=float(s))).strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
        for s in np.linspace(0, 100, number_data)
    ]
    
    df = pd.DataFrame({
        first_signal: noisy_signal,
        "ГСМ-А.Текущее положение": step_graph,
        "Значение развертки. Положение ГСМ": step_graph,
        "ОЗ-А": [5 + random.randint(-1, 1) for _ in x],
        "ОЗ-Б": [random.randint(-1, 1) for _ in x],
        COMMON_TIME: timestamps,
    })

    all_signals = [
        first_signal,
        "ГСМ-А.Текущее положение",
        "Значение развертки. Положение ГСМ",
        "ОЗ-А",
        "ОЗ-Б",
    ]

    app = QApplication(sys.argv)
    window = WindowGraph(
        data=df,
        signals=all_signals,
        time_signals=COMMON_TIME,
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
