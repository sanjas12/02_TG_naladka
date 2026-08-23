import numpy as np
import pytest

from logic.regulator_analyzer import RegulatorAnalyzer


def make_analyzer(
    aim,
    real_a,
    real_b=None,
    *,
    threshold=9.0,
):
    aim_array = np.asarray(aim, dtype=float)
    real_a_array = np.asarray(real_a, dtype=float)
    real_b_array = real_a_array.copy() if real_b is None else np.asarray(real_b)
    time = np.arange(len(aim_array)) * 0.01
    return RegulatorAnalyzer(
        time,
        real_a_array,
        real_b_array,
        aim_array,
        files=["sample.csv.gz"],
        dt=0.01,
        jump_threshold=threshold,
    )


@pytest.mark.unit
def test_increasing_jump_is_evaluated_after_point_seven_seconds():
    aim = np.zeros(150)
    aim[10:] = 100.0
    real = np.zeros(150)
    real[80:] = 63.0

    analyzer = make_analyzer(aim, real)

    jump = analyzer.jumps[1]
    assert jump["expected_63"] == pytest.approx(63.0)
    assert jump["reached_value_a"] == pytest.approx(63.0)
    assert jump["reg_ok_a"] is True


@pytest.mark.unit
def test_decreasing_jump_uses_lower_comparison():
    aim = np.full(150, 100.0)
    aim[10:] = 0.0
    real = np.full(150, 100.0)
    real[80:] = 37.0

    analyzer = make_analyzer(aim, real)

    assert analyzer.jumps[1]["expected_63"] == pytest.approx(37.0)
    assert analyzer.jumps[1]["reg_ok_a"] is True


@pytest.mark.unit
def test_operator_threshold_controls_jump_detection():
    aim = np.zeros(100)
    aim[10:] = 10.0
    real = np.zeros(100)

    assert len(make_analyzer(aim, real, threshold=9.0).jumps) == 1
    assert len(make_analyzer(aim, real, threshold=10.0).jumps) == 0


@pytest.mark.unit
def test_fractional_setpoints_are_not_truncated():
    aim = np.full(100, 10.9)
    aim[10:] = 20.9
    real = np.full(100, 17.2)

    jump = make_analyzer(aim, real).jumps[1]

    assert jump["start_value"] == pytest.approx(10.9)
    assert jump["end_value"] == pytest.approx(20.9)
    assert jump["expected_63"] == pytest.approx(17.2)


@pytest.mark.unit
def test_short_tail_is_reported_as_not_evaluated():
    aim = np.zeros(30)
    aim[20:] = 100.0
    real = np.zeros(30)

    jump = make_analyzer(aim, real).jumps[1]

    assert jump["reg_ok_a"] is None
    assert jump["reached_value_a"] is None
    assert "Недостаточно данных" in jump["evaluation_error"]


@pytest.mark.unit
def test_jump_plot_contains_two_seconds_before_jump():
    aim = np.zeros(600)
    aim[250:] = 100.0
    real = np.zeros(600)

    jump = make_analyzer(aim, real).jumps[1]

    assert jump["plot_jump_offset"] == 200
    assert jump["plot_time"][0] == pytest.approx(0.5)
    assert jump["time"] == pytest.approx(2.5)
    assert jump["plot_aim"][199] == pytest.approx(0.0)
    assert jump["plot_aim"][200] == pytest.approx(100.0)


@pytest.mark.unit
def test_empty_input_is_rejected():
    with pytest.raises(ValueError, match="Нет данных"):
        make_analyzer([], [])


@pytest.mark.unit
def test_arrays_with_different_lengths_are_rejected():
    with pytest.raises(ValueError, match="разную длину"):
        RegulatorAnalyzer(
            np.arange(3),
            np.arange(2),
            np.arange(3),
            np.arange(3),
            files=[],
        )


@pytest.mark.unit
def test_nan_is_rejected():
    with pytest.raises(ValueError, match="пустые или бесконечные"):
        make_analyzer([0.0, 10.0], [0.0, np.nan])
