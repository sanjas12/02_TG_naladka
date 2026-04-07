import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

from PyQt5.QtWidgets import QApplication
from win32api import GetFileVersionInfo
from win32api import error as win32_error

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


def _get_version_from_frozen_exe() -> Optional[str]:
    """
    Возвращает номер версии из исполняемого файла или setup.py.

    Returns:
        Optional[str]: Номер версии в формате '#X.Y.Z' или None при ошибке
    """
    try:
        version_info = GetFileVersionInfo(sys.argv[0], "\\")  # type: ignore
        version = (
            version_info["FileVersionMS"] // 65536,
            version_info["FileVersionMS"] % 65536,
            version_info["FileVersionLS"] // 65536,
        )
        return f"#{'.'.join(map(str, version))}"
    except (win32_error, KeyError, Exception):
        return None


def _get_version_from_setup() -> Optional[str]:
    """Получение версии из корневого `setup.py` (первая строка вида `#0.1.26`)."""
    try:
        # main.py находится в /src/main.py`, поэтому корень репо — на уровень выше
        setup_path = Path(__file__).resolve().parents[1] / "setup.py"
        if not setup_path.exists():
            return None
        first_line = setup_path.read_text(encoding="utf-8").splitlines()[0].strip()
        if first_line.startswith("#") and len(first_line) > 1:
            return f"#{first_line.lstrip('#').strip()}"
    except Exception:
        return None
    return None


def get_version() -> Optional[str]:
    """Возвращает версию приложения из exe, затем из setup.py"""
    if getattr(sys, "frozen", False):
        v = _get_version_from_frozen_exe()
        if v:
            return v
    return _get_version_from_setup() or None


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

        main_window = MainWindowUI(get_version() or "Неизвестно")
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
