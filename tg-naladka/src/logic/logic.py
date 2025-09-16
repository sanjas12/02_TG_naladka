import logging
import os
import gzip
from pathlib import Path
import sys
import chardet
import pandas as pd
from typing import List, Dict, Optional, Union
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config.config as cfg
from model.basemodel import Model
from ui.MainWindowUI import MainWindowUI, MyGroupBox
from ui.graph_matplot import WindowGraph


class FileHandler:
    """Обработчик работы с файлами данных"""

    def __init__(self, model: Model):
        self.model = model

    def open_files(self, parent_ui) -> bool:
        """Открывает диалог выбора файлов и сохраняет выбранные файлы в модель"""
        file_filters = ["GZ Files (*.gz)", "CSV Files (*.csv)", "Text Files (*.txt)"]

        filenames, selected_filter = QFileDialog.getOpenFileNames(
            parent_ui, caption="Выбор данных:", filter=";;".join(file_filters)
        )

        if not filenames:
            return False

        self.model.filenames = filenames
        self.model.first_filename = filenames[0]
        self.model.selected_filter_file = selected_filter
        return True

    def analyze_file(self, filepath: str) -> bool:
        """Анализирует параметры файла (кодировка, разделители и т.д.)"""
        try:
            if not os.path.isfile(filepath):
                raise FileNotFoundError(f"Файл не найден: {filepath}")

            # Определяем кодировку и параметры файла
            with self._open_file(filepath) as f:
                sample = f.read(20000)
                f.seek(0)
                second_row = f.readlines()[1]

            self._detect_file_params(sample, second_row)
            return True

        except Exception as e:
            logging.error(f"Ошибка анализа файла: {e}", exc_info=True)
            return False

    def _open_file(self, filepath: str):
        """Открывает файл с учетом сжатия"""
        return (
            gzip.open(filepath, "rb")
            if filepath.endswith(".gz")
            else open(filepath, "rb")
        )

    def _detect_file_params(self, sample: bytes, second_row: bytes) -> None:
        """Определяет параметры файла из образца данных"""
        self.model.encoding = chardet.detect(sample).get("encoding")

        if not self.model.encoding:
            raise ValueError("Не удалось определить кодировку файла")

        sample_str = sample[:200].decode(self.model.encoding, errors="ignore")
        second_row_str = second_row.decode(self.model.encoding)

        self.model.is_kol_1_2 = sample_str.startswith("Count=")
        self.model.delimiter = (
            ";" if sample_str.count(";") > sample_str.count("\t") else "\t"
        )
        self.model.decimal = (
            "." if second_row_str.count(".") > second_row_str.count(",") else ","
        )

    def get_file_params(self) -> Dict[str, Union[str, bool, List[str], None]]:
        """Возвращает параметры текущего файла для использования в других классах"""
        return {
            "encoding": self.model.encoding,
            "delimiter": self.model.delimiter,
            "decimal": self.model.decimal,
            "is_kol_1_2": self.model.is_kol_1_2,
            "first_filename": self.model.first_filename,
            "filenames": self.model.filenames,
            "selected_filter": self.model.selected_filter_file,
        }


class SignalManager:
    """Управление сигналами и их отображением в UI"""

    def __init__(self, model: Model, ui: MainWindowUI):
        self.model = model
        self.ui = ui

    def load_all_signals(self) -> bool:
        """Загружает все сигналы из первого файла"""
        try:
            if not self.model.encoding or not self.model.filenames:
                return False

            df_headers = self._read_file_headers()
            self._process_headers(df_headers)
            return True

        except Exception as e:
            logging.error(f"Ошибка загрузки сигналов: {e}", exc_info=True)
            return False

    def _read_file_headers(self) -> pd.DataFrame:
        """Читает заголовки из файла"""
        kwargs = {
            "encoding": self.model.encoding,
            "delimiter": self.model.delimiter,
            "nrows": 0,
        }

        if self.model.is_kol_1_2:
            kwargs["skiprows"] = 1

        # Ошибка возникает, если self.model.first_filename == None.
        # Проверьте, что имя файла не None перед вызовом read_csv:
        if not self.model.first_filename:
            raise ValueError("Файл не выбран")
        return pd.read_csv(self.model.first_filename, **kwargs)

    def _process_headers(self, df: pd.DataFrame) -> None:
        """Обрабатывает заголовки и определяет временные метки"""
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
        self.model.dict_all_signals = {sig: i for i, sig in enumerate(df.columns, 1)}

        self.model.is_time = cfg.DEFAULT_TIME in self.model.dict_all_signals
        self.model.is_ms = cfg.DEFAULT_MS in self.model.dict_all_signals

        if self.model.is_time and self.model.is_ms:
            self.model.dict_all_signals[cfg.COMMON_TIME] = (
                len(self.model.dict_all_signals) + 1
            )


class PlotManager:
    """Управление построением графиков"""

    def __init__(self, model: Model, ui: MainWindowUI):
        self.model = model
        self.ui = ui

    def prepare_plot_data(self) -> bool:
        """Подготавливает данные для построения графиков.

        - Сбрасывает состояние модели данных.
        - Загружает выбранные сигналы.
        - Проверяет возможность анализа регулятора.
        - Обновляет прогресс-бар.

        Returns:
            bool: True, если данные успешно подготовлены, иначе False.
        """

        self.model.clear_state()

        # Получаем выбранные сигналы
        base_signals = self._get_signals_from_table(
            self.ui.gb_base_axe.qtable_axe, self.model.dict_base_signals
        )
        secondary_signals = self._get_signals_from_table(
            self.ui.gb_secondary_axe.qtable_axe, self.model.dict_secondary_signals
        )

        if not base_signals and not secondary_signals:
            self.ui.show_error("Не выбраны сигналы для построения графика")
            return False

        self.model.step = int(self.ui.combobox_dot.currentText())

        # Проверка, если среди выбранных сигналов есть дла АНАЛИЗА РЕГУлятора
        all_signals = base_signals + secondary_signals

        if (cfg.ANALYS_AIM in all_signals) and (cfg.GSM_A_CUR in all_signals):
            self.model.ready_to_analysis = True
        else:
            print("Данных для анализа регулятора ГСМ - нет")

        # Запускаем прогресс-бар с количеством файлов
        self.ui.start_modal_progress(maximum=len(self.model.filenames))
        try:
            self.model.df = self._load_data(all_signals)
            self.model.ready_plot = True
        finally:
            self.ui.stop_modal_progress()

        return True

    def _get_signals_from_table(
        self, table: QTableWidget, signals_dict: Dict[str, int]
    ) -> List[str]:
        """Извлекает названия сигналов из QTableWidget и обновляет словарь {название: индекс}"""
        result: List[str] = []
        for row in range(table.rowCount()):
            idx_signal = table.item(row, 0)
            name_signal = table.item(row, 1)
            if idx_signal is not None and name_signal is not None:
                try:
                    index = int(idx_signal.text())
                    name_s = name_signal.text()
                    signals_dict[name_s] = index
                    # print(f"{index=} {name_s=}")
                    result.append(name_s)
                except ValueError:
                    # Если не удалось преобразовать в int, пропускаем
                    continue
        return result

    def _load_data(self, signals: List[str]) -> pd.DataFrame:
        """Загружает данные из файлов с использованием pandas"""
        usecols = signals.copy()

        # если в архивах есть колонка миллисекунды,
        # то необходимо создать Время -> 'дата/время' + 'миллисекунды'
        if self.model.is_ms:
            usecols.extend([cfg.DEFAULT_TIME, cfg.DEFAULT_MS])
        else:
            usecols.extend([cfg.DEFAULT_TIME])

        # print(f"{usecols=}")

        # Используем функцию для usecols, чтобы избежать проблем типизации в pandas-stubs
        usecols_set = set(usecols)
        read_kwargs = {
            "encoding": self.model.encoding,
            "sep": self.model.delimiter,
            "usecols": (lambda c, s=usecols_set: c in s),
            "skiprows": 1 if self.model.is_kol_1_2 else 0,
            "decimal": self.model.decimal,
        }

        # dfs = [pd.read_csv(file, **read_kwargs) for file in self.model.filenames]

        # if not dfs:
        #     return pd.DataFrame(columns=pd.Index(list(usecols_set)))

        # df = pd.concat(dfs, ignore_index=True)

        dfs = []
        # total_files = len(self.model.filenames)
        for i, file in enumerate(self.model.filenames, start=1):
            df_part = pd.read_csv(file, **read_kwargs)
            dfs.append(df_part)

            # обновляем прогресс
            self.ui.set_modal_progress(i)

        if not dfs:
            return pd.DataFrame(columns=pd.Index(list(usecols_set)))

        df = pd.concat(dfs, ignore_index=True)

        # создаем Обобщенное время
        if self.model.is_ms:
            df[cfg.COMMON_TIME] = (
                df[cfg.DEFAULT_TIME].astype(str) + "," + df[cfg.DEFAULT_MS].astype(str)
            )

        return df


class MainLogic:
    """Основной класс логики приложения"""

    def __init__(self, ui: MainWindowUI):
        self.model = Model()
        self.ui = ui
        self.graph_window = None

        self.file_handler = FileHandler(self.model)
        self.signal_manager = SignalManager(self.model, self.ui)
        self.plot_manager = PlotManager(self.model, self.ui)

        self._setup_connections()

    def _setup_connections(self) -> None:
        """Настраивает соединения сигналов и слотов"""
        # кнопка Open files
        self.ui.gb_signals.btn_first.clicked.connect(self.load_and_prepare_data)
        
        # кнопка Построить графики
        self.ui.button_graph.clicked.connect(self.plot_graph)
        
        for group_box, dict_signal in zip(
            (self.ui.gb_base_axe, self.ui.gb_secondary_axe),
            (self.model.dict_base_signals, self.model.dict_secondary_signals),
        ):
            group_box.btn_first.clicked.connect(
                lambda _, gb=group_box, ds=dict_signal: self.add_signal(gb, ds)
            )
            group_box.btn_second.clicked.connect(
                lambda _, gb=group_box, ds=dict_signal: self.remove_signal(gb, ds)
            )
        self.ui.gb_base_axe.ch_analyzer.stateChanged.connect(self.on_checkbox_changed)

    def on_checkbox_changed(self):
        if self.ui.gb_base_axe.ch_analyzer.isChecked():
            # Добавляем сигналы только если они существуют в общем списке
            for signal_name in [cfg.ANALYS_AIM, cfg.GSM_A_CUR, cfg.GSM_B_CUR]:
                if signal_name in self.model.dict_all_signals:
                    self.add_signal(self.ui.gb_base_axe, self.model.dict_base_signals, signal_name)
        else:
            # Удаляем сигналы только если они есть в группе
            for signal_name in [cfg.ANALYS_AIM, cfg.GSM_A_CUR, cfg.GSM_B_CUR]:
                if signal_name in self.model.dict_base_signals:
                    self.remove_signal(self.ui.gb_base_axe, self.model.dict_base_signals, signal_name)

    def load_and_prepare_data(self) -> None:
        """Основной метод загрузки и подготовки данных"""
        try:
            self._clear_state()

            if not self.file_handler.open_files(self.ui):
                return

            if not self.file_handler.analyze_file(self.model.first_filename or ""):
                raise ValueError("Не удалось проанализировать файл")

            if not self.signal_manager.load_all_signals():
                raise ValueError("Не удалось загрузить сигналы")

            file_param = self.file_handler.get_file_params()
            file = file_param["first_filename"]
            delimiter = file_param["delimiter"]
            decimal = file_param["decimal"]
            is_kol_1_2 = file_param["is_kol_1_2"]

            self.ui.ql_info.setText(
                f"Исходные файлы: {file} \n"
                f"Delimiter: {delimiter} Decimal: {decimal} Кольский САРЗ 1,2 блок: {is_kol_1_2} "
            )

            self._update_ui()

        except Exception as e:
            self._show_error(f"Ошибка: {str(e)}")
            logging.error(f"Ошибка подготовки данных: {e}", exc_info=True)

    def _clear_state(self) -> None:
        """Очищает состояние приложения"""
        self.model.clear_state()
        self.ui.ql_info.setText("")
        self.ui.button_graph.setEnabled(False)
        self.ui.gb_base_axe.ch_analyzer.setEnabled(False)
        self.ui.gb_base_axe.ch_analyzer.setChecked(False)

        for group_box in (
            self.ui.gb_base_axe,
            self.ui.gb_secondary_axe,
            self.ui.gb_x_axe,
            self.ui.gb_signals,
        ):
            group_box.qtable_axe.setRowCount(0)

    def _update_ui(self) -> None:
        """Обновляет UI после загрузки данных"""
        self._update_qtable(self.ui.gb_signals, self.model.dict_all_signals)
        self._setup_time_axis()
        self.ui.button_graph.setEnabled(True)
        if (cfg.ANALYS_AIM and cfg.GSM_A_CUR) in self.model.dict_all_signals.keys():
            self.ui.gb_base_axe.ch_analyzer.setEnabled(True)

    def _update_qtable(
        self, group_box: MyGroupBox, dict_signals: Dict[str, int]
    ) -> None:
        """Обновляет Qtable таблицу сигналов"""
        group_box.qtable_axe.setRowCount(0)

        if not dict_signals:
            return

        for signal, idx in sorted(dict_signals.items(), key=lambda x: x[1]):
            row = group_box.qtable_axe.rowCount()
            group_box.qtable_axe.insertRow(row)

            group_box.qtable_axe.setItem(row, 0, QTableWidgetItem(str(idx)))
            item = QTableWidgetItem(signal)
            item.setToolTip(f"Название сигнала: {signal}")
            group_box.qtable_axe.setItem(row, 1, item)

    def _setup_time_axis(self) -> None:
        """
        Настраивает ось времени в интерфейсе.

        Пошагово выполняет:
        1. Проверяет наличие данных для времени (self.model.is_time).
        Если данных нет — показывает ошибку и завершает работу.
        2. Очищает таблицу оси X.
        3. Выбирает сигнал времени:
        - cfg.COMMON_TIME ('Время'), если данные в миллисекундах (self.model.is_ms) и время self.model.is_time
        - cfg.DEFAULT_TIME ('дата/время'), иначе.
        4. Проверяет наличие выбранного сигнала в модели (self.model.dict_all_signals).
        Если сигнала нет — показывает ошибку и завершает работу.
        5. Добавляет сигнал времени в таблицу оси X с индексом и названием.
        6. Удаляет сигнал времени из общего списка сигналов в модели.
        7. Обновляет таблицу сигналов (self._update_qtable).
        8. Устанавливает фокус на первую строку таблицы сигналов.
        """

        if not self.model.is_time:
            self._show_error("Данные для времени не найдены")
            return

        # Очищаем таблицу оси X перед добавлением
        self.ui.gb_x_axe.qtable_axe.setRowCount(0)

        # Определяем сигнал времени в зависимости от доступных данных
        if self.model.is_ms:
            self.model.time_signal = cfg.COMMON_TIME
        else:
            self.model.time_signal = cfg.DEFAULT_TIME

        # # Проверяем, что сигнал времени существует в данных
        if self.model.time_signal not in self.model.dict_all_signals.keys():
            self._show_error(
                f"Сигнал времени '{self.model.time_signal}' не найден в данных"
            )
            return

        # Получаем индекс сигнала времени
        time_idx = self.model.dict_all_signals[self.model.time_signal]
        # print(f"{time_idx=}")

        # Добавляем сигнал времени в таблицу оси X
        row = self.ui.gb_x_axe.qtable_axe.rowCount()
        self.ui.gb_x_axe.qtable_axe.insertRow(row)

        self.ui.gb_x_axe.qtable_axe.setItem(row, 0, QTableWidgetItem(str(time_idx)))
        item = QTableWidgetItem(self.model.time_signal)
        item.setToolTip(f"Сигнал времени: {self.model.time_signal}")
        self.ui.gb_x_axe.qtable_axe.setItem(row, 1, item)

        # Удаляем сигнал времени из общего списка сигналов
        self.model.dict_all_signals.pop(self.model.time_signal, None)
        # del self.model.dict_all_signals[time_signal]

        # Обновляем таблицу сигналов
        self._update_qtable(self.ui.gb_signals, self.model.dict_all_signals)

        # Устанавливаем фокус на первый элемент в таблице сигналов
        if self.ui.gb_signals.qtable_axe.rowCount() > 0:
            self.ui.gb_signals.qtable_axe.selectRow(0)

    def add_signal(self, group_box: MyGroupBox, dict_signals: Dict[str, int], 
                signal_name: Optional[str] = None) -> None:
        """Добавляет сигнал в указанную группу по названию сигнала 
        или выбранному положению в таблице"""
        
        # Получаем данные сигнала  Определяем текущую строку 
        if signal_name:
            if signal_name not in self.model.dict_all_signals:
                self.ui.show_error(f"Сигнал '{signal_name}' не найден в общем списке")
                return
            idx = self.model.dict_all_signals[signal_name]
            signal_text = signal_name
        else:
            current_row = self.ui.gb_signals.qtable_axe.currentRow()
            if current_row < 0:
                self.ui.show_error("Не выбраны сигналы для построения графика")
                return
            signal_text = self.ui.gb_signals.qtable_axe.item(current_row, 1).text()
            idx = int(self.ui.gb_signals.qtable_axe.item(current_row, 0).text())

        # Обновляем словари
        dict_signals[signal_text] = idx
        self.model.dict_all_signals.pop(signal_text, None)

        # Обновляем таблицы
        self._update_qtable(group_box, dict_signals)
        self._update_qtable(self.ui.gb_signals, self.model.dict_all_signals)
        
        # self.ui.gb_signals.qtable_axe.selectRow(current_row)

    def remove_signal(self, group_box: MyGroupBox, dict_signals: Dict[str, int],
                    signal_name: Optional[str] = None) -> None:
        """Удаляет сигнал из указанной группы"""

        # Определяем какой сигнал удалять
        if signal_name:
            # Удаляем по имени
            if signal_name not in dict_signals:
                self.ui.show_error(f"Сигнал '{signal_name}' не найден в группе")
                return
            signal_to_remove = signal_name
            idx = dict_signals[signal_name]
            
        else:
            # Удаляем по текущему выбору в таблице
            current_row = group_box.qtable_axe.currentRow()
            if current_row < 0:
                self.ui.show_error("Не выбраны сигналы для удаления")
                return
                
            signal_to_remove = group_box.qtable_axe.item(current_row, 1).text()
            idx = int(group_box.qtable_axe.item(current_row, 0).text())

        # Обновляем словари
        self.model.dict_all_signals[signal_to_remove] = idx
        dict_signals.pop(signal_to_remove, None)

        # Обновляем таблицы
        self._update_qtable(group_box, dict_signals)
        self._update_qtable(self.ui.gb_signals, self.model.dict_all_signals)

        # # Восстанавливаем фокус (если удаляли по текущей строке)
        # if signal_name is None:
        #     current_row = group_box.qtable_axe.currentRow()
        #     new_row = max(0, current_row - 1) if group_box.qtable_axe.rowCount() > 0 else 0
        #     if new_row < group_box.qtable_axe.rowCount():
        #         group_box.qtable_axe.selectRow(new_row)

    def plot_graph(self) -> None:
        """Строит график на основе выбранных данных"""
        try:
            if not self.plot_manager.prepare_plot_data():
                self.ui.stop_modal_progress()
                return

            if not self.model.ready_plot:
                self.ui.stop_modal_progress()
                self._show_error("Данные для графика не подготовлены")
                return

            # Проверяем, что есть данные
            if self.model.df is None or self.model.df.empty:
                self.ui.stop_modal_progress()
                self._show_error("Нет данных для построения графика")
                return

            # Проверяем количество точек
            n_points = len(self.model.df)
            if n_points == 0:
                self.ui.stop_modal_progress()
                self._show_error("Нет точек для построения графика")
                return

            self.ui.number_plot_point.setText(
                str(int(len(self.model.df) / self.model.step))
            )

            self.graph_window = WindowGraph(
                self.model.df,
                base_signals=list(self.model.dict_base_signals.keys()),
                secondary_signals=list(self.model.dict_secondary_signals.keys()),
                # time_signals=next(iter(self.model.dict_time_axe.items()))[0],
                time_signals=self.model.time_signal,
                step=self.model.step,
                filenames=self.model.filenames,
                enable_analys=self.model.ready_to_analysis,
            )

            self.graph_window.show()

        finally:
            self.ui.stop_modal_progress()

    def _show_error(self, message: str) -> None:
        """Показывает сообщение об ошибке"""
        QMessageBox.critical(self.ui, "Ошибка", message)


def test_FileHandker():
    model = Model()
    fh = FileHandler(model)

    test_gz_file = (
        "tg-naladka\src\DATA_in\sarz\смол\step\ШУР11-2025-07-11_115842_1.csv.gz"
    )

    print("\n=== Тест GZ файла ===")
    if fh.analyze_file(test_gz_file):
        print("Файл успешно проанализирован!")
        print("Параметры файла:", fh.get_file_params())
    else:
        print("Ошибка при анализе файла")


def test_MainLogic():

    app = QApplication(sys.argv)

    main_window = MainWindowUI("Тест Main Logic")
    MainLogic(main_window)

    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":

    # --- Тест FileHandler класса ---
    # test_FileHandker()

    # --- Тест MainLogic класса ---
    test_MainLogic()
