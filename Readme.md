# TG-Naladka

Программа для визуализации(matplotlib) и анализа данных.

GUI: Qt5.

Поддерживает форматы CSV, GZ, TXT.


## Установка (из репозитория)

### 1. Требования

| Параметр | Значение |
|---|---|
| Python | 3.8.10 |
| ОС | Windows 7 и выше |
| [uv](https://github.com/astral-sh/uv) | 0.11.7 |

### 2. Настройка окружения

#### 2.1 Создание виртуального окружения (VSCode)

```bash
bash scripts/venv_pip.sh
```

#### 2.2 Установка зависимостей (если скрипт из пункта 2.1 не сработал)

Рекомендуется — через [uv](https://github.com/astral-sh/uv):

```bash
uv sync
```

Без uv:

```bash
pip install -r requirements.txt
```

> `requirements.txt` генерируется из `pyproject.toml` — не редактировать вручную.

### 3. Запуск

```bash
python main.py
```

---

## Использование (Windows — exe)

### Требования

- [Visual C++ Redistributable 2015–2022](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- ОС: Windows 7 и выше


TODO
1. Узнать сколько памяти использует программа (memory_profiler и psutil)
4. Matplotlib заменить на PyQtGrath
5. Сделать аналогичную версию на С++
6. Сделать серверную службу
7. Сделать десктопную версию
8. Сделать мобильную версию
9. Добавить тесты
11. Портировать на Linux(Astra и Ubuntu)


## old
main.py - текущая версия программы (GUI-QT5) выбора любых данный из файлов (csv, gz, txt)
grath_matplot.py - модуль построения графиков на matplotlib

RBMK_naladka.py(grath_from_tg_static_8.py - в предыдущих версиях) - текущая версия программы для работы на РБМК -> скачки, смещения и т.д.(GUI-tkinter)

grath_from_tg_static_9.py - аналог main.py только под(GUI-tkinter), для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше
grath_from_tg_static_9(Qt4).py - аналог read_csv_3_any только под(Qt4) через anaconda, для Xp - последняя версия питона 3.4.2, PyQT5 ставиться на 3.5 и выше
