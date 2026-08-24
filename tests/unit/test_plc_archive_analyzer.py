from datetime import datetime, timedelta
from pathlib import Path

import pytest

from logic.plc_archive_analyzer import (
    PlkEvent,
    compare_events,
    extract_numeric_signal,
    load_plk_archive,
)


def _event(offset_ms: int, message: str = "Событие", value: str = "Вкл") -> PlkEvent:
    return PlkEvent(
        datetime(2026, 8, 21, 10) + timedelta(milliseconds=offset_ms),
        message,
        value,
        Path("archive.csv"),
        2,
    )


def test_load_cp1251_archive(tmp_path):
    archive = tmp_path / "archive.csv"
    archive.write_bytes(
        (
            "Дата/Время;Сообщение;Значение\n2026-08-21 10:00:00,120;Режим работы;Пуск\n"
        ).encode("cp1251")
    )

    events = load_plk_archive(archive)

    assert len(events) == 1
    assert events[0].timestamp.microsecond == 120000
    assert events[0].key == ("Режим работы", "Пуск")


def test_compare_events_uses_message_value_and_tolerance():
    channel_1 = [_event(0), _event(500, value="Выкл")]
    channel_2 = [_event(30), _event(510, value="Другое")]

    result = compare_events(channel_1, channel_2, tolerance_ms=100)

    assert len(result.pairs) == 1
    assert result.pairs[0].delta_ms == 30
    assert result.only_channel_1 == [channel_1[1]]
    assert result.only_channel_2 == [channel_2[1]]


def test_compare_events_does_not_reuse_duplicate():
    channel_1 = [_event(0), _event(20)]
    channel_2 = [_event(10)]

    result = compare_events(channel_1, channel_2, tolerance_ms=100)

    assert len(result.pairs) == 1
    assert len(result.only_channel_1) == 1
    assert not result.only_channel_2


def test_compare_events_maximizes_duplicate_pairs():
    channel_1 = [_event(0), _event(100)]
    channel_2 = [_event(-90), _event(10)]

    result = compare_events(channel_1, channel_2, tolerance_ms=100)

    assert len(result.pairs) == 2
    assert not result.only_channel_1
    assert not result.only_channel_2


def test_extract_numeric_signal_separates_and_converts_values():
    signal_name = "Код ошибки по приоритету (младшая часть)"
    signal_event = _event(0, message=signal_name, value="32768")
    ordinary_event = _event(10)

    points, remaining = extract_numeric_signal(
        [signal_event, ordinary_event], signal_name
    )

    assert len(points) == 1
    assert points[0].value == 32768
    assert points[0].event is signal_event
    assert remaining == [ordinary_event]


def test_extract_numeric_signal_rejects_non_numeric_value():
    signal_name = "Код ошибки по приоритету (младшая часть)"

    with pytest.raises(ValueError, match="Нечисловое значение"):
        extract_numeric_signal([_event(0, signal_name, "ошибка")], signal_name)
