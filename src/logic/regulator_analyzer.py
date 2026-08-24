import logging
import math
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.config import (  # noqa: E402
    ANALYS_AIM,
    DEFAULT_TIME,
    GSM_A_CUR,
    GSM_B_CUR,
    PDF_FILENAME,
)
from model.basemodel import Model  # noqa: E402

logger = logging.getLogger(__name__)

# Повышать только при изменении структуры или оформления PDF-отчёта.
PDF_REPORT_FORMAT_VERSION = "0.1"


class ReportCanvas(canvas.Canvas):
    """Canvas, автоматически добавляющий номер в правый нижний угол."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._page_number_drawn = False

    def _draw_page_number(self) -> None:
        if self._page_number_drawn:
            return
        page_width, _ = self._pagesize
        self.saveState()
        self.setFillColor(colors.HexColor("#555555"))
        self.setFont("Helvetica", 8)
        self.drawRightString(page_width - 24, 18, str(self.getPageNumber()))
        self.restoreState()
        self._page_number_drawn = True

    def showPage(self) -> None:  # noqa: N802
        self._draw_page_number()
        super().showPage()
        self._page_number_drawn = False

    def save(self) -> None:
        self._draw_page_number()
        super().save()


class RegulatorAnalyzer:
    def __init__(
        self,
        time_: np.ndarray,
        real_position_a: np.ndarray,
        real_position_b: np.ndarray,
        aim_position: np.ndarray,
        files: List[str],
        dt: float = 0.01,
        jump_threshold: float = 9.0,
        max_jump_threshold: float = 50.0,
        plot_file: Optional[str] = None,
    ) -> None:
        """
        Анализатор данных регулятора.

        :param real_position: массив реальных положений
        :param aim_position: массив целевых положений
        :param dt: шаг дискретизации по времени
        """
        logger.info(
            f"Инициализация RegulatorAnalyzer: точек={len(time_)}, файлов={len(files)}, dt={dt:.4f}"
        )
        self.time = np.asarray(time_)
        try:
            self.real_position_a = np.asarray(real_position_a, dtype=float)
            self.real_position_b = np.asarray(real_position_b, dtype=float)
            self.aim_position = np.asarray(aim_position, dtype=float)
        except (TypeError, ValueError) as exc:
            raise ValueError("Сигналы регулятора должны содержать числа") from exc

        self.dt = float(dt)
        self.jump_threshold = float(jump_threshold)
        self.max_jump_threshold = float(max_jump_threshold)
        self._validate_input()
        self.plot_file = plot_file
        self.jumps: Dict[int, Dict[str, Any]] = {}
        self.excluded_large_jumps: List[Dict[str, Any]] = []
        self.total_jump_count = 0
        self.files = [os.path.basename(path) for path in files]
        logger.debug(f"Файлы для анализа: {self.files}")
        self.count_jumps()
        self.evaluate_regulator_quality()

    def _validate_input(self) -> None:
        """Проверяет входные ряды до выполнения расчёта."""
        lengths = {
            len(self.time),
            len(self.real_position_a),
            len(self.real_position_b),
            len(self.aim_position),
        }
        if len(lengths) != 1:
            raise ValueError("Время, задание, ГСМ-А и ГСМ-Б имеют разную длину")
        if not self.aim_position.size:
            raise ValueError("Нет данных для анализа регулятора")
        if self.dt <= 0:
            raise ValueError("Шаг дискретизации должен быть больше нуля")
        if self.jump_threshold < 0:
            raise ValueError("Порог скачка не может быть отрицательным")
        if self.max_jump_threshold <= self.jump_threshold:
            raise ValueError(
                "Максимальный порог скачка должен быть больше минимального"
            )
        if not all(
            np.isfinite(values).all()
            for values in (
                self.real_position_a,
                self.real_position_b,
                self.aim_position,
            )
        ):
            raise ValueError(
                "Сигналы регулятора содержат пустые или бесконечные значения"
            )

    def count_jumps(
        self, threshold: Optional[float] = None
    ) -> Dict[int, Dict[str, Any]]:
        """
        Подсчёт количества скачков целевого задания с временными метками.

        :param threshold: порог изменения задания для определения скачка
        :return: словарь со скачками:
                 {
                   порядковый номер_скачка: {
                                "start_value": начальное значение,
                                "end_value": конечное задание,
                                "time": индекс во временном массиве, когда произошло изменение задания,
                                "regulator": значения регулятора в окрестности скачка + interval
                                 }
                 }
        """
        threshold = self.jump_threshold if threshold is None else float(threshold)
        if threshold < 0:
            raise ValueError("Порог скачка не может быть отрицательным")
        logger.debug(f"Поиск скачков задания, порог={threshold:.3f}")
        self.jumps.clear()
        self.excluded_large_jumps.clear()
        self.total_jump_count = 0
        prev_pos = float(self.aim_position[0])
        open_jump_id: Optional[int] = None
        last_change_index = 0
        interval = int(round(3.0 / self.dt))
        pre_interval = int(round(2.0 / self.dt))

        for index, pos in enumerate(self.aim_position[1:], start=1):
            new_pos = float(pos)
            if abs(new_pos - prev_pos) > threshold:
                if open_jump_id is not None:
                    previous_jump = self.jumps[open_jump_id]
                    previous_length = index - previous_jump["sample_index"]
                    previous_jump["regulator_a"] = previous_jump["regulator_a"][
                        :previous_length
                    ]
                    previous_jump["regulator_b"] = previous_jump["regulator_b"][
                        :previous_length
                    ]
                    previous_jump["time_values"] = previous_jump["time_values"][
                        :previous_length
                    ]
                    previous_plot_length = index - previous_jump["plot_start_index"]
                    for key in (
                        "plot_time",
                        "plot_aim",
                        "plot_regulator_a",
                        "plot_regulator_b",
                    ):
                        previous_jump[key] = previous_jump[key][:previous_plot_length]

                self.total_jump_count += 1
                jump_size = abs(new_pos - prev_pos)
                if jump_size > self.max_jump_threshold:
                    self.excluded_large_jumps.append(
                        {
                            "jump_id": self.total_jump_count,
                            "start_value": prev_pos,
                            "end_value": new_pos,
                            "jump_size": jump_size,
                            "time": self.time[index],
                        }
                    )
                    logger.info(
                        "Изменение задания №%d исключено: %.3f мм > %.3f мм",
                        self.total_jump_count,
                        jump_size,
                        self.max_jump_threshold,
                    )
                    open_jump_id = None
                    prev_pos = new_pos
                    last_change_index = index
                    continue

                plot_start = max(0, index - pre_interval, last_change_index)
                plot_end = index + interval
                self.jumps[self.total_jump_count] = {
                    "start_value": prev_pos,
                    "end_value": new_pos,
                    "sample_index": index,
                    "plot_start_index": plot_start,
                    "plot_jump_offset": index - plot_start,
                    "time": self.time[index],
                    "time_values": list(self.time[index : index + interval]),
                    "plot_time": list(self.time[plot_start:plot_end]),
                    "plot_aim": list(self.aim_position[plot_start:plot_end]),
                    "plot_regulator_a": list(self.real_position_a[plot_start:plot_end]),
                    "plot_regulator_b": list(self.real_position_b[plot_start:plot_end]),
                    "regulator_a": list(self.real_position_a[index : index + interval]),
                    "regulator_b": list(self.real_position_b[index : index + interval]),
                }
                open_jump_id = self.total_jump_count
                prev_pos = new_pos
                last_change_index = index

        logger.info(
            "Обнаружено изменений задания: %d; исключено крупных: %d; анализируется: %d",
            self.total_jump_count,
            len(self.excluded_large_jumps),
            len(self.jumps),
        )
        return self.jumps

    def evaluate_regulator_quality(self, time_constant: float = 0.7) -> None:
        """
        Оценивает качество переходного процесса по скачкам задания.

        :param time_constant: время, за которое регулятор должен достичь 63% изменения (по умолчанию 0.7 с)
        :self.jumps: обновляется с ключом "reg_ok"
        """
        logger.debug(
            f"Оценка качества регулятора, постоянная времени={time_constant:.2f} с"
        )
        ok_a_count = 0
        ok_b_count = 0

        for jump_id, jump_info in self.jumps.items():
            start = jump_info["start_value"]
            end = jump_info["end_value"]
            delta = end - start
            expected_63 = start + 0.63 * delta
            reg_values_a = jump_info["regulator_a"]
            reg_values_b = jump_info["regulator_b"]
            check_idx = int(round(time_constant / self.dt))
            if check_idx >= len(reg_values_a) or check_idx >= len(reg_values_b):
                self.jumps[jump_id].update(
                    {
                        "expected_63": expected_63,
                        "reached_value_a": None,
                        "reached_value_b": None,
                        "reg_ok_a": None,
                        "reg_ok_b": None,
                        "evaluation_error": (
                            f"Недостаточно данных после скачка: требуется {check_idx + 1} "
                            f"отсчётов ({time_constant:.2f} с)"
                        ),
                    }
                )
                logger.warning("Скачок №%d не оценён: недостаточно данных", jump_id)
                continue

            reached_value_a = reg_values_a[check_idx]
            reached_value_b = reg_values_b[check_idx]
            ok_a = bool(
                (delta >= 0 and reached_value_a >= expected_63)
                or (delta < 0 and reached_value_a <= expected_63)
            )
            ok_b = bool(
                (delta >= 0 and reached_value_b >= expected_63)
                or (delta < 0 and reached_value_b <= expected_63)
            )
            self.jumps[jump_id].update(
                {
                    "expected_63": expected_63,
                    "reached_value_a": reached_value_a,
                    "reached_value_b": reached_value_b,
                    "reg_ok_a": ok_a,
                    "reg_ok_b": ok_b,
                }
            )
            if ok_a:
                ok_a_count += 1
            if ok_b:
                ok_b_count += 1
            logger.debug(
                f"Скачок №{jump_id}: ожид.(63%)={expected_63:.3f}, "
                f"ГСМ-А={reached_value_a:.3f} ({'Удовл.' if ok_a else 'Неудовл.'}), "
                f"ГСМ-Б={reached_value_b:.3f} ({'Удовл.' if ok_b else 'Неудовл.'})"
            )

        if self.jumps:
            total = len(self.jumps)
            logger.info(
                f"Качество регулятора: ГСМ-А удовл. {ok_a_count}/{total}, ГСМ-Б удовл. {ok_b_count}/{total}"
            )

    def get_quality_summary(self) -> Dict[str, Dict[str, int]]:
        """Подсчитать результаты только по скачкам детального анализа."""
        summary = {
            "gsm_a": {"satisfactory": 0, "unsatisfactory": 0, "not_evaluated": 0},
            "gsm_b": {"satisfactory": 0, "unsatisfactory": 0, "not_evaluated": 0},
            "overall": {"satisfactory": 0, "unsatisfactory": 0, "not_evaluated": 0},
        }
        for info in self.jumps.values():
            for field_name, summary_key in (
                ("reg_ok_a", "gsm_a"),
                ("reg_ok_b", "gsm_b"),
            ):
                value = info.get(field_name)
                result_key = (
                    "not_evaluated"
                    if value is None
                    else "satisfactory"
                    if value
                    else "unsatisfactory"
                )
                summary[summary_key][result_key] += 1

            reg_ok_a = info.get("reg_ok_a")
            reg_ok_b = info.get("reg_ok_b")
            if reg_ok_a is None or reg_ok_b is None:
                overall_key = "not_evaluated"
            elif reg_ok_a and reg_ok_b:
                overall_key = "satisfactory"
            else:
                overall_key = "unsatisfactory"
            summary["overall"][overall_key] += 1
        return summary

    def _get_summary_lines(self) -> List[str]:
        quality = self.get_quality_summary()
        return [
            f"Количество изменений заданий ГСМ: {self.total_jump_count}",
            f"Из них больше {self.max_jump_threshold:g} мм: "
            f"{len(self.excluded_large_jumps)} — не учитываются в детальном анализе.",
            f"Детально проанализировано изменений: {len(self.jumps)}.",
            "ГСМ-А: удовлетворительно — {satisfactory}, неудовлетворительно — "
            "{unsatisfactory}, не оценено — {not_evaluated}.".format(
                **quality["gsm_a"]
            ),
            "ГСМ-Б: удовлетворительно — {satisfactory}, неудовлетворительно — "
            "{unsatisfactory}, не оценено — {not_evaluated}.".format(
                **quality["gsm_b"]
            ),
            "По обоим каналам: удовлетворительно — {satisfactory}, "
            "неудовлетворительно хотя бы по одному — {unsatisfactory}, "
            "не оценено — {not_evaluated}.".format(**quality["overall"]),
        ]

    def _get_report_overview_lines(self) -> List[str]:
        """Сформировать содержимое второй страницы PDF-отчёта."""
        return [
            f"Версия формата PDF-отчёта: {PDF_REPORT_FORMAT_VERSION}",
            "",
            *self._get_summary_lines(),
            "Подробные результаты и графики приведены далее: по одной странице "
            "на каждое учитываемое изменение задания.",
        ]

    def get_analysis_report(self) -> str:
        """Генерация текстового отчёта по анализу."""
        logger.debug(f"Генерация текстового отчёта, скачков={len(self.jumps)}")
        report_lines = self._get_summary_lines()
        if self.jumps:
            report_lines.append("\nДетальная информация по каждому изменению задания:")
            for jump_id, info in self.jumps.items():
                start_val = info["start_value"]
                end_val = info["end_value"]
                time_idx = info["time"]
                if info["reg_ok_a"] is None:
                    reg_ok_a = "Не оценено"
                    reg_ok_b = "Не оценено"
                else:
                    reg_ok_a = "Удовл." if info["reg_ok_a"] else "Неудовл."
                    reg_ok_b = "Удовл." if info["reg_ok_b"] else "Неудовл."
                expected_63 = info["expected_63"]
                reached_value_a = info["reached_value_a"]
                reached_value_b = info["reached_value_b"]
                reached_a_text = (
                    f"{reached_value_a:0.3f}"
                    if reached_value_a is not None
                    else "нет данных"
                )
                reached_b_text = (
                    f"{reached_value_b:0.3f}"
                    if reached_value_b is not None
                    else "нет данных"
                )
                report_lines.append(
                    f"Изменение задания № {jump_id}, мм: {start_val:g} → {end_val:g}, "
                    f"Время изменения задания = {time_idx}, "
                    f"Ожидаемое значение(63%) = {expected_63:0.3f} мм, "
                    f"Достигнутое значение ГСМ-А = {reached_a_text} мм, "
                    f"Достигнутое значение ГСМ-Б = {reached_b_text} мм, "
                    f"Качество регулятора ГСМ-А = {reg_ok_a}; "
                    f"Качество регулятора ГСМ-Б = {reg_ok_b}"
                )
        report = "\n".join(report_lines)
        logger.debug(f"Отчёт сформирован, строк={len(report_lines)}")
        return report

    @staticmethod
    def _quality_text(value: Optional[bool]) -> str:
        if value is None:
            return "Не оценено"
        return "Удовл." if value else "Неудовл."

    def _format_jump_details(self, jump_id: int, info: Dict[str, Any]) -> str:
        """Формирует единое описание скачка для текста и страницы с графиком."""
        reached_a = info["reached_value_a"]
        reached_b = info["reached_value_b"]
        reached_a_text = f"{reached_a:0.3f}" if reached_a is not None else "нет данных"
        reached_b_text = f"{reached_b:0.3f}" if reached_b is not None else "нет данных"
        return (
            f"Изменение задания № {jump_id}, мм: "
            f"{info['start_value']:g} → {info['end_value']:g}, "
            f"Время изменения задания = {info['time']}, "
            f"Ожидаемое значение (63%) = {info['expected_63']:0.3f} мм, "
            f"Достигнутое значение ГСМ-А = {reached_a_text} мм, "
            f"Достигнутое значение ГСМ-Б = {reached_b_text} мм, "
            f"Качество регулятора ГСМ-А = {self._quality_text(info['reg_ok_a'])}; "
            f"Качество регулятора ГСМ-Б = {self._quality_text(info['reg_ok_b'])}. "
            f"Порог обнаружения = {self.jump_threshold:g} мм."
        )

    def _register_font(self) -> str:
        """Регистрация шрифта с поддержкой Unicode. Возвращает имя шрифта."""
        for font_name, font_file in [
            ("ArialUnicode", "arial.ttf"),
            ("DejaVuSans", "DejaVuSans.ttf"),
        ]:
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_file))
                logger.debug(f"Зарегистрирован шрифт: {font_name} ({font_file})")
                return font_name
            except Exception as e:
                logger.warning(
                    f"Не удалось зарегистрировать шрифт {font_name} ({font_file}): {e}"
                )
        logger.warning("Используется резервный шрифт: Helvetica")
        return "Helvetica"

    def _draw_wrapped_lines(
        self,
        c: canvas.Canvas,
        text_lines: List[str],
        font_name: str,
        font_size: int,
        x: int,
        y: int,
        max_width: int,
        line_height: int = 18,
        bottom_margin: int = 50,
    ) -> int:
        """
        Рисует строки текста с переносами по ширине.
        Возвращает текущую координату Y после вывода.
        """
        c.setFont(font_name, font_size)
        page_width, page_height = letter
        for line in text_lines:
            words = line.split(" ")
            buffer = ""
            for word in words:
                test_line = f"{buffer} {word}".strip()
                if c.stringWidth(test_line, font_name, font_size) > max_width:
                    c.drawString(x, y, buffer)
                    y -= line_height
                    buffer = word
                else:
                    buffer = test_line
            if buffer:
                c.drawString(x, y, buffer)
                y -= line_height
            y -= 6  # дополнительный отступ между строками

            if y < bottom_margin:
                c.showPage()
                c.setFont(font_name, font_size)
                y = page_height - 50
        return y

    def _draw_jump_plot(
        self,
        c: canvas.Canvas,
        info: Dict[str, Any],
        font_name: str,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        """Рисует векторный график одного переходного процесса."""

        def parse_source_datetime(value: Any) -> Optional[datetime]:
            text = str(value)
            for time_format in ("%Y-%m-%d %H:%M:%S,%f", "%Y-%m-%d %H:%M:%S.%f"):
                try:
                    return datetime.strptime(text, time_format)
                except ValueError:
                    continue
            return None

        def split_source_time(value: Any) -> Tuple[str, str]:
            text = str(value)
            parts = text.split(" ", 1)
            if (
                len(parts) == 2
                and len(parts[0]) == 10
                and parts[0][4] == "-"
                and parts[0][7] == "-"
            ):
                return parts[0], parts[1]
            return "", text

        regulator_a = np.asarray(info["plot_regulator_a"], dtype=float)
        regulator_b = np.asarray(info["plot_regulator_b"], dtype=float)
        target = np.asarray(info["plot_aim"], dtype=float)
        source_time = info["plot_time"]
        point_count = min(
            len(regulator_a), len(regulator_b), len(target), len(source_time)
        )
        time_axis = (
            np.arange(point_count, dtype=float) - info["plot_jump_offset"]
        ) * self.dt

        all_values = np.concatenate(
            (
                regulator_a[:point_count],
                regulator_b[:point_count],
                target,
                np.asarray([info["expected_63"]]),
            )
        )
        raw_min = float(np.min(all_values))
        raw_max = float(np.max(all_values))
        assignment_min = min(info["start_value"], info["end_value"]) - 5.0
        assignment_max = max(info["start_value"], info["end_value"]) + 5.0
        signal_min = math.floor(raw_min / 5.0) * 5.0
        signal_max = math.ceil(raw_max / 5.0) * 5.0
        value_min = min(assignment_min, signal_min)
        value_max = max(assignment_max, signal_max)
        value_span = value_max - value_min
        y_tick_step = max(5.0, math.ceil((value_span / 7.0) / 5.0) * 5.0)
        time_min = min(float(time_axis[0]) if point_count else 0.0, 0.0)
        time_max = max(float(time_axis[-1]) if point_count else 0.0, 0.7, self.dt)
        time_span = time_max - time_min

        left = x + 45
        bottom = y + 55
        plot_width = width - 60
        plot_height = height - 90

        def map_x(value: float) -> float:
            return left + (value - time_min) / time_span * plot_width

        def map_y(value: float) -> float:
            return bottom + (value - value_min) / value_span * plot_height

        c.saveState()
        c.setFont(font_name, 8)
        c.setStrokeColor(colors.HexColor("#b0b0b0"))
        c.setLineWidth(0.4)
        c.setFont(font_name, 6.5)
        first_date, _ = split_source_time(source_time[0]) if point_count else ("", "")
        last_date, _ = split_source_time(source_time[-1]) if point_count else ("", "")
        x_tick_step = self._choose_time_tick_step(time_span)
        first_datetime = parse_source_datetime(source_time[0]) if point_count else None
        x_ticks: List[Tuple[float, str]] = []
        if first_datetime is not None:
            seconds_at_first_point = (
                first_datetime.hour * 3600
                + first_datetime.minute * 60
                + first_datetime.second
                + first_datetime.microsecond / 1_000_000.0
            )
            absolute_start = seconds_at_first_point + time_min - time_axis[0]
            first_tick_absolute = (
                math.ceil((absolute_start - 1e-9) / x_tick_step) * x_tick_step
            )
            tick_absolute = first_tick_absolute
            while (
                tick_absolute <= seconds_at_first_point + time_max - time_axis[0] + 1e-9
            ):
                tick_value = time_axis[0] + tick_absolute - seconds_at_first_point
                tick_datetime = first_datetime + timedelta(
                    seconds=tick_value - time_axis[0]
                )
                x_ticks.append((tick_value, tick_datetime.strftime("%H:%M:%S,%f")[:-3]))
                tick_absolute += x_tick_step
        else:
            first_tick = math.ceil((time_min - 1e-9) / x_tick_step) * x_tick_step
            tick_value = first_tick
            while tick_value <= time_max + 1e-9:
                source_index = min(
                    max(round((tick_value - time_axis[0]) / self.dt), 0),
                    point_count - 1,
                )
                _, source_label = split_source_time(source_time[source_index])
                x_ticks.append((tick_value, source_label))
                tick_value += x_tick_step

        for tick_value, source_label in x_ticks:
            tick_x = map_x(tick_value)
            c.line(tick_x, bottom, tick_x, bottom + plot_height)
            time_parts = source_label.rsplit(",", 1)
            main_time = time_parts[0]
            milliseconds = f",{time_parts[1]}" if len(time_parts) == 2 else ""
            if abs(tick_x - left) < 1.0:
                c.drawString(tick_x, bottom - 12, main_time)
                c.drawString(tick_x, bottom - 20, milliseconds)
            elif abs(tick_x - (left + plot_width)) < 1.0:
                c.drawRightString(tick_x, bottom - 12, main_time)
                c.drawRightString(tick_x, bottom - 20, milliseconds)
            else:
                c.drawCentredString(tick_x, bottom - 12, main_time)
                c.drawCentredString(tick_x, bottom - 20, milliseconds)

        c.setFont(font_name, 8)
        first_y_tick = math.ceil(value_min / y_tick_step) * y_tick_step
        y_tick_count = int(math.floor((value_max - first_y_tick) / y_tick_step)) + 1
        for tick in range(y_tick_count):
            tick_value = first_y_tick + tick * y_tick_step
            tick_y = map_y(tick_value)
            c.line(left, tick_y, left + plot_width, tick_y)
            c.drawRightString(left - 5, tick_y - 3, f"{tick_value:g}")

        c.setStrokeColor(colors.black)
        c.rect(left, bottom, plot_width, plot_height, stroke=1, fill=0)
        c.setFont(font_name, 8)
        c.drawCentredString(left + plot_width / 2, y + 20, "Время")
        if first_date:
            date_label = (
                f"Дата: {first_date}"
                if first_date == last_date
                else f"Дата: {first_date} - {last_date}"
            )
            c.drawCentredString(left + plot_width / 2, y + 7, date_label)
        c.saveState()
        c.translate(x + 10, bottom + plot_height / 2)
        c.rotate(90)
        c.drawCentredString(0, 0, "Положение, мм")
        c.restoreState()

        def draw_series(
            values: np.ndarray, color: colors.Color, line_width: float
        ) -> None:
            if not point_count:
                return
            path = c.beginPath()
            path.moveTo(map_x(float(time_axis[0])), map_y(float(values[0])))
            for time_value, signal_value in zip(time_axis[1:], values[1:]):
                path.lineTo(map_x(float(time_value)), map_y(float(signal_value)))
            c.setStrokeColor(color)
            c.setLineWidth(line_width)
            c.drawPath(path, stroke=1, fill=0)

        draw_series(target, colors.HexColor("#202020"), 1.3)
        draw_series(regulator_a[:point_count], colors.HexColor("#1f77b4"), 1.1)
        draw_series(regulator_b[:point_count], colors.HexColor("#ff7f0e"), 1.1)

        c.setStrokeColor(colors.HexColor("#d62728"))
        c.setDash(5, 3)
        c.line(
            left,
            map_y(info["expected_63"]),
            left + plot_width,
            map_y(info["expected_63"]),
        )
        c.setStrokeColor(colors.HexColor("#9467bd"))
        c.setDash(2, 2)
        c.line(map_x(0.7), bottom, map_x(0.7), bottom + plot_height)
        c.setDash()

        legend = [
            ("Задание", "#202020"),
            ("ГСМ-А", "#1f77b4"),
            ("ГСМ-Б", "#ff7f0e"),
            ("Уровень 63%", "#d62728"),
            ("0,7 с", "#9467bd"),
        ]
        legend_x = left
        legend_y = y + height - 12
        for label, color in legend:
            c.setStrokeColor(colors.HexColor(color))
            c.setLineWidth(1.5)
            c.line(legend_x, legend_y, legend_x + 14, legend_y)
            c.setFillColor(colors.black)
            c.drawString(legend_x + 18, legend_y - 3, label)
            legend_x += 85 if label != "Уровень 63%" else 115
        c.restoreState()

    @staticmethod
    def _choose_time_tick_step(time_span: float) -> float:
        """Выбрать круглый постоянный шаг сетки, сохраняя около 10 делений."""
        nice_steps = (
            0.01,
            0.02,
            0.05,
            0.1,
            0.2,
            0.5,
            1.0,
            2.0,
            5.0,
            10.0,
            20.0,
            30.0,
            60.0,
        )
        minimum_step = max(time_span, 0.0) / 12.0
        for step in nice_steps:
            if step >= minimum_step - 1e-12:
                return step
        return math.ceil(minimum_step / 60.0) * 60.0

    def save_to_pdf(
        self,
        plot_filename: Optional[str] = None,
        filename: Union[str, Path] = PDF_FILENAME,
    ) -> None:
        """
        Сохранение отчёта анализа в PDF файл.
        :param filename: имя выходного файла PDF
        :param plot_filename: путь к графику для вставки (если None — не вставлять)
        """
        if plot_filename is None:
            plot_filename = self.plot_file

        logger.info(f"Сохранение PDF-отчёта: {filename}")
        font_name = self._register_font()
        c = ReportCanvas(str(filename), pagesize=letter)
        page_width, page_height = letter

        # Заголовок
        c.setFont(font_name, 16)
        c.drawString(50, page_height - 50, "Анализ работы регулятора ГСМ")

        # Дата отчета
        c.setFont(font_name, 12)
        c.drawString(
            50,
            page_height - 80,
            f"Дата создания отчета: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        )

        # Исходные данные
        c.drawString(50, page_height - 110, "Исходные данные:")
        y_position = page_height - 130
        for i, file_path in enumerate(self.files, start=1):
            y_position = self._draw_wrapped_lines(
                c,
                [f"{i}. {Path(file_path).name}"],
                font_name,
                12,
                70,
                y_position,
                max_width=page_width - 100,
            )

        # Вставка графика
        if plot_filename:
            try:
                img = ImageReader(str(plot_filename))
                img_width, img_height = img.getSize()
                aspect = img_height / img_width
                display_width = page_width - 100
                display_height = display_width * aspect

                if y_position - display_height < 50:
                    c.showPage()
                    y_position = page_height - 50

                c.drawImage(
                    img,
                    50,
                    y_position - display_height,
                    width=display_width,
                    height=display_height,
                )
                logger.debug(f"График вставлен из файла: {plot_filename}")
            except Exception as e:
                logger.warning(f"Ошибка вставки графика '{plot_filename}': {e}")

        # Текст отчёта
        c.showPage()
        report_lines = self._get_report_overview_lines()
        self._draw_wrapped_lines(
            c,
            report_lines,
            font_name,
            12,
            50,
            page_height - 80,
            max_width=page_width - 100,
        )

        # Отдельная страница с графиком для каждого найденного скачка.
        for jump_id, info in self.jumps.items():
            c.showPage()
            page_width, page_height = landscape(letter)
            c.setPageSize((page_width, page_height))
            details_bottom = self._draw_wrapped_lines(
                c,
                [self._format_jump_details(jump_id, info)],
                font_name,
                11,
                50,
                page_height - 50,
                max_width=page_width - 100,
                line_height=15,
            )

            plot_height = min(445, details_bottom - 75)
            self._draw_jump_plot(
                c,
                info,
                font_name,
                35,
                details_bottom - plot_height - 20,
                page_width - 70,
                plot_height,
            )

        try:
            c.save()
            logger.info(f"PDF-отчёт успешно сохранён: {filename}")
        except OSError as e:
            logger.error(
                f"Не удалось сохранить PDF '{filename}': {e}. Возможно, файл открыт."
            )
            raise

    def print_jumps(self) -> None:
        """Печать информации по каждому скачку."""
        for k, v in self.jumps.items():
            print(f"{k}: {v}")


def generator_signals(
    count_n: int = 50,
    dt: float = 0.01,
    noise_percent: float = 0.25,
    time_constant: float = 0.1,
) -> pd.DataFrame:
    """
    Генерация сигналов для анализа работы регулятора.

    :param count_n: количество точек
    :param dt: шаг дискретизации
    :param noise_percent: уровень шума (% от макс. значения задания)
    :param time_constant: постоянная времени
    :return: DataFrame с сигналами
    """
    logger.debug(
        f"Генерация сигналов: count_n={count_n}, dt={dt:.3f}, noise={noise_percent:.2f}%, tau={time_constant:.3f}"
    )
    df = pd.DataFrame()
    reference_jump_values = np.array(
        [
            0,
            10,
            20,
            10,
            30,
            10,
            60,
            10,
            100,
            110,
            100,
            120,
            100,
            150,
            100,
            200,
            210,
            200,
            220,
            200,
            250,
            200,
            300,
            320,
            300,
            10,
            0,
        ]
    )
    jump_times = np.linspace(0, count_n, len(reference_jump_values), endpoint=False)
    noise_std = (noise_percent / 100) * np.max(reference_jump_values)
    time_sim = np.arange(0, count_n, dt)
    df[DEFAULT_TIME] = time_sim
    aim_position = np.zeros_like(time_sim)
    real_position_a = np.zeros_like(time_sim)
    real_position_b = np.zeros_like(time_sim)
    delta_np = np.zeros_like(time_sim)
    aim_position_current = 0.0
    ref_idx = 0
    for i, t in enumerate(time_sim):
        if ref_idx < len(jump_times) and t >= jump_times[ref_idx]:
            aim_position_current = float(reference_jump_values[ref_idx])
            ref_idx += 1
        aim_position[i] = aim_position_current
        if i > 0:
            delta = (dt / time_constant) * (
                aim_position_current - real_position_a[i - 1]
            )
            real_position_a[i] = real_position_a[i - 1] + delta
            real_position_b[i] = real_position_b[i - 1] + delta
            delta_np[i] = delta
        real_position_a[i] += np.random.normal(0, noise_std)
        real_position_b[i] += np.random.normal(0, noise_std)
    df[ANALYS_AIM] = aim_position
    df[GSM_A_CUR] = real_position_a
    df[GSM_B_CUR] = real_position_b
    df["delta"] = delta_np
    df.to_csv("out.csv", encoding="UTF-8", sep=";", float_format="%.3f", index=False)
    logger.debug(f"Сигналы сгенерированы, точек={len(time_sim)}")
    return df


if __name__ == "__main__":
    model = Model(df=generator_signals())

    analyzer = RegulatorAnalyzer(
        model.df[DEFAULT_TIME].to_numpy(),
        model.df[GSM_A_CUR].to_numpy(),
        model.df[GSM_B_CUR].to_numpy(),
        model.df[ANALYS_AIM].to_numpy(),
        files=[
            "E:/User/Temp/ТГ41-2021-06-25_134810_14099.csv.gz",
            "E:/User/Temp/ТГ41-2021-06-25_134917_14099.csv.gz",
        ],
    )
    analyzer.save_to_pdf()
