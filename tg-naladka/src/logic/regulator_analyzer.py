import numpy as np
from typing import Tuple
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# Если проблема сохраняется, попробуйте явно указать путь к шрифту:
# pdfmetrics.registerFont(TTFont('ArialUnicode', 'C:/Windows/Fonts/arial.ttf'))


class RegulatorAnalyzer:
    def __init__(
        self, time_sim: np.ndarray, real_position: np.ndarray, aim_position: float
    ):
        """
        Анализатор данных регулятора

        :param time_sim: массив времени моделирования
        :param real_position: массив реальных положений
        :param aim_position: целевое положение
        """
        self.time_sim = time_sim
        self.real_position = real_position
        self.aim_position = aim_position
        self.dt = time_sim[1] - time_sim[0] if len(time_sim) > 1 else 0

    def count_jumps(self, threshold: float = 5.0) -> int:
        """
        Подсчет количества скачков задания

        :param threshold: порог изменения для определения скачка
        :return: количество скачков
        """
        jumps = 0
        prev_aim = self.real_position[0]

        for pos in self.real_position[1:]:
            if abs(pos - prev_aim) > threshold:
                jumps += 1
                prev_aim = pos
        return jumps

    def evaluate_regulator_quality(
        self, settling_threshold: float = 0.05, settling_time_factor: float = 5.0
    ) -> Tuple[float, float]:
        """
        Оценка качества регулятора

        :param settling_threshold: порог установления (в % от целевого значения)
        :param settling_time_factor: множитель для определения времени установления
        :return: (перерегулирование в %, время установления)
        """
        if len(self.real_position) == 0:
            return 0.0, 0.0

        max_value = np.max(self.real_position)
        target = self.aim_position
        overshoot = ((max_value - target) / target) * 100 if target != 0 else 0

        # Находим индекс, после которого значение остается в пределах порога
        threshold_value = target * (1 + settling_threshold)
        settling_index = 0
        for i, pos in enumerate(self.real_position):
            if abs(pos - target) <= abs(target * settling_threshold):
                settling_index = i
                break

        settling_time = settling_index * self.dt * settling_time_factor

        return overshoot, settling_time

    def get_analysis_report(self) -> str:
        """Генерация отчета по анализу"""
        jumps_count = self.count_jumps()
        overshoot, settling_time = self.evaluate_regulator_quality()

        report = f"""
        Анализ работы регулятора:
        --------------------------
        Количество скачков задания: {jumps_count}
        Перерегулирование: {overshoot:.2f}%
        Время установления: {settling_time:.2f} сек
        Качество регулятора: {'Хорошее' if overshoot < 10 and settling_time < 2 else 'Удовлетворительное' if overshoot < 20 else 'Плохое'}
        """
        return report

    def save_to_pdf(self, filename: str = "regulator_analysis.pdf"):
        """
        Сохранение отчета анализа в PDF файл с поддержкой Unicode
        
        :param filename: имя файла для сохранения
        """
        # Регистрируем Unicode-шрифт (например, Arial Unicode MS или другой с поддержкой кириллицы)
        try:
            pdfmetrics.registerFont(TTFont('ArialUnicode', 'arial.ttf'))
        except:
            # Если основной шрифт не найден, пробуем альтернативный
            try:
                pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
                font_name = 'DejaVuSans'
            except:
                # Если нет Unicode-шрифтов, используем стандартный (может не поддерживать кириллицу)
                font_name = 'Helvetica'
        else:
            font_name = 'ArialUnicode'

        jumps_count = self.count_jumps()
        overshoot, settling_time = self.evaluate_regulator_quality()
        
        # Создаем PDF документ
        c = canvas.Canvas(filename, pagesize=letter)
        width, height = letter
        
        # Заголовок
        c.setFont(font_name, 16)
        c.drawString(100, height - 100, "Анализ работы регулятора")
        c.setFont(font_name, 12)
        c.drawString(100, height - 130, f"Дата создания: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Основная информация
        y_position = height - 170
        c.drawString(100, y_position, f"Количество скачков задания: {jumps_count}")
        y_position -= 30
        c.drawString(100, y_position, f"Перерегулирование: {overshoot:.2f}%")
        y_position -= 30
        c.drawString(100, y_position, f"Время установления: {settling_time:.2f} сек")
        y_position -= 30
        
        # Оценка качества
        quality = 'Хорошее' if overshoot < 10 and settling_time < 2 else 'Удовлетворительное' if overshoot < 20 else 'Плохое'
        c.drawString(100, y_position, f"Качество регулятора: {quality}")
        
        c.save()
        print(f"Отчет сохранен в файл: {os.path.abspath(filename)}")


# Пример использования:
if __name__ == "__main__":
    # Пример данных (в реальности нужно получить от Simulator)
    time_sim = np.linspace(0, 10, 1000)
    real_position = np.sin(time_sim) * 10 + 50  # Имитация сигнала
    aim_position = 50

    analyzer = RegulatorAnalyzer(time_sim, real_position, aim_position)
    print(analyzer.get_analysis_report())
    analyzer.save_to_pdf()  # Сохраняем отчет в PDF
