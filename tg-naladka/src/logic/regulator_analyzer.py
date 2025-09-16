import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Union

import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QApplication
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from model.basemodel import Model
from config.config import *


class RegulatorAnalyzer:
    def __init__(
        self,
        time_: np.ndarray,
        real_position_a: np.ndarray,
        real_position_b: np.ndarray,
        aim_position: np.ndarray,
        files: List[str], 
        dt: float = 0.05,
    ) -> None:
        """
        Анализатор данных регулятора.

        :param real_position: массив реальных положений
        :param aim_position: массив целевых положений
        :param dt: шаг дискретизации по времени
        """
        self.time = time_
        self.real_position_a = real_position_a
        self.real_position_b = real_position_b
        self.aim_position = aim_position
        self.dt = dt
        self.jumps: Dict[int, Dict[str, Any]] = {}
        self.files = [os.path.basename(path) for path in files]
        self.count_jumps()
        self.evaluate_regulator_quality()

    def count_jumps(self, threshold: float = 9.0) -> Dict[int, Dict[str, Any]]:
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
        self.jumps.clear()
        prev_pos = float(self.aim_position[0])
        jump_count = 0
        interval = 300          # эквивалетно 3 cek после измененея задания   3/0.01 = 300

        for index, pos in enumerate(self.aim_position[1:], start=1):
            new_pos = float(pos)
            if abs(new_pos - prev_pos) > threshold:
                jump_count += 1
                self.jumps[jump_count] = {
                    "start_value": int(prev_pos),
                    "end_value": int(new_pos),
                    "time": self.time[index],
                    "regulator_a": list(self.real_position_a[index: index + interval]),
                    "regulator_b": list(self.real_position_b[index: index + interval]),
                }
                prev_pos = new_pos
        return self.jumps

    def evaluate_regulator_quality(self, time_constant: float = 0.7) -> None:
        """
        Оценивает качество переходного процесса по скачкам задания.

        :param time_constant: время, за которое регулятор должен достичь 63% изменения (по умолчанию 0.7 с)
        :self.jumps: обновляется с ключом "reg_ok"
        """
        dt = 0.01  # шаг дискретизации в секундах от ПЛК

        for jump_id, jump_info in self.jumps.items():
            start = jump_info["start_value"]
            end = jump_info["end_value"]
            delta = end - start
            expected_63 = start + 0.63 * delta
            reg_values_a = jump_info["regulator_a"]
            reg_values_b = jump_info["regulator_b"]
            check_idx = int(time_constant / dt)
            reached_value_a = reg_values_a[check_idx] if check_idx < len(reg_values_a) else reg_values_a[-1]
            reached_value_b = reg_values_b[check_idx] if check_idx < len(reg_values_b) else reg_values_b[-1]
            ok_a = (delta >= 0 and reached_value_a >= expected_63) or (delta < 0 and reached_value_a <= expected_63)
            ok_b = (delta >= 0 and reached_value_b >= expected_63) or (delta < 0 and reached_value_b <= expected_63)
            self.jumps[jump_id].update({
                "expected_63": expected_63,
                "reached_value_a": reached_value_a,
                "reached_value_b": reached_value_b,
                "reg_ok_a": ok_a,
                "reg_ok_b": ok_b,
            })

    def get_analysis_report(self) -> str:
        """Генерация текстового отчёта по анализу."""
        report_lines: list[str] = [f"Количество изменений заданий ГСМ: {len(self.jumps)}"]
        if self.jumps:
            report_lines.append("\nДетальная информация по каждому изменению задания:")
            for jump_id, info in self.jumps.items():
                start_val = info["start_value"]
                end_val = info["end_value"]
                time_idx = info["time"]
                reg_ok_a = "Удовл." if info["reg_ok_a"] else "Неудовл."
                reg_ok_b = "Удовл." if info["reg_ok_b"] else "Неудовл."
                expected_63 = info["expected_63"]
                reached_value_a = info["reached_value_a"]
                reached_value_b = info["reached_value_b"]
                report_lines.append(
                    f"Изменение задания № {jump_id}, мм: {start_val} → {end_val}, "
                    f"Время изменения задания = {time_idx}, "
                    f"Ожидаемое значение(63%) = {expected_63:0.3f} мм, "
                    f"Достигнутое значение ГСМ-А = {reached_value_a:0.3f} мм, "
                    f"Достигнутое значение ГСМ-Б = {reached_value_b:0.3f} мм, "
                    f"Качество регулятора ГСМ-А = {reg_ok_a} "
                    f"Качество регулятора ГСМ-Б = {reg_ok_b} "
                )
        return "\n".join(report_lines)

    def _register_font(self) -> str:
            """Регистрация шрифта с поддержкой Unicode. Возвращает имя шрифта."""
            for font_name, font_file in [
                ("ArialUnicode", "arial.ttf"),
                ("DejaVuSans", "DejaVuSans.ttf"),
            ]:
                try:
                    pdfmetrics.registerFont(TTFont(font_name, font_file))
                    return font_name
                except Exception:
                    continue
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

    def save_to_pdf(
        self,
        filename: Union[str, Path] = PDF_FILENAME,
        plot_filename: Union[str, Path] = PLOT_FILENAME,
    ) -> None:
        """
        Сохранение отчёта анализа в PDF файл.
        :param filename: имя выходного файла
        :param plot_filename: путь к графику для вставки (если None — не вставлять)
        """
        font_name = self._register_font()
        c = canvas.Canvas(str(filename), pagesize=letter)
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
        # y_position -= 10

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
            except Exception as e:
                print(f"Ошибка вставки графика: {e}")

        # Текст отчёта
        c.showPage()
        # page_width, page_height = letter
        report_lines = self.get_analysis_report().split("\n")
        y_position = self._draw_wrapped_lines(
            c,
            report_lines,
            font_name,
            12,
            50,
            page_height - 80,
            max_width=page_width - 100,
        )

        try:
            c.save()
            print(f"Отчёт сохранён в файл: {filename}")
        except OSError:
            print(f"Не удалось сохранить файл. Закройте {filename} и повторите попытку.")

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
    df = pd.DataFrame()
    reference_jump_values = np.array(
        [
            0, 10,
            20, 10, 30, 10, 60, 10, 100, 110, 100,
            120, 100, 150, 100, 200, 210, 200, 220, 200,
            250, 200, 300, 320, 300, 10, 0,
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
            delta = (dt / time_constant) * (aim_position_current - real_position_a[i - 1])
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
    return df


if __name__ == "__main__":
    model = Model(df=generator_signals())
    
    # app = QApplication(sys.argv)
    # graph = WindowGraph(
    #     data=model.df,
    #     base_signals=[AIM_GSM, CUR_GSM],
    #     secondary_signals=None,
    #     time_signals="Время",
    #     filename="test",
    #     enable_analys=True,
    # )
    # graph.show()

    analyzer = RegulatorAnalyzer(model.df[DEFAULT_TIME].to_numpy(),
                                model.df[GSM_A_CUR].to_numpy(),
                                model.df[GSM_B_CUR].to_numpy(),
                                model.df[ANALYS_AIM].to_numpy(),
                                files=["E:/User/Temp/ТГ41-2021-06-25_134810_14099.csv.gz",
                                        #    "E:/User/Temp/ТГ41-2021-06-25_134914_14099.csv.gz", 
                                        #    "E:/User/Temp/ТГ41-2021-06-25_134915_14099.csv.gz", 
                                        #    "E:/User/Temp/ТГ41-2021-06-25_134916_14099.csv.gz", 
                                           "E:/User/Temp/ТГ41-2021-06-25_134917_14099.csv.gz"], 
                                )
    analyzer.save_to_pdf()
    # print(analyzer.get_analysis_report())

    # sys.exit(app.exec())