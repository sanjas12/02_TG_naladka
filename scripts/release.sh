#!/bin/bash
set -e

# Переходим в корень проекта (папка выше scripts/)
cd "$(dirname "$0")/.."

# ─── Логирование ──────────────────────────────────────────────
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/release_$(date '+%Y%m%d_%H%M%S').log"
mkdir -p "$LOG_DIR"

# Всё что идёт в терминал — дублируется в файл
exec > >(tee -a "$LOG_FILE") 2>&1

log_info()  { echo "[INFO]  $(date '+%H:%M:%S') $1"; }
log_ok()    { echo "[OK]    $(date '+%H:%M:%S') $1"; }
log_warn()  { echo "[WARN]  $(date '+%H:%M:%S') $1"; }
log_error() { echo "[ERROR] $(date '+%H:%M:%S') $1"; }

# Ловим любой выход из скрипта
trap 'if [ $? -ne 0 ]; then log_error "Скрипт упал на строке $LINENO. См. $LOG_FILE"; fi' EXIT

log_info "Запуск release.sh"
log_info "Рабочая папка: $(pwd)"
log_info "Git версия: $(git --version)"
log_info "Log файл: $LOG_FILE"

# ─── Кодировка ────────────────────────────────────────────────
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

# ─── Git: переключаемся на master ─────────────────────────────
echo ""
log_info "Переключаемся на master"
if ! git checkout master; then
    log_error "Не удалось переключиться на master"
    exit 1
fi

log_info "Получаем изменения с remote"
if ! git pull origin master; then
    log_error "Не удалось выполнить git pull. Проверь подключение к remote."
    exit 1
fi
log_ok "master актуален"

# ─── Тесты ────────────────────────────────────────────────────
echo ""
log_info "Запускаем тесты"
if ! uv run pytest; then
    log_error "Тесты не прошли! Релиз отменён."
    exit 1
fi
log_ok "Тесты прошли успешно"

# ─── Коммиты с последнего релиза ──────────────────────────────
echo ""
log_info "Коммиты с последнего релиза:"

# Защита от отсутствия тегов
if ! git describe --tags --abbrev=0 > /dev/null 2>&1; then
    log_warn "Теги не найдены — показываем все коммиты"
    git log --oneline
else
    LAST_TAG=$(git describe --tags --abbrev=0)
    log_info "Последний тег: $LAST_TAG"
    git log "$LAST_TAG"..HEAD --oneline
fi

# ─── Текущая версия и предполагаемые bump'ы ───────────────────
echo ""
log_info "Определяем версии"

if ! CURRENT=$(uv run cz version --project 2>&1); then
    log_error "Не удалось получить текущую версию: $CURRENT"
    exit 1
fi

PATCH=$(uv run cz bump --increment PATCH --dry-run 2>&1 | grep "tag to create" | awk '{print $NF}')
MINOR=$(uv run cz bump --increment MINOR --dry-run 2>&1 | grep "tag to create" | awk '{print $NF}')
MAJOR=$(uv run cz bump --increment MAJOR --dry-run 2>&1 | grep "tag to create" | awk '{print $NF}')

log_info "Текущая версия: $CURRENT"

echo ""
echo "Выбери тип релиза:"
echo "  1) Авто    — определить по коммитам (feat/fix)"
echo "  2) PATCH   — $CURRENT → $PATCH"
echo "  3) MINOR   — $CURRENT → $MINOR"
echo "  4) MAJOR   — $CURRENT → $MAJOR"
echo "  5) Вручную — ввести версию"
echo "  0) Отмена"
echo ""
read -p "Выбор (0-5): " choice
log_info "Выбор пользователя: $choice"

# ─── Bump ─────────────────────────────────────────────────────
do_bump() {
    local cmd=$1
    local label=$2
    log_info "Запускаем: $cmd"
    if ! eval "$cmd"; then
        log_error "Ошибка при bump: $label"
        exit 1
    fi
    log_ok "Bump выполнен: $label"
}

case $choice in
    1)
        uv run cz bump --dry-run
        read -p "Продолжить? (y/n): " confirm
        [ "$confirm" = "y" ] && do_bump "uv run cz bump" "авто" || { log_info "Отменено."; exit 0; }
        ;;
    2)
        read -p "Продолжить? $CURRENT → $PATCH (y/n): " confirm
        [ "$confirm" = "y" ] && do_bump "uv run cz bump --increment PATCH" "PATCH" || { log_info "Отменено."; exit 0; }
        ;;
    3)
        read -p "Продолжить? $CURRENT → $MINOR (y/n): " confirm
        [ "$confirm" = "y" ] && do_bump "uv run cz bump --increment MINOR" "MINOR" || { log_info "Отменено."; exit 0; }
        ;;
    4)
        read -p "Продолжить? $CURRENT → $MAJOR (y/n): " confirm
        [ "$confirm" = "y" ] && do_bump "uv run cz bump --increment MAJOR" "MAJOR" || { log_info "Отменено."; exit 0; }
        ;;
    5)
        read -p "Введи версию (например 1.2.0): " manual_version
        read -p "Продолжить? $CURRENT → $manual_version (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            do_bump "uv run cz bump --version $manual_version" "manual $manual_version"
        else
            log_info "Отменено."
            exit 0
        fi
        ;;
    0)
        log_info "Отменено пользователем."
        exit 0
        ;;
    *)
        log_error "Неверный выбор: $choice"
        exit 1
        ;;
esac

# ─── Push ─────────────────────────────────────────────────────
log_info "Пушим в remote"
if ! git push origin master --follow-tags; then
    log_error "Не удалось выполнить git push"
    exit 1
fi

echo ""
log_ok "Релиз готов! Версия: $(git describe --tags)"
log_info "Лог сохранён: $LOG_FILE"
