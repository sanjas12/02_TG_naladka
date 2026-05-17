import pandas as pd
import pytest

from model.basemodel import Model


@pytest.fixture
def sample_df():
    return pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})


@pytest.fixture
def filled_model(sample_df):
    model = Model()

    # Arrange: заполняем состояние
    model.encoding = "utf-8"
    model.delimiter = ";"
    model.decimal = ","
    model.first_filename = "file1.csv"
    model.filenames = ["file1.csv", "file2.csv"]
    model.selected_filter_file = "filter.json"

    model.is_kol_1_2 = True
    model.is_time = True
    model.is_ms = True
    model.ready_plot = True
    model.ready_to_analysis = True

    model.df = sample_df.copy()
    model.dict_all_signals = {"A": 1, "B": 2}
    model.dict_base_signals = {"A": 1}
    model.dict_secondary_signals = {"B": 2}
    model.time_signal = "time"
    model.step = 10

    return model


@pytest.mark.unit
def test_model_init_default_state_is_empty():
    # Arrange
    model = Model()

    # Assert
    assert model.df is None
    assert model.dict_all_signals == {}
    assert model.dict_base_signals == {}
    assert model.dict_secondary_signals == {}
    assert model.filenames == []
    assert model.ready_plot is False
    assert model.step is None


@pytest.mark.unit
def test_clear_state_clears_dataframe_and_dicts(filled_model):
    # Arrange
    model = filled_model

    # Act
    model.clear_state()

    # Assert
    assert model.df is None
    assert model.dict_all_signals == {}
    assert model.dict_base_signals == {}
    assert model.dict_secondary_signals == {}


@pytest.mark.unit
def test_clear_state_resets_ready_plot_and_step(filled_model):
    # Arrange
    model = filled_model

    # Act
    model.clear_state()

    # Assert
    assert model.ready_plot is False
    assert model.step is None


@pytest.mark.unit
def test_clear_state_does_not_reset_disabled_fields(filled_model):
    # Arrange
    model = filled_model

    # Act
    model.clear_state()

    # Assert (эти поля закомментированы в clear_state и не должны сбрасываться)
    assert model.encoding == "utf-8"
    assert model.delimiter == ";"
    assert model.decimal == ","
    assert model.first_filename == "file1.csv"
    assert model.filenames == ["file1.csv", "file2.csv"]
    assert model.selected_filter_file == "filter.json"

    assert model.is_kol_1_2 is True
    assert model.is_time is True
    assert model.is_ms is True
    assert model.ready_to_analysis is True


@pytest.mark.unit
def test_clear_state_keeps_time_signal_unchanged(filled_model):
    # Arrange
    model = filled_model

    # Act
    model.clear_state()

    # Assert
    assert model.time_signal == "time"
