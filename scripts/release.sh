#!/bin/bash
set -e

# Переходим в корень проекта (папка выше scripts/)
cd "$(dirname "$0")/.."

# Фикс кодировки для Windows
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

echo "=== Переключаемся на master ==="
git checkout master
git pull origin master

echo ""
echo "=== Запускаем тесты ==="
uv run pytest
if [ $? -ne 0 ]; then
    echo "❌ Тесты не прошли! Релиз отменён."
    exit 1
fi
echo "✅ Тесты прошли успешно"

echo ""
echo "=== Коммиты с последнего релиза ==="
git log $(git describe --tags --abbrev=0)..HEAD --oneline

# Читаем текущую версию динамически
CURRENT=$(uv run cz version --project)

# Вычисляем предполагаемые версии динамически
PATCH=$(uv run cz bump --increment PATCH --dry-run 2>&1 | grep "tag to create" | awk '{print $NF}')
MINOR=$(uv run cz bump --increment MINOR --dry-run 2>&1 | grep "tag to create" | awk '{print $NF}')
MAJOR=$(uv run cz bump --increment MAJOR --dry-run 2>&1 | grep "tag to create" | awk '{print $NF}')

echo ""
echo "=== Текущая версия: $CURRENT ==="
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

case $choice in
    1)
        echo ""
        echo "=== Предполагаемая новая версия ==="
        uv run cz bump --dry-run
        echo ""
        read -p "Продолжить? (y/n): " confirm
        [ "$confirm" = "y" ] && uv run cz bump || { echo "Отменено."; exit 0; }
        ;;
    2)
        read -p "Продолжить? $CURRENT → $PATCH (y/n): " confirm
        [ "$confirm" = "y" ] && uv run cz bump --increment PATCH || { echo "Отменено."; exit 0; }
        ;;
    3)
        read -p "Продолжить? $CURRENT → $MINOR (y/n): " confirm
        [ "$confirm" = "y" ] && uv run cz bump --increment MINOR || { echo "Отменено."; exit 0; }
        ;;
    4)
        read -p "Продолжить? $CURRENT → $MAJOR (y/n): " confirm
        [ "$confirm" = "y" ] && uv run cz bump --increment MAJOR || { echo "Отменено."; exit 0; }
        ;;
    5)
        read -p "Введи версию (например 1.2.0): " manual_version
        read -p "Продолжить? $CURRENT → $manual_version (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            uv run cz bump --version "$manual_version"
        else
            echo "Отменено."
            exit 0
        fi
        ;;
    0)
        echo "Отменено."
        exit 0
        ;;
    *)
        echo "Неверный выбор."
        exit 1
        ;;
esac

git push origin master --follow-tags
echo ""
echo "=== Релиз готов! ==="
git describe --tags
