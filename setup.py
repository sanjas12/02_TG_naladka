#0.0.1.0
import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "excludes": ["tkinter", "unittest"],
    "zip_include_packages": ["encodings", "PySide6"],
    # "optimize": 2,
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