import os
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication

import config.config as cfg
from ui.graph_matplot import WindowGraph
from ui.main_window import MainWindowUI


def _application() -> QApplication:
    application = QApplication.instance()
    if application is None:
        application = QApplication([])
    return application


def test_main_window_has_single_selected_signals_group() -> None:
    application = _application()
    window = MainWindowUI("test")

    assert window.gb_selected_signals.title() == "Выбранные сигналы"
    assert not hasattr(window, "gb_secondary_axe")

    window.close()
    application.processEvents()


def test_each_signal_gets_separate_left_y_axis(tmp_path, monkeypatch) -> None:
    application = _application()
    monkeypatch.setattr(cfg, "PLOT_FILENAME", str(tmp_path / "plot.png"))
    data = pd.DataFrame(
        {
            "time": [0.0, 1.0, 2.0],
            "signal_a": [1.0, 2.0, 3.0],
            "signal_b": [100.0, 200.0, 300.0],
            "signal_c": [-1.0, 0.0, 1.0],
        }
    )
    window = WindowGraph(
        data=data,
        selected_signals=["signal_a", "signal_b", "signal_c"],
        time_signals="time",
        filenames=["test.csv"],
        step=1,
    )

    axes = [window.signal_axes[name] for name in window.selected_signals]
    assert len({id(axis) for axis in axes}) == 3
    assert [axis.get_ylabel() for axis in axes] == window.selected_signals
    assert axes[1].spines["left"].get_position() == ("outward", 65)
    assert axes[2].spines["left"].get_position() == ("outward", 130)
    assert all(axes[0].get_shared_x_axes().joined(axes[0], axis) for axis in axes[1:])
    assert isinstance(axes[0].xaxis.get_major_locator(), ticker.LinearLocator)
    assert len(axes[0].get_xticks()) == 11
    assert axes[0].get_xlabel() == "time"
    assert all(tick.get_rotation() == 0 for tick in axes[0].get_xticklabels())
    assert not axes[0].xaxis.get_offset_text().get_visible()

    window.close()
    application.processEvents()


def test_similar_signals_have_synchronized_y_scale(tmp_path, monkeypatch) -> None:
    application = _application()
    monkeypatch.setattr(cfg, "PLOT_FILENAME", str(tmp_path / "plot.png"))
    data = pd.DataFrame(
        {
            "time": [0.0, 1.0, 2.0, 3.0],
            "first": [314.0, 316.0, 318.0, 320.0],
            "second": [313.8, 316.1, 318.2, 319.9],
            "different": [0.0, 25.0, 50.0, 100.0],
        }
    )
    window = WindowGraph(
        data=data,
        selected_signals=["first", "second", "different"],
        time_signals="time",
        filenames=["test.csv"],
        step=1,
    )

    first_axis = window.signal_axes["first"]
    second_axis = window.signal_axes["second"]
    different_axis = window.signal_axes["different"]
    assert first_axis.get_ylim() == second_axis.get_ylim()
    assert np.allclose(
        np.diff(first_axis.get_yticks()), np.diff(second_axis.get_yticks())
    )
    assert different_axis.get_ylim() != first_axis.get_ylim()

    window.close()
    application.processEvents()


def test_plot_margins_keep_constant_physical_size(tmp_path, monkeypatch) -> None:
    application = _application()
    monkeypatch.setattr(cfg, "PLOT_FILENAME", str(tmp_path / "plot.png"))
    data = pd.DataFrame(
        {
            "time": [0.0, 1.0],
            "first": [1.0, 2.0],
            "second": [1.1, 2.1],
            "third": [0.9, 1.9],
            "fourth": [1.2, 2.2],
            "fifth": [0.8, 1.8],
        }
    )
    window = WindowGraph(
        data=data,
        selected_signals=["first", "second", "third", "fourth", "fifth"],
        time_signals="time",
        filenames=["test.csv"],
        step=1,
    )

    window.figure.set_size_inches(10, 8)
    window._adjust_plot_layout()
    compact_left_inches = window.ax1.get_position().x0 * window.figure.get_figwidth()
    window.figure.set_size_inches(20, 10)
    window._adjust_plot_layout()
    wide_left_inches = window.ax1.get_position().x0 * window.figure.get_figwidth()

    assert compact_left_inches == wide_left_inches
    assert len(window.signal_axes) == 5
    assert [
        axis.spines["left"].get_position()
        for axis in list(window.signal_axes.values())[1:]
    ] == [("outward", 65.0), ("outward", 130.0), ("outward", 195.0), ("outward", 260.0)]
    assert window.centralWidget().layout().itemAt(0).widget().maximumWidth() == 360

    window.close()
    application.processEvents()


def test_movable_marker_displays_value_on_each_y_axis(tmp_path, monkeypatch) -> None:
    application = _application()
    monkeypatch.setattr(cfg, "PLOT_FILENAME", str(tmp_path / "plot.png"))
    data = pd.DataFrame(
        {
            "time": [0.0, 1.0, 2.0],
            "first": [10.0, 11.0, 12.0],
            "second": [20.0, 21.0, 22.0],
            "third": [30.0, 31.0, 32.0],
            "fourth": [40.0, 41.0, 42.0],
            "fifth": [50.0, 51.0, 52.0],
        }
    )
    signals = ["first", "second", "third", "fourth", "fifth"]
    window = WindowGraph(
        data=data,
        selected_signals=signals,
        time_signals="time",
        filenames=["test.csv"],
        step=1,
    )

    active_axis = window.signal_axes["fifth"]
    window.on_marker_press(SimpleNamespace(button=1, inaxes=active_axis, xdata=0.2))
    assert window.marker_dragging
    window.on_marker_move(SimpleNamespace(inaxes=active_axis, xdata=1.8))
    window.on_marker_release(SimpleNamespace(button=1))

    assert window.marker_index == 2
    assert not window.marker_dragging
    assert window.vline.get_visible()
    assert window.annotation.get_visible()
    assert "0:00:02" in window.annotation.get_text()
    assert [window.marker_labels[signal].get_text() for signal in signals] == [
        "12.000",
        "22.000",
        "32.000",
        "42.000",
        "52.000",
    ]
    assert all(label.get_visible() for label in window.marker_labels.values())

    window.close()
    application.processEvents()


def test_datetime_x_axis_matches_plc_archive_style(tmp_path, monkeypatch) -> None:
    application = _application()
    monkeypatch.setattr(cfg, "PLOT_FILENAME", str(tmp_path / "plot.png"))
    data = pd.DataFrame(
        {
            "date/time": [
                "2026-08-24 10:17:44,293",
                "2026-08-24 10:17:45,293",
                "2026-08-24 10:17:46,293",
                "2026-08-24 10:17:47,293",
            ],
            "signal": [1.0, 2.0, 3.0, 4.0],
        }
    )
    window = WindowGraph(
        data=data,
        selected_signals=["signal"],
        time_signals="date/time",
        filenames=["test.csv"],
        step=1,
    )

    axis = window.signal_axes["signal"]
    tick_labels = [tick.get_text() for tick in axis.get_xticklabels()]
    assert window.x_is_datetime
    assert len(axis.get_xticks()) == 11
    assert all(":" in label and "2026" not in label for label in tick_labels)
    assert axis.get_xlabel().startswith("Дата и время (диапазон: ")
    assert window.date_label is not None
    assert window.date_label.get_text() == "Дата: 24.08.2026"
    assert window.date_label.get_position() == (0, -42)
    assert window.date_label.get_annotation_clip() is False

    window.close()
    application.processEvents()


def test_datetime_labels_do_not_reorder_signal_points(tmp_path, monkeypatch) -> None:
    application = _application()
    monkeypatch.setattr(cfg, "PLOT_FILENAME", str(tmp_path / "plot.png"))
    data = pd.DataFrame(
        {
            "date/time": [
                "2026-08-24 10:17:46,293",
                "2026-08-24 10:17:44,293",
                "2026-08-24 10:17:47,293",
                "2026-08-24 10:17:45,293",
            ],
            "signal": [30.0, 10.0, 40.0, 20.0],
        }
    )
    window = WindowGraph(
        data=data,
        selected_signals=["signal"],
        time_signals="date/time",
        filenames=["test.csv"],
        step=1,
    )

    line = window.lines_list[0]
    plotted_x = np.asarray(line.get_xdata(orig=False), dtype=float)
    assert np.all(np.diff(plotted_x) >= 0)
    assert line.get_ydata().tolist() == [30.0, 10.0, 40.0, 20.0]
    assert window.displayed_data_indices.tolist() == [0, 1, 2, 3]

    window.close()
    application.processEvents()
