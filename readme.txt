1.  grath_from_tg_static_8.py - текущая версия программы (GUI-tkinter)
    grath_from_tg_static_9.py - аналог read_csv_3_any только под(GUI-tkinter), для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше
    grath_from_tg_static_9(Qt4).py - аналог read_csv_3_any только под(Qt4) через anaconda, для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше

	
    ******************************************************

    main.py - текущая версия программы (GUI-QT5) выбора любого графика для загрузки данных из файлов csv
    grath - модуль построения графиков на matplotlib

    
    ******************************************************



2.  Создание exe (второй вариант)
    1. https://stackoverflow.com/questions/41570359/how-can-i-convert-a-py-to-exe-for-python
    1. setup.py - для создания exe через cx_Freeze
    2. в командной строке         python setup.py build


3. конвертирование ui в py (через терминал) ------ python -m PyQt5.uic.pyuic -x qt_des.ui -o qt_des.py

Help
Run->Edit Configurations -> Emulate terminal in output console* (для расшифровки ошибок  pyqt5)



TODO
1. Узнать сколько памяти использует программа (memory_profiler и psutil)
2. перейти на timeit
3. перейти на новый вывод сообщений f
4. добавить логирование ()




