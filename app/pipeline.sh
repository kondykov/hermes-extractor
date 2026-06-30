#!/bin/bash

INPUT_DIR="${INPUT_DIR:-/input}"
OUTPUT_DIR="${OUTPUT_DIR:-/output}"
TMP_DIR="/tmp/hermes_workspace"

mkdir -p "$TMP_DIR"
mkdir -p "$OUTPUT_DIR"

echo "========================================================================"
echo "[*] ЗАПУСК КОНВЕЙЕРА АНАЛИЗА МОБИЛЬНЫХ ПРИЛОЖЕНИЙ ЕИС ГОСЗАКУПКИ"
echo "========================================================================"

mapfile -t APK_FILES < <(find "$INPUT_DIR" -maxdepth 1 -name "*.apk" | sort)

if [ ${#APK_FILES[@]} -eq 0 ]; then
    echo "[!] Ошибка: В папке $INPUT_DIR не найдено .apk файлов!"
    echo "Пожалуйста, положите туда файлы для анализа."
    exit 1
fi

TOTAL_APKS=0
TARGET_TXT_FILES=()

for apk in "${APK_FILES[@]}"; do
    ((TOTAL_APKS++))
    APK_NAME=$(basename "$apk" .apk)
    echo "[*] [$TOTAL_APKS] Извлечение и декомпиляция версии: $APK_NAME"

    unzip -p "$apk" "assets/index.android.bundle" > "$TMP_DIR/current.bundle" 2>/dev/null

    if [ $? -ne 0 ] || [ ! -s "$TMP_DIR/current.bundle" ]; then
        echo "    [!] Пропуск: Внутри APK не найден assets/index.android.bundle"
        continue
    fi

    DECOMPILER="hbc-decompiler"
    if ! command -v hbc-decompiler &> /dev/null; then
        DECOMPILER="$HOME/.local/bin/hbc-decompiler"
    fi

    $DECOMPILER "$TMP_DIR/current.bundle" "$TMP_DIR/decompiled.js" >/dev/null 2>&1

    cp "$TMP_DIR/decompiled.js" "$OUTPUT_DIR/${APK_NAME}.js"

    grep -oE "[a-zA-Z0-9./?=&_\\-]*api/[a-zA-Z0-9./?=&_\\-]+" "$TMP_DIR/decompiled.js" | \
    sed "s/\\\\\\//\\//g" | sed "s/\\\\//g" | sed "s/['\"]//g" | \
    sed 's/?[^ ]*//' | sort -u > "$OUTPUT_DIR/${APK_NAME}.txt"


    TARGET_TXT_FILES+=("${APK_NAME}.txt")

    echo "    [+] Успешно сохранено -> $OUTPUT_DIR/${APK_NAME}.txt"
    echo "    [+] Проброшен JS код  -> $OUTPUT_DIR/${APK_NAME}.js"
    rm -f "$TMP_DIR/current.bundle" "$TMP_DIR/decompiled.js"
done

echo "[+] Этап индивидуального извлечения завершен. Всего обработано APK: $TOTAL_APKS"

echo "[*] Запуск глубокого статического анализа сигнатур..."
if [ -f "/app/signature_extractor.py" ]; then
    python3 /app/signature_extractor.py "$OUTPUT_DIR"
elif [ -f "./signature_extractor.py" ]; then
    python3 ./signature_extractor.py "$OUTPUT_DIR"
fi

rm -rf "$TMP_DIR"
echo "========================================================================"
echo "[+] КОНВЕЙЕР УСПЕШНО СВЕРНУЛ РАБОТУ."
echo "========================================================================"
