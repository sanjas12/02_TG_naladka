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

LOGS_DIR = Path(BASE_DIR.parent, "logs")  # на уровень выше src
os.makedirs(LOGS_DIR, exist_ok=True)

LOG_FILE = Path(LOGS_DIR, 'app.log')

REPORT_DIR = Path(BASE_DIR.parent, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

# OUT_DIR = Path(BASE_DIR, "DATA_out")
# OUT_DIR.mkdir(parents=True, exist_ok=True)
# OUT_FILE = Path(OUT_DIR, 'out_merge.csv')

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

# Analys
ANALYS_AIM = "Значение развертки. Положение ГСМ"
GSM_A_CUR = "ГСМ-А.Текущее положение"
GSM_B_CUR = "ГСМ-Б.Текущее положение"

# Save plot
PLOT_FILENAME = Path(REPORT_DIR, "regulator_plot.png")

# PDF
PDF_FILENAME = Path(REPORT_DIR, "regulator_analysis.pdf")