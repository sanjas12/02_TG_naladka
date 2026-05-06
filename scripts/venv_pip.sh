#!/bin/bash

# uv + интернет → uv sync (если есть pyproject.toml) или uv pip install -r requirements.txt
# uv + офлайн → uv sync --no-index --find-links=... или uv pip install --no-index
# нет uv + интернет → fallback на pip install -r requirements.txt
# нет uv + офлайн → fallback на pip install --no-index -f ...

# Переходим в корень проекта (на уровень выше от scripts/)
cd "$(dirname "$0")/.." || exit 1

LOCAL_PACKAGES_DIR="d:\\temp\\python_Library"

# ── Проверка доступности PyPI ─────────────────────────────────────────────────
# ВАЖНО: корпоративный SSL-прокси (MITM) перехватывает HTTPS и подменяет сертификат.
# curl при этом может получить "валидный" ответ (он доверяет системным CA),
# а pip/python — нет, потому что они используют свой bundled certifi и видят чужой сертификат.
# Поэтому проверяем ИМЕННО через pip/python — теми же инструментами, которые потом будут ставить пакеты.
# curl используем только как последний fallback (когда python недоступен).
check_internet() {
    echo "🌐 Проверка доступности PyPI..."

    local TEST_URL="https://pypi.org/pypi/pip/json"
    local result=0
    local py

    # 1) Приоритет: python — использует те же SSL/certifi настройки, что и pip
    if command -v python3 &>/dev/null || command -v python &>/dev/null; then
        py=$(command -v python3 2>/dev/null || command -v python)
        "$py" -c "
import urllib.request, ssl, sys
try:
    # Используем стандартный SSL-контекст python (тот же, что у pip)
    ctx = ssl.create_default_context()
    r = urllib.request.urlopen('$TEST_URL', timeout=10, context=ctx)
    data = r.read(2)
    sys.exit(0 if data == b'{\"' else 1)
except Exception as e:
    sys.exit(1)
" 2>/dev/null
        result=$?

    # 2) uv — имеет собственный SSL-стек, близкий к реальному поведению
    elif command -v uv &>/dev/null; then
        uv pip install pip --dry-run --quiet 2>/dev/null
        result=$?

    # 3) curl — последний резерв; может давать ложный успех при MITM-прокси
    elif command -v curl &>/dev/null; then
        echo "⚠️  python не найден — проверка через curl (возможен ложный результат при SSL-прокси)"
        local body
        body=$(curl -s --connect-timeout 7 --max-time 15 -o - "$TEST_URL" 2>/dev/null | head -c 2)
        [[ "$body" == '{"' ]]
        result=$?

    elif command -v wget &>/dev/null; then
        echo "⚠️  python не найден — проверка через wget (возможен ложный результат при SSL-прокси)"
        local body
        body=$(wget -qO- --timeout=10 --tries=1 "$TEST_URL" 2>/dev/null | head -c 2)
        [[ "$body" == '{"' ]]
        result=$?

    else
        echo "⚠️  Нет доступных инструментов для проверки (python / uv / curl / wget)"
        return 1
    fi

    if [ $result -eq 0 ]; then
        echo "✅ PyPI доступен"
    else
        echo "❌ PyPI недоступен (SSL-прокси, firewall или нет сети) — переходим на локальную установку"
    fi

    return $result
}

# ── Активация venv ────────────────────────────────────────────────────────────
activate_venv() {
    if [[ -f ".venv/Scripts/activate" ]]; then
        source .venv/Scripts/activate   # Windows Git Bash
    elif [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate       # Linux / macOS
    else
        echo "❌ Не удалось найти activate в .venv"
        exit 1
    fi
}

# ── Локальная установка через uv ──────────────────────────────────────────────
install_offline_uv() {
    local find_links_path="$LOCAL_PACKAGES_DIR"

    # Конвертируем Windows-путь в Unix для uv, если запущено в Git Bash / Cygwin
    if [[ "$LOCAL_PACKAGES_DIR" =~ ^[A-Za-z]:\\ ]] && command -v cygpath &>/dev/null; then
        find_links_path=$(cygpath -u "$LOCAL_PACKAGES_DIR")
    fi

    if [ ! -d "$find_links_path" ]; then
        echo "❌ Локальная папка с пакетами не найдена: $LOCAL_PACKAGES_DIR"
        exit 1
    fi

    rm -rf .venv

    if [ -f "pyproject.toml" ]; then
        uv sync --group build --no-index --find-links="$find_links_path"
    elif [ -f "requirements.txt" ]; then
        uv venv
        uv pip install -r requirements.txt --no-index --find-links="$find_links_path"
    else
        echo "❌ Не найден ни pyproject.toml, ни requirements.txt"
        exit 1
    fi

    activate_venv
    echo "✅ .venv создан через uv (офлайн / локальная папка)"
}

# ── Локальная установка через pip ─────────────────────────────────────────────
install_offline_pip() {
    if [ ! -f "requirements.txt" ]; then
        echo "❌ Файл requirements.txt не найден"
        exit 1
    fi

    local find_links_path="$LOCAL_PACKAGES_DIR"
    if [[ "$LOCAL_PACKAGES_DIR" =~ ^[A-Za-z]:\\ ]] && command -v cygpath &>/dev/null; then
        find_links_path=$(cygpath -u "$LOCAL_PACKAGES_DIR")
    fi

    if [ ! -d "$find_links_path" ]; then
        echo "❌ Локальная папка с пакетами не найдена: $LOCAL_PACKAGES_DIR"
        exit 1
    fi

    rm -rf .venv
    python -m venv .venv
    activate_venv
    pip install -r requirements.txt --no-index --find-links="$find_links_path" --no-deps
    echo "✅ .venv создан через pip (офлайн / локальная папка)"
}

# ═════════════════════════════════════════════════════════════════════════════
# Основной поток
# ═════════════════════════════════════════════════════════════════════════════

if ! command -v uv &>/dev/null; then
    echo "⚠️  uv не найден — используем fallback на pip"

    if ! check_internet; then
        install_offline_pip
    else
        echo "Интернет доступен — устанавливаем через pip"
        rm -rf .venv
        python -m venv .venv
        activate_venv

        if [ ! -f "requirements.txt" ]; then
            echo "❌ Файл requirements.txt не найден"
            exit 1
        fi

        python -m pip install --upgrade pip
        pip install -r requirements.txt
        echo "✅ .venv создан через pip (uv не найден)"
    fi

    exit 0
fi

# ── uv найден ─────────────────────────────────────────────────────────────────
echo "✅ uv найден: $(uv --version)"

if ! check_internet; then
    install_offline_uv
    exit 0
fi

# ── Онлайн-режим: uv есть, интернет есть ─────────────────────────────────────
rm -rf .venv

if [ -f "pyproject.toml" ]; then
    echo "Найден pyproject.toml — используем uv sync"
    uv sync --group build
elif [ -f "requirements.txt" ]; then
    echo "Найден requirements.txt — используем uv pip install"
    uv venv
    uv pip install -r requirements.txt
else
    echo "❌ Не найден ни pyproject.toml, ни requirements.txt"
    exit 1
fi

activate_venv
echo "✅ .venv создан и активирован через uv"