from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


@dataclass(frozen=True)
class PlkEvent:
    timestamp: datetime
    message: str
    value: str
    source: Path
    row_number: int

    @property
    def key(self) -> Tuple[str, str]:
        return self.message.strip(), self.value.strip()


@dataclass(frozen=True)
class EventPair:
    channel_1: PlkEvent
    channel_2: PlkEvent

    @property
    def delta_ms(self) -> float:
        return (
            self.channel_2.timestamp - self.channel_1.timestamp
        ).total_seconds() * 1000


@dataclass(frozen=True)
class ComparisonResult:
    pairs: List[EventPair]
    only_channel_1: List[PlkEvent]
    only_channel_2: List[PlkEvent]


@dataclass(frozen=True)
class NumericSignalPoint:
    timestamp: datetime
    value: float
    event: PlkEvent


@dataclass(frozen=True)
class BinarySignalPoint:
    timestamp: datetime
    active: bool
    event: PlkEvent


def _read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "cp1251"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Не удалось определить кодировку файла: {path}")


def load_plk_archive(path: Path) -> List[PlkEvent]:
    """Читает архив PLC с колонками времени, сообщения и значения."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Файл архива не найден: {path}")

    rows = csv.reader(_read_text(path).splitlines(), delimiter=";")
    header = next(rows, None)
    expected_header = ["Дата/Время", "Сообщение", "Значение"]
    if not header or [item.strip() for item in header[:3]] != expected_header:
        raise ValueError(
            f"Неверный формат {path.name}: ожидаются колонки "
            "«Дата/Время; Сообщение; Значение»"
        )

    events: List[PlkEvent] = []
    for row_number, row in enumerate(rows, start=2):
        if not row or not any(item.strip() for item in row):
            continue
        if len(row) < 3:
            raise ValueError(f"Неверная строка {row_number} в {path.name}")
        try:
            timestamp = datetime.strptime(row[0].strip(), "%Y-%m-%d %H:%M:%S,%f")
        except ValueError as error:
            raise ValueError(
                f"Неверное время в строке {row_number} файла {path.name}: {row[0]}"
            ) from error
        events.append(
            PlkEvent(timestamp, row[1].strip(), row[2].strip(), path, row_number)
        )
    return sorted(events, key=lambda event: event.timestamp)


def extract_numeric_signal(
    events: Sequence[PlkEvent], message: str
) -> Tuple[List[NumericSignalPoint], List[PlkEvent]]:
    """Извлекает числовой сигнал, не оставляя его в списке обычных событий."""
    points: List[NumericSignalPoint] = []
    remaining_events: List[PlkEvent] = []
    for event in events:
        if event.message != message:
            remaining_events.append(event)
            continue
        try:
            value = float(event.value.replace(",", "."))
        except ValueError as error:
            raise ValueError(
                f"Нечисловое значение сигнала «{message}» в строке "
                f"{event.row_number} файла {event.source.name}: {event.value}"
            ) from error
        points.append(NumericSignalPoint(event.timestamp, value, event))
    return points, remaining_events


def extract_binary_signal(
    events: Sequence[PlkEvent], message: str
) -> Tuple[List[BinarySignalPoint], List[PlkEvent]]:
    """Извлекает дискретный сигнал с активным и пассивным состояниями."""
    active_values = {"1", "акт", "активный"}
    passive_values = {"0", "пас", "пассивный"}
    points: List[BinarySignalPoint] = []
    remaining_events: List[PlkEvent] = []

    for event in events:
        if event.message != message:
            remaining_events.append(event)
            continue

        normalized_value = event.value.strip().casefold()
        if normalized_value in active_values:
            active = True
        elif normalized_value in passive_values:
            active = False
        else:
            raise ValueError(
                f"Неизвестное состояние сигнала «{message}» в строке "
                f"{event.row_number} файла {event.source.name}: {event.value}"
            )
        points.append(BinarySignalPoint(event.timestamp, active, event))

    return points, remaining_events


def compare_events(
    channel_1: Sequence[PlkEvent],
    channel_2: Sequence[PlkEvent],
    tolerance_ms: int = 100,
) -> ComparisonResult:
    """Сопоставляет одинаковые сообщения и значения в заданном окне времени."""
    if tolerance_ms < 0:
        raise ValueError("Допуск времени не может быть отрицательным")

    grouped_1: Dict[Tuple[str, str], List[PlkEvent]] = {}
    grouped_2: Dict[Tuple[str, str], List[PlkEvent]] = {}
    for event in channel_1:
        grouped_1.setdefault(event.key, []).append(event)
    for event in channel_2:
        grouped_2.setdefault(event.key, []).append(event)

    pairs: List[EventPair] = []
    only_channel_1: List[PlkEvent] = []
    only_channel_2: List[PlkEvent] = []
    tolerance_seconds = tolerance_ms / 1000

    for key in grouped_1.keys() | grouped_2.keys():
        events_1 = sorted(grouped_1.get(key, []), key=lambda event: event.timestamp)
        events_2 = sorted(grouped_2.get(key, []), key=lambda event: event.timestamp)
        index_1 = index_2 = 0
        while index_1 < len(events_1) and index_2 < len(events_2):
            event_1 = events_1[index_1]
            event_2 = events_2[index_2]
            delta = (event_2.timestamp - event_1.timestamp).total_seconds()
            if delta < -tolerance_seconds:
                only_channel_2.append(event_2)
                index_2 += 1
            elif delta > tolerance_seconds:
                only_channel_1.append(event_1)
                index_1 += 1
            else:
                pairs.append(EventPair(event_1, event_2))
                index_1 += 1
                index_2 += 1
        only_channel_1.extend(events_1[index_1:])
        only_channel_2.extend(events_2[index_2:])

    return ComparisonResult(
        sorted(pairs, key=lambda pair: pair.channel_1.timestamp),
        sorted(only_channel_1, key=lambda event: event.timestamp),
        sorted(only_channel_2, key=lambda event: event.timestamp),
    )
