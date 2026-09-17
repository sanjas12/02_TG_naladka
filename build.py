import glob
import os
import platform
import shutil
import sys
from typing import List, Tuple

# ── Убеждаемся, что CWD совпадает с расположением build.py ──────────────────
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from cx_Freeze import Executable, setup  # type: ignore  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from _version import __app_name__, __revision__, __version__  # noqa: E402

_sys = platform.system().lower()
if _sys == "darwin":
    _sys = "macos"
elif _sys == "windows":
    _sys = "win"
_arch = platform.machine().lower()
_py = f"{sys.version_info.major}.{sys.version_info.minor}"

# TG-Naladka-0.3.1+rev379-win_amd64-py38
output_name = f"{__app_name__}-{__version__}+{__revision__}-{_sys}_{_arch}-py{_py}"

project_root = os.path.dirname(os.path.abspath(__file__))
src_root = os.path.join(project_root, "src")
build_dir = os.path.join("build", output_name)


def get_include_files() -> List[Tuple[str, str]]:
    files: List[Tuple[str, str]] = []
    config_path = os.path.join(project_root, "settings.json")
    if os.path.exists(config_path):
        files.append((config_path, "settings.json"))
    relnote = os.path.join(project_root, "docs", "CHANGELOG.md")
    if os.path.isfile(relnote):
        files.append((relnote, "docs/CHANGELOG.md"))
    readme = os.path.join(project_root, "docs", "Readme.md")
    if os.path.isfile(readme):
        files.append((readme, "docs/Readme.md"))
    revision = os.path.join(src_root, "_revision.py")
    if os.path.isfile(revision):
        files.append((revision, "docs/_revision.py"))
    return files


exe_name = __app_name__ + (".exe" if sys.platform == "win32" else "")

build_options = {
    "path": sys.path + [src_root],
    "excludes": [
        "matplotlib.tests",
        "matplotlib.testing",
        "matplotlib.sphinxext",
        "matplotlib.backends.backend_gtk3",
        "matplotlib.backends.backend_gtk3agg",
        "matplotlib.backends.backend_gtk4",
        "matplotlib.backends.backend_gtk4agg",
        "matplotlib.backends.backend_macosx",
        "matplotlib.backends.backend_tkagg",
        "matplotlib.backends.backend_wx",
        "matplotlib.backends.backend_wxagg",
        "pandas.tests",
        "scipy",
        "setuptools",
        "wheel",
        "fontTools",
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
        "PySide",
        "PySide2",
        "PySide6",
        "IPython",
        "_pytest",
        "argcomplete",
        "commitizen",
        "coverage",
        "identify",
        "iniconfig",
        "jupyter",
        "nodeenv",
        "notebook",
        "pluggy",
        "pre_commit",
        "pygments",
        "pytest",
        "rich",
        "semantic_release",
        "tkinter",
        "debugpy",
        "distutils",
        "unittest",
        "xmlrpc",
        "curses",
    ],
    "optimize": 2,
    "include_files": get_include_files(),
    "build_exe": build_dir,
    # Чистые модули стандартной библиотеки хранятся в сжатом library.zip.
    # Пакеты с DLL и файлами данных cx_Freeze оставляет рядом с приложением.
    "zip_include_packages": [
        "collections",
        "concurrent",
        "email",
        "encodings",
        "html",
        "http",
        "importlib",
        "json",
        "logging",
        "urllib",
        "xml",
    ],
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

# ── Пост-обработка: удаляем мусор после сборки ──────────────────────────────
REMOVE_DIRS = [
    "PyQt5/Qt5/translations",
    "matplotlib/mpl-data/sample_data",
    "matplotlib/mpl-data/stylelib",
    "matplotlib/backends/web_backend",
    "matplotlib/sphinxext",
    "fontTools",
    "setuptools",
    "wheel",
    "importlib_resources/tests",
    "mpl_toolkits/axes_grid1/tests",
    "mpl_toolkits/axisartist/tests",
    "mpl_toolkits/mplot3d/tests",
    "ctypes/test",
    "unittest/test",
    "numpy/distutils",
    "numpy/f2py",
    "numpy/testing",
    "numpy/tests",
    # Неиспользуемые плагины Qt. Обязательные platforms, styles и imageformats
    # сохраняются для нормальной работы GUI и диалогов Windows.
    "PyQt5/Qt5/plugins/bearer",
    "PyQt5/Qt5/plugins/canbus",
    "PyQt5/Qt5/plugins/geoservices",
    "PyQt5/Qt5/plugins/networkinformation",
    "PyQt5/Qt5/plugins/position",
    "PyQt5/Qt5/plugins/printsupport",
    "PyQt5/Qt5/plugins/qmltooling",
    "PyQt5/Qt5/plugins/scenegraph",
    "PyQt5/Qt5/plugins/sqldrivers",
    "PyQt5/Qt5/plugins/texttospeech",
    "PyQt5/Qt5/plugins/tls",
    "PyQt5/Qt5/plugins/virtualkeyboard",
    "PyQt5/Qt5/plugins/webview",
]

lib_dir = os.path.join(build_dir, "lib")
for rel in REMOVE_DIRS:
    path = os.path.join(lib_dir, rel)
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

# Удаляем .egg-info после сборки
for egg_info in glob.glob(os.path.join(project_root, "src", "*.egg-info")):
    shutil.rmtree(egg_info)
    print(f"[CLEAN] Удалено: {egg_info}")

# Отладочные символы не требуются для запуска приложения и могут быть крупными.
for pattern in ("*.pdb", "*.lib", "*.exp"):
    for development_file in glob.glob(
        os.path.join(build_dir, "**", pattern), recursive=True
    ):
        os.remove(development_file)
        print(f"[CLEAN] Удалено: {development_file}")

# cx_Freeze копирует некоторые DLL Qt транзитивно вместе с PyQt5, хотя приложение
# не использует QML/Quick, DBus и WebSockets. Базовые QtCore/Gui/Widgets,
# QtNetwork, QtSvg и плагины Windows сохраняются.
REMOVE_QT_FILES = [
    "Qt5DBus.dll",
    "Qt5Qml.dll",
    "Qt5QmlModels.dll",
    "Qt5Quick.dll",
    "Qt5WebSockets.dll",
]
qt_bin_dir = os.path.join(lib_dir, "PyQt5", "Qt5", "bin")
for filename in REMOVE_QT_FILES:
    path = os.path.join(qt_bin_dir, filename)
    if os.path.isfile(path):
        os.remove(path)
        print(f"[CLEAN] Удалено: {path}")


def get_directory_size(path: str) -> int:
    """Возвращает суммарный размер файлов каталога."""
    return sum(
        os.path.getsize(os.path.join(root, filename))
        for root, _directories, filenames in os.walk(path)
        for filename in filenames
    )


def format_megabytes(size: int) -> str:
    """Форматирует размер в мегабайтах для лога сборки."""
    return f"{size / (1024 * 1024):.1f} МБ"


build_size = get_directory_size(build_dir)
print(f"[SIZE] Распакованная сборка: {format_megabytes(build_size)}")

largest_files = sorted(
    (
        (os.path.getsize(path), path)
        for path in glob.glob(os.path.join(build_dir, "**", "*"), recursive=True)
        if os.path.isfile(path)
    ),
    reverse=True,
)[:15]
print("[SIZE] Самые крупные файлы:")
for size, path in largest_files:
    relative_path = os.path.relpath(path, build_dir)
    print(f"[SIZE]   {format_megabytes(size):>10}  {relative_path}")
