import numpy as np
import pytest

from logic.regulator_analyzer import PDF_REPORT_FORMAT_VERSION, RegulatorAnalyzer


def make_analyzer(
    aim,
    real_a,
    real_b=None,
    *,
    threshold=9.0,
    max_threshold=50.0,
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
        max_jump_threshold=max_threshold,
    )


@pytest.mark.unit
def test_increasing_jump_is_evaluated_after_point_seven_seconds():
    aim = np.zeros(150)
    aim[10:] = 10.0
    real = np.zeros(150)
    real[80:] = 6.3

    analyzer = make_analyzer(aim, real)

    jump = analyzer.jumps[1]
    assert jump["expected_63"] == pytest.approx(6.3)
    assert jump["reached_value_a"] == pytest.approx(6.3)
    assert jump["reg_ok_a"] is True


@pytest.mark.unit
def test_decreasing_jump_uses_lower_comparison():
    aim = np.full(150, 50.0)
    aim[10:] = 0.0
    real = np.full(150, 50.0)
    real[80:] = 18.5

    analyzer = make_analyzer(aim, real)

    assert analyzer.jumps[1]["expected_63"] == pytest.approx(18.5)
    assert analyzer.jumps[1]["reg_ok_a"] is True


@pytest.mark.unit
def test_operator_threshold_controls_jump_detection():
    aim = np.zeros(100)
    aim[10:] = 10.0
    real = np.zeros(100)

    assert len(make_analyzer(aim, real, threshold=9.0).jumps) == 1
    assert len(make_analyzer(aim, real, threshold=10.0).jumps) == 0


@pytest.mark.unit
def test_jump_larger_than_maximum_is_counted_but_not_analyzed():
    aim = np.zeros(500)
    aim[10:] = 10.0
    aim[150:] = 80.0
    aim[300:] = 90.0
    real = aim.copy()

    analyzer = make_analyzer(aim, real, max_threshold=50.0)

    assert analyzer.total_jump_count == 3
    assert list(analyzer.jumps) == [1, 3]
    assert len(analyzer.excluded_large_jumps) == 1
    assert analyzer.excluded_large_jumps[0]["jump_id"] == 2
    assert analyzer.excluded_large_jumps[0]["jump_size"] == pytest.approx(70.0)


@pytest.mark.unit
def test_jump_equal_to_maximum_is_analyzed():
    aim = np.zeros(150)
    aim[10:] = 50.0
    real = aim.copy()

    analyzer = make_analyzer(aim, real, max_threshold=50.0)

    assert analyzer.total_jump_count == 1
    assert len(analyzer.jumps) == 1
    assert analyzer.excluded_large_jumps == []


@pytest.mark.unit
def test_quality_summary_counts_only_analyzed_jumps():
    aim = np.zeros(500)
    aim[10:] = 10.0
    aim[150:] = 20.0
    aim[300:] = 80.0
    aim[430:] = 90.0
    analyzer = make_analyzer(aim, aim.copy(), max_threshold=50.0)

    analyzed = list(analyzer.jumps.values())
    analyzed[0].update(reg_ok_a=True, reg_ok_b=True)
    analyzed[1].update(reg_ok_a=True, reg_ok_b=False)
    analyzed[2].update(reg_ok_a=None, reg_ok_b=None)

    assert analyzer.total_jump_count == 4
    assert len(analyzer.excluded_large_jumps) == 1
    assert analyzer.get_quality_summary() == {
        "gsm_a": {"satisfactory": 2, "unsatisfactory": 0, "not_evaluated": 1},
        "gsm_b": {"satisfactory": 1, "unsatisfactory": 1, "not_evaluated": 1},
        "overall": {"satisfactory": 1, "unsatisfactory": 1, "not_evaluated": 1},
    }


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
    aim[20:] = 10.0
    real = np.zeros(30)

    jump = make_analyzer(aim, real).jumps[1]

    assert jump["reg_ok_a"] is None
    assert jump["reached_value_a"] is None
    assert "Недостаточно данных" in jump["evaluation_error"]


@pytest.mark.unit
def test_jump_plot_contains_two_seconds_before_jump():
    aim = np.zeros(600)
    aim[250:] = 10.0
    real = np.zeros(600)

    jump = make_analyzer(aim, real).jumps[1]

    assert jump["plot_jump_offset"] == 200
    assert jump["plot_time"][0] == pytest.approx(0.5)
    assert jump["time"] == pytest.approx(2.5)
    assert jump["plot_aim"][199] == pytest.approx(0.0)
    assert jump["plot_aim"][200] == pytest.approx(10.0)


@pytest.mark.unit
def test_pdf_time_grid_uses_round_constant_step():
    assert RegulatorAnalyzer._choose_time_tick_step(0.95) == pytest.approx(0.1)
    assert RegulatorAnalyzer._choose_time_tick_step(5.65) == pytest.approx(0.5)
    assert RegulatorAnalyzer._choose_time_tick_step(20.0) == pytest.approx(2.0)


@pytest.mark.unit
def test_pdf_overview_contains_independent_format_version():
    analyzer = make_analyzer(np.zeros(10), np.zeros(10))

    assert PDF_REPORT_FORMAT_VERSION == "0.1"
    assert analyzer._get_report_overview_lines()[0] == (
        "Версия формата PDF-отчёта: 0.1"
    )


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
