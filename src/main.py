import logging
import sys
from PyQt5.QtWidgets import QApplication
from win32api import GetFileVersionInfo
from MainWindowUI import MainWindow
from config.config import FONT_SIZE, FORMAT, LOG_FILE, LEVEL_LOG


def get_version():
    """
    Возвращает номер версии из файла исполняемого файла или setup.py.

    Возвращает:
        str: Номер версии.
    """
    if sys.argv[0].endswith(".exe"):  # Проверяем, запускается ли как исполняемый файл
        version_info = GetFileVersionInfo(sys.argv[0], "\\")
        version = (
            version_info["FileVersionMS"] // 65536,
            version_info["FileVersionMS"] % 65536,
            version_info["FileVersionLS"] // 65536,
            version_info["FileVersionLS"] % 65536,
        )
        return "#" + ".".join(map(str, version))
    else:
        try:
            with open("setup.py", "r", encoding="utf-8") as f:
                return f.readline().strip()
        except FileNotFoundError as e:
            logging.error(f"Ошибка при получении версии: {e}")
            return "Неизвестно"


def setup_logging():
    """Настройка логирования."""
    if sys.version_info[1]>=9:
        logging.basicConfig(
            filename=LOG_FILE, 
            encoding='utf-8', 
            level=LEVEL_LOG,
            format=FORMAT,
            filemode='a')
    else:
        logging.basicConfig(handlers=[logging.FileHandler(filename=LOG_FILE, 
                                                     encoding='utf-8', mode='a')],
                            format=FORMAT, level=LEVEL_LOG)

    logging.info('Приложение запущено')


def main():
    setup_logging()

    app = QApplication(sys.argv)

    font_size = FONT_SIZE
    style = f"""
        * {{
        font-size: {font_size}pt;
        font-family: Arial;
        }}
    """
    app.setStyleSheet(style)

    version = get_version()
    main_window = MainWindow(version)
    main_window.show()

    try:
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Ошибка при выполнении приложения: {e}")
    finally:
        logging.info("Приложение завершено.")


if __name__ == "__main__":
    main()
