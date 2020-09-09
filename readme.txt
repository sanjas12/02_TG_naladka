1.  grath_from_tg_static_8.py - текущая версия программы (GUI-tkinter)
    grath_from_tg_static_9.py - текущая версия программы (GUI-tkinter), возможность выбора любого  графика через кнопку "Any"

    read_csv_3_any - текущая версия программы (GUI-QT) выбора любого графика для загрузки данных из файлов csv
    
grath - модуль построения графиков на matplotlib

2.  Создание exe (второй вариант)
    1. https://stackoverflow.com/questions/41570359/how-can-i-convert-a-py-to-exe-for-python
    1. setup.py - для создания exe через cx_Freeze
    2. в командной строке         python setup.py build


3. конвертирование ui в py (через терминал) ------ python -m PyQt5.uic.pyuic -x qt_des.ui -o qt_des.py


TODO
1. Узнать сколько памяти использует программа (memory_profiler и psutil)
2. перейти на timeit
3. перейти на новый вывод сообщений f
4. добавить логирование ()




