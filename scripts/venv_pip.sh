#!/bin/bash

# uv + интернет → uv sync (если есть pyproject.toml) или uv pip install -r requirements.txt
# uv + офлайн → uv sync --no-index --find-links=... или uv pip install --no-index
# нет uv + интернет → fallback на pip install -r requirements.txt
# нет uv + офлайн → fallback на pip install --no-index -f ...
set -e

# Переходим в корень проекта (на уровень выше от scripts/)
cd "$(dirname "$0")/.." || exit 1

LOCAL_PACKAGES_DIR="d:\\temp\\python_Library"

# ── Активация venv ────────────────────────────────────────────────────────────
activate_venv() {
    if [[ -f ".venv/Scripts/activate" ]]; then
        source .venv/Scripts/activate   # Windows Git Bash
        echo " activate .venv"
    elif [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate       # Linux / macOS
    else
        echo "❌ Не удалось найти activate в .venv"
        exit 1
    fi
}

# удаление старого окружения
echo "удаляем старый .venv"
rm -rf .venv

echo "=== Проверка окружения ==="

# проверка на наличие uv
if command -v uv >/dev/null 2>&1; then
    HAS_UV=1
    echo "✔ uv найден"
else
    HAS_UV=0
    echo "✖ uv не найден"
fi

# интернет
set +e
python - <<EOF 2>/dev/null
import urllib.request
urllib.request.urlopen("https://pypi.org/simple/", timeout=3)
EOF
HAS_NET=$?
set -e

if [ $HAS_NET -eq 0 ]; then
    echo "✔ Интернет доступен"
else
    echo "✖ Интернет недоступен"
fi

# проверка файлов зависимостей
if [ -f "pyproject.toml" ]; then
    USE_PYPROJECT=1
elif [ -f "requirements.txt" ]; then
    USE_PYPROJECT=0
else
    echo "❌  Файл requirements.txt или pyproject.toml не найден"
    exit 1
fi

echo "=== Установка зависимостей ==="



if [ $HAS_UV -eq 1 ]; then
    echo "→ Используем uv"

    if [ $HAS_NET -eq 0 ]; then
        if [ $USE_PYPROJECT -eq 1 ]; then
            uv sync --group build
        else
            uv venv
            uv pip install -r requirements.txt
        fi
    else
        if [ $USE_PYPROJECT -eq 1 ]; then
            uv sync --group build --no-index --find-links="$LOCAL_PACKAGES_DIR"
            echo "✅ .venv создан и обновлен через uv (онлайн)"
        else
            uv venv
            uv pip install --no-index --find-links="$LOCAL_PACKAGES_DIR" -r requirements.txt
            echo "✅ .venv создан и обновлен через uv (офлайн / локальная папка)"
        fi
    fi


else
    echo "→ Используем pip"

    python -m venv .venv
    activate_venv

    echo "обновляем pip до 25 версии"
    python -m pip install --no-index --find-links="$LOCAL_PACKAGES_DIR" pip==25.0.1

    if [ $HAS_NET -eq 0 ]; then
        pip install -r requirements.txt
        echo "✅ .venv создан и обновлен через pip (онлайн)"
    else
        # проверка
        pip install --no-index --find-links="$LOCAL_PACKAGES_DIR" -r requirements.txt --dry-run
        # установка
        pip install --no-index --find-links="$LOCAL_PACKAGES_DIR" -r requirements.txt
        echo "✅ .venv создан и обновлен через pip (офлайн / локальная папка)"
    fi
    
fi