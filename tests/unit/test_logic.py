from pathlib import Path
from types import SimpleNamespace

import pandas as pd

from logic.logic import (
    FileHandler,
    PlotManager,
    SignalManager,
    detect_archive_project,
    unwrap_timestamp_counter,
)
from model.basemodel import Model

VEIK_DIAGRAM = (
    Path(__file__).resolve().parents[2]
    / "input"
    / "veik"
    / "diagram_1789700659884-2-1_22092026_203708_206256.csv"
)


def test_archive_project_detection_uses_headers_before_path() -> None:
    assert (
        detect_archive_project(
            "D:/archives/sarz/diagram.csv",
            ["Время ЭМП, с", "Напряжение заряда ГИТ, кВ"],
        )
        == "ВЭИК"
    )
    assert (
        detect_archive_project(
            "D:/archives/unknown.csv",
            [
                "Значение развертки. Положение ГСМ",
                "ГСМ-А.Текущее положение",
            ],
        )
        == "САРЗ"
    )


def test_archive_project_detection_falls_back_to_path_and_format() -> None:
    assert detect_archive_project("D:/input/veik/archive.log", ["timestamp"]) == "ВЭИК"
    assert detect_archive_project("D:/input/rk/archive.csv", ["дата/время"]) == "РК"
    assert detect_archive_project("D:/input/САРЗ/archive.csv", ["time"]) == "САРЗ"
    assert detect_archive_project("D:/input/archive.csv", ["time"], True) == "САРЗ"
    assert detect_archive_project("D:/input/archive.csv", ["time"]) == "Не определён"


def test_archive_project_detection_recognizes_rk_headers() -> None:
    assert (
        detect_archive_project(
            "D:/input/archive.csv",
            [
                "Этот канал: ошибка управления ЭМП РК ВД 2",
                "Этот канал: контур позиционирования СМ РК НД 1 в работе",
            ],
        )
        == "РК"
    )


def test_log_format_detects_comma_delimiter_and_decimal_point() -> None:
    model = Model()
    handler = FileHandler(model)
    sample = b"timestamp,Driver Current,Wiring Current\r\n8652,0.0471145,0.0472218\r\n"

    handler._detect_file_params(sample, b"8652,0.0471145,0.0472218\r\n")

    assert model.delimiter == ","
    assert model.decimal == "."


def test_timestamp_header_is_recognized_as_time_axis() -> None:
    model = Model()
    manager = SignalManager(model, SimpleNamespace())

    manager._process_headers(
        pd.DataFrame(columns=["timestamp", "Driver Current", "Wiring Current"])
    )

    assert model.is_time is True
    assert model.time_signal == "timestamp"


def test_veik_diagram_detects_complete_time_axis_and_all_columns() -> None:
    model = Model(filenames=[str(VEIK_DIAGRAM)], first_filename=str(VEIK_DIAGRAM))
    handler = FileHandler(model)

    assert handler.analyze_file(str(VEIK_DIAGRAM))
    assert model.delimiter == ";"
    assert model.decimal == "."

    manager = SignalManager(model, SimpleNamespace())
    assert manager.load_all_signals()
    assert model.is_time
    assert model.time_signal == "Время ЭМП, с"
    assert model.has_veik_dual_time
    assert model.archive_project == "ВЭИК"
    assert list(model.dict_all_signals) == [
        "Напряжение заряда ГИТ, кВ",
        "Время ЭМП, с",
        "Положение верхнего пуансона, мм",
        "Положение нижнего пуансона, мм",
        "Усилие верхнего ЭМП, кН",
        "Усилие нижнего ЭМП, кН",
    ]

    plot_manager = PlotManager(
        model, SimpleNamespace(set_modal_progress=lambda _value: None)
    )
    loaded = plot_manager._load_data(list(model.dict_all_signals))
    assert len(loaded) == 6280
    assert set(loaded.columns) == set(model.dict_all_signals) | {"Время ГИТ, с"}
    assert loaded["Время ЭМП, с"].notna().all()
    assert loaded["Время ГИТ, с"].notna().sum() == 247


def test_plot_step_is_one_only_for_veik_dual_time_diagram(monkeypatch) -> None:
    class Table:
        def __init__(self, signals):
            self.signals = signals

        def rowCount(self):  # noqa: N802 - имитация метода QTableWidget
            return len(self.signals)

        def item(self, row, column):
            value = row + 1 if column == 0 else self.signals[row]
            return SimpleNamespace(text=lambda value=value: str(value))

    def make_ui(time_signal):
        return SimpleNamespace(
            gb_selected_signals=SimpleNamespace(qtable_axe=Table(["Signal"])),
            gb_x_axe=SimpleNamespace(qtable_axe=Table([time_signal])),
            start_modal_progress=lambda maximum: None,
            stop_modal_progress=lambda: None,
        )

    for dual_time, time_signal, expected_step in (
        (True, "Время ЭМП, с", 1),
        (False, "timestamp", 10),
    ):
        model = Model(
            filenames=["archive.csv"],
            has_veik_dual_time=dual_time,
        )
        manager = PlotManager(model, make_ui(time_signal))
        monkeypatch.setattr(
            manager,
            "_load_data",
            lambda signals: pd.DataFrame({signal: [1.0] for signal in signals}),
        )

        assert manager.prepare_plot_data()
        assert model.step == expected_step


def test_veik_voltage_loads_its_own_time_column() -> None:
    model = Model(filenames=[str(VEIK_DIAGRAM)], first_filename=str(VEIK_DIAGRAM))
    handler = FileHandler(model)
    assert handler.analyze_file(str(VEIK_DIAGRAM))
    assert SignalManager(model, SimpleNamespace()).load_all_signals()

    manager = PlotManager(
        model, SimpleNamespace(set_modal_progress=lambda _value: None)
    )
    loaded = manager._load_data(["Время ЭМП, с", "Напряжение заряда ГИТ, кВ"])

    assert "Время ГИТ, с" in loaded.columns
    assert "Время ГИТ, с" not in model.dict_all_signals
    assert loaded["Время ЭМП, с"].notna().all()
    assert loaded["Время ГИТ, с"].notna().sum() == 247


def test_plot_manager_loads_log_values_and_none_as_nan(tmp_path) -> None:
    archive = tmp_path / "2026-09-16 15-06-44.log"
    archive.write_text(
        "timestamp,Driver Current,Wiring Current\n"
        "8652,0.0471145,0.0472218\n"
        "8684,None,0.0472993\n",
        encoding="utf-8",
    )
    model = Model(
        encoding="utf-8",
        delimiter=",",
        decimal=".",
        filenames=[str(archive)],
        first_filename=str(archive),
        is_time=True,
        time_signal="timestamp",
    )
    ui = SimpleNamespace(set_modal_progress=lambda _value: None)
    manager = PlotManager(model, ui)

    result = manager._load_data(["timestamp", "Driver Current"])

    assert result["timestamp"].tolist() == [8652, 8684]
    assert result["Driver Current"].iloc[0] == 0.0471145
    assert pd.isna(result["Driver Current"].iloc[1])


def test_timestamp_counter_is_unwrapped_after_multiple_overflows() -> None:
    source = pd.Series([65518, 13, 65509, 5, 100])

    result = unwrap_timestamp_counter(source)

    assert result.tolist() == [65518, 65549, 131045, 131077, 131172]


def test_small_timestamp_decrease_is_not_treated_as_overflow() -> None:
    source = pd.Series([1000, 995, 1010])

    result = unwrap_timestamp_counter(source)

    assert result.tolist() == [1000, 995, 1010]


def test_plot_manager_unwraps_timestamp_in_log_file(tmp_path) -> None:
    archive = tmp_path / "overflow.log"
    archive.write_text(
        "timestamp,Driver Current\n65518,0.1\n13,0.2\n20,0.3\n",
        encoding="utf-8",
    )
    model = Model(
        encoding="utf-8",
        delimiter=",",
        decimal=".",
        filenames=[str(archive)],
        first_filename=str(archive),
        is_time=True,
        time_signal="timestamp",
    )
    manager = PlotManager(
        model, SimpleNamespace(set_modal_progress=lambda _value: None)
    )

    result = manager._load_data(["timestamp", "Driver Current"])

    assert result["timestamp"].tolist() == [65518, 65549, 65556]
