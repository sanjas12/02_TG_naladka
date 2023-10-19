## Prerequisites ()
>=Python 3.8.10
https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170#visual-studio-2015-2017-2019-and-2022   - for exe

     ******************************************************
main.py - текущая версия программы (GUI-QT5) выбора любых данный из файлов (csv, gz, txt)
grath - модуль построения графиков на matplotlib
    ******************************************************


1.  RBMK_naladka.py(grath_from_tg_static_8.py - в предыдущих версиях) - текущая версия программы для работы на РБМК -> скачки, смещения и т.д.(GUI-tkinter) 
    
    grath_from_tg_static_9.py - аналог main.py только под(GUI-tkinter), для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше
    grath_from_tg_static_9(Qt4).py - аналог read_csv_3_any только под(Qt4) через anaconda, для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше

2.  Создание exe (второй вариант)
    1. https://stackoverflow.com/questions/41570359/how-can-i-convert-a-py-to-exe-for-python
    1. setup.py - для создания exe через cx_Freeze
    2. в командной строке         python setup.py build


3. конвертирование ui в py (через терминал) ------ python -m PyQt5.uic.pyuic -x qt_des.ui -o qt_des.py


4. PyCharm 
Help -> Run->Edit Configurations -> Emulate terminal in output console* (для расшифровки ошибок  pyqt5)



TODO
1. Узнать сколько памяти использует программа (memory_profiler и psutil)
2. перейти на timeit
3. добавить логирование ()
4. Matplotlib заменить на PyQtGrath
5. Сделать аналогичную версию на С++

help:
python -m pip  install -r requirements.txt --no-index -f d:\\temp\\python_Library

