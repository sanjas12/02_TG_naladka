from pathlib import Path
from enum import Enum

class AxeName(Enum):
    BASE_AXE = "Основная Ось"
    SECONDARY_AXE = "Вспомогательная Ось"
    X_AXE = "Ось X (Времени)"

# Directories
BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_DIR = Path(BASE_DIR, "config")

LOGS_DIR = Path(BASE_DIR, "logs")
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = Path(LOGS_DIR, 'log.log')

OUT_DIR = Path(BASE_DIR, "DATA_out")
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_FILE = Path(OUT_DIR, 'out_merge.csv')

#Logging
FORMAT = '%(asctime)s:%(levelname)s:%(message)s'

MYTIME = 'my time, c'
DEFAULT_TIME = 'дата/время'

# plot
TICK_MARK_COUNT = 10

# UI
FONT_SIZE = 10