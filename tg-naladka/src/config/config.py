import logging
import os
from pathlib import Path
from enum import Enum

class AxeName(Enum):
    LIST_SIGNALS = "Список сигналов"
    BASE_AXE = "Основная Ось"
    SECONDARY_AXE = "Вспомогательная Ось"
    TIME_AXE = "Ось Времени"

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "config")

LOGS_DIR = Path(BASE_DIR.parent, "logs")

# Создаем директории, если они не существуют
os.makedirs(LOGS_DIR, exist_ok=True)

# LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = Path(LOGS_DIR, 'app.log')

OUT_DIR = Path(BASE_DIR, "DATA_out")
# OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = Path(OUT_DIR, 'out_merge.csv')

#Logging
FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LEVEL_LOG = logging.INFO

COMMON_TIME = 'Время'
DEFAULT_TIME = 'дата/время'
DEFAULT_MS = 'миллисекунды'

# plot
TICK_MARK_COUNT_X = 15
TICK_MARK_COUNT_Y = 10

# UI
FONT_SIZE = 8