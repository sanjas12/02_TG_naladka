# TG-Naladka

Программа для визуализации(matplotlib) и анализа данных.  

GUI: Qt5.

Поддерживает форматы CSV, GZ, TXT. 


## Usage (Repository)

### Prerequisites:
- Python >= 3.8.10 

- 0S >= Windows 7

### Installation
С uv (рекомендуется):
    uv sync

Без uv:
    pip install -r requirements.txt
    # requirements.txt сгенерирован из pyproject.toml, не редактировать вручную

## Usage (Windows - exe)

### Prerequisites:
- Visual C++ 2015-2022

- 0S >= Windows 7


## help
PyCharm 
Help -> Run->Edit Configurations -> Emulate terminal in output console* (для расшифровки ошибок  pyqt5)



TODO
1. Узнать сколько памяти использует программа (memory_profiler и psutil)
2. перейти на timeit
3. добавить логирование ()
4. Matplotlib заменить на PyQtGrath
5. Сделать аналогичную версию на С++
6. Сделать серверную службу
7. Сделать десктопную версию
8. Сделать мобильную версию
9. Добавить тесты
10. Поиск в списке сигналов (Qtablewidget) https://stackoverflow.com/questions/51613638/highlight-search-results-in-qtablewidgetselect-and-highlight-that-text-or-chara
11. Портировать на Linux(Astra и Ubuntu)
13. перейти на polars для версии по Win_11 для загрузки данных из csv
14. перейти на uv
15. добавить pre commit.yaml


## old
main.py - текущая версия программы (GUI-QT5) выбора любых данный из файлов (csv, gz, txt)
grath_matplot.py - модуль построения графиков на matplotlib

RBMK_naladka.py(grath_from_tg_static_8.py - в предыдущих версиях) - текущая версия программы для работы на РБМК -> скачки, смещения и т.д.(GUI-tkinter) 

grath_from_tg_static_9.py - аналог main.py только под(GUI-tkinter), для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше
grath_from_tg_static_9(Qt4).py - аналог read_csv_3_any только под(Qt4) через anaconda, для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше