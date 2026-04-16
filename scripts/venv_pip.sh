#!/bin/bash

# Создание venv через стандартный pip или uv

# Переходим в корень проекта (на уровень выше от scripts/)
cd "$(dirname "$0")/.." || exit 1

# ── Проверка интернета ────────────────────────────────────────────────────────

check_internet() {
    # Проверяем через curl/wget (более надежно)
    if command -v curl &>/dev/null; then
        curl -s --connect-timeout 3 --max-time 5 https://www.google.com >/dev/null 2>&1
        return $?
    elif command -v wget &>/dev/null; then
        wget -q --timeout=3 --tries=1 https://www.google.com -O /dev/null 2>&1
        return $?
    fi
}

# ── Интернет отсутствует — только локальная установка через pip ───────────────

LOCAL_PACKAGES_DIR="f:\\temp\\python_Library"

# В секции без интернета
if ! check_internet; then
    echo "❌ Интернет недоступен — устанавливаем локально через pip"
    
    echo "Cleaning previous venv..."
    rm -rf .venv
    
    python -m venv .venv
    
    # Активация
    if [[ -f ".venv/Scripts/activate" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
    
    if [ ! -f "requirements.txt" ]; then
        echo "❌ Файл requirements.txt не найден"
        exit 1
    fi
    
    
    # # Проверяем наличие всех пакетов
    # echo "Проверяем наличие пакетов в $LOCAL_PACKAGES_DIR..."
    # missing_packages=()
    
    # while IFS= read -r package; do
    #     # Пропускаем пустые строки и комментарии
    #     [[ -z "$package" || "$package" =~ ^# ]] && continue
        
    #     # Извлекаем имя пакета (без версии)
    #     package_name=$(echo "$package" | sed -E 's/([a-zA-Z0-9_-]+).*/\1/')
        
    #     # Ищем файл пакета
    #     if ! ls "$LOCAL_PACKAGES_DIR" | grep -i "$package_name" >/dev/null 2>&1; then
    #         missing_packages+=("$package_name")
    #     fi
    # done < requirements.txt
    
    # if [ ${#missing_packages[@]} -gt 0 ]; then
    #     echo "❌ Отсутствуют пакеты:"
    #     printf '%s\n' "${missing_packages[@]}"
    #     echo ""
    #     echo "Скачайте недостающие пакеты на машине с интернетом:"
    #     echo "pip download -r requirements.txt -d $LOCAL_PACKAGES_DIR"
    #     exit 1
    # fi
    
    echo "Все пакеты найдены. Устанавливаем..."
    pip install -r requirements.txt --no-index -f "$LOCAL_PACKAGES_DIR" --no-deps
    # pip install -r requirements.txt --no-index -f f:\\temp\\python_Library --no-deps
    
    echo "✅ .venv создан через pip (локальная установка)"
    exit 0

fi

# ── Интернет есть ─────────────────────────────────────────────────────────────

echo "✅ Интернет доступен"

# ── Предпочтительно: uv (быстрее, читает pyproject.toml) ──────────────────────

if command -v uv &>/dev/null; then
    echo "Найден uv — используем его"
    rm -rf .venv
    uv sync

    # Активация окружения
    if [[ -f ".venv/Scripts/activate" ]]; then
        source .venv/Scripts/activate   # Windows Git Bash
    else
        source .venv/bin/activate       # Linux / macOS
    fi
    
    echo "✅ .venv создан через uv (uv sync)  и активирован"
    exit 0
fi

# ── Fallback: стандартный pip (интернет есть, но uv нет) ──────────────────────

echo "uv не найден — используем pip"

echo "Cleaning previous venv..."
rm -rf .venv

python -m venv .venv

# Активация (Windows Git Bash / WSL / Linux / macOS)
if [[ -f ".venv/Scripts/activate" ]]; then
    source .venv/Scripts/activate   # Windows Git Bash
else
    source .venv/bin/activate       # Linux / macOS
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Файл requirements.txt не найден. Убедитесь, что вы в корне проекта."
    exit 1
fi

python -m pip install --upgrade pip
pip install -r requirements.txt

echo "✅ .venv создан через pip"