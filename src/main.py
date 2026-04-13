import logging
import os
import sys
import traceback
from typing import Any, Dict

from PyQt5.QtWidgets import QApplication

import config.config as cfg
from logic.logic import MainLogic
from ui.MainWindowUI import MainWindowUI


# блок перехвата необработанных исключений (которые не были поймано try-except)
def excepthook(exc_type, exc_value, exc_tb):
    error_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    # Пишем в файл рядом с exe
    log_path = os.path.join(os.path.dirname(sys.executable), "crash.log")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(error_text)
    # И показываем в консоли
    print(error_text)
    input("Press Enter to exit...")  # чтобы окно не закрылось


sys.excepthook = excepthook


def setup_logging() -> None:
    """Настраиваем систему логирования."""
    kwargs: Dict[str, Any] = {
        "filename": cfg.LOG_FILE,
        "level": cfg.LEVEL_LOG,
        "format": cfg.FORMAT,
        "filemode": "a",
    }

    if sys.version_info >= (3, 9):
        kwargs["encoding"] = "utf-8"

    logging.basicConfig(**kwargs)
    logging.info("Запуск приложения")


def main() -> None:
    """Точка входа в приложение."""
    setup_logging()

    try:
        app = QApplication(sys.argv)
        app.setStyleSheet(f"* {{ font-size: {cfg.FONT_SIZE}pt; font-family: Arial; }}")

        main_window = MainWindowUI()
        MainLogic(main_window)  # Инъекция зависимости

        main_window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical("Критическая ошибка", exc_info=True)
        raise
    finally:
        logging.info("Приложение завершено")


if __name__ == "__main__":
    main()
