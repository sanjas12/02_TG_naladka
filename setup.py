#0.0.1.2
import sys
from cx_Freeze import setup, Executable


file = "setup.py"

with open(file, 'r+') as f:
    version = f.readline().split('.')
    version[-1] = str(int(version[-1]) + 1)
    version = '.'.join(version)
    f.seek(0)
    f.write(version)

# для включения конкретных файлов в build
# files = [("install.cmd")]


# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "excludes": ["tkinter", "unittest"],
    "optimize": 0,      # c 2 exe не запускается
    # "include_files" : files
}

# base="Win32GUI" should be used only for Windows GUI app
base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name="TG-Naladka",
    version="0.0.1.0",
    description="My TG-Naladka",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base)],
)