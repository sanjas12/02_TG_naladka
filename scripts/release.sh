#!/bin/bash
set -e

# Фикс кодировки для Windows
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

echo "=== Переключаемся на master ==="
git checkout master
git pull origin master

echo ""
echo "=== Коммиты с последнего релиза ==="
git log $(git describe --tags --abbrev=0)..HEAD --oneline

echo ""
echo "=== Предполагаемая новая версия ==="
uv run cz bump --dry-run

echo ""
read -p "Продолжить релиз? (y/n): " confirm
if [ "$confirm" = "y" ]; then
    uv run cz bump
    git push origin master --follow-tags
    echo ""
    echo "=== Релиз готов! ==="
    git describe --tags
else
    echo "Отменено."
fi
