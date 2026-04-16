"""
Сборка cx_Freeze.
Запуск: python build.py build_exe
"""
import os
import platform
import shutil
import sys
from typing import List, Tuple

from cx_Freeze import Executable, setup  # type: ignore

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from _version import __app_name__, __revision__, __version__  # noqa: E402

_sys = platform.system().lower()
if _sys == "darwin":
    _sys = "macos"
elif _sys == "windows":
    _sys = "win"
_arch = platform.machine().lower()
_py = f"{sys.version_info.major}.{sys.version_info.minor}"

output_name = f"{__app_name__}.{_sys}-{_arch}-{_py}-{__version__}{__revision__}"

project_root = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.join(project_root, "src")
build_dir = os.path.join("build", output_name)


def get_include_files() -> List[Tuple[str, str]]:
    files: List[Tuple[str, str]] = []
    config_path = os.path.join(src_root, "config", "config.py")
    if os.path.exists(config_path):
        files.append((config_path, "config/config.py"))
    relnote_dir = os.path.join(project_root, "Documentation", "RelNote")
    if os.path.isdir(relnote_dir):
        files.append((relnote_dir, "Documentation/RelNote"))
    return files


exe_name = __app_name__ + (".exe" if sys.platform == "win32" else "")

build_options = {
    "path": sys.path + [src_root],
    "excludes": [
        "matplotlib.tests",
        "matplotlib.testing",
        "pandas.tests",
        "scipy",
        "PyQt5.QtWebEngine",
        "PyQt5.QtNetwork",
        "PyQt5.QtSql",
        "PyQt5.QtScript",
        "PyQt5.QtSvg",
        "PyQt5.QtTest",
        "PyQt5.QtXml",
        "PyQt5.QtDesigner",
        "PyQt5.QtMultimedia",
        "PyQt5.QtMultimediaWidgets",
        "PyQt5.QtOpenGL",
        "PyQt5.QtPrintSupport",
        "PyQt5.QtQml",
        "debugpy",
        "distutils",
    ],
    "optimize": 2,
    "include_files": get_include_files(),
    "build_exe": build_dir,
}

setup(
    name=__app_name__,
    version=__version__,
    description="TG Analysis Tool",
    options={"build_exe": build_options},
    executables=[
        Executable(
            os.path.join(src_root, "main.py"),
            target_name=exe_name,
            # base="Win32GUI",  # раскомментировать чтобы скрыть консоль на Windows
        )
    ],
)

# ---------------------------------------------------------------------------
# Пост-обработка: удаляем мусор после сборки
# ---------------------------------------------------------------------------
REMOVE_DIRS = [
    "lib/PyQt5/Qt5/translations",
    # "matplotlib/mpl-data/sample_data",
    # "matplotlib/mpl-data/stylelib",
]

for rel in REMOVE_DIRS:
    path = os.path.join(build_dir, rel)
    if os.path.isdir(path):
        shutil.rmtree(path)
        print(f"[CLEAN] Удалено: {path}")
    else:
        print(f"[SKIP]  Не найдено: {path}")

# cx_Freeze 7.x создаёт служебную папку build/lib — удаляем её
cx_lib_dir = os.path.join("build", "lib")
if os.path.isdir(cx_lib_dir):
    shutil.rmtree(cx_lib_dir)
    print(f"[CLEAN] Удалено: {cx_lib_dir}")