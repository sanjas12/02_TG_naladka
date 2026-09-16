from types import SimpleNamespace

import pandas as pd

from logic.logic import FileHandler, PlotManager, SignalManager
from model.basemodel import Model


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
