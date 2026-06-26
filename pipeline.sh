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
    
    grep -oE "[a-zA-Z0-9./?=&_\\-]*api/[a-zA-Z0-9./?=&_\\-]+" "$TMP_DIR/decompiled.js" | \
    sed "s/\\\\\\//\\//g" | sed "s/\\\\//g" | sed "s/['\"]//g" | sort -u > "$OUTPUT_DIR/${APK_NAME}.txt"
    
    echo "    [+] Успешно сохранено -> $OUTPUT_DIR/${APK_NAME}.txt"
    rm -f "$TMP_DIR/current.bundle" "$TMP_DIR/decompiled.js"
done

echo "[+] Этап индивидуального извлечения завершен. Всего обработано APK: $TOTAL_APKS"

if [ "$TOTAL_APKS" -ge 2 ]; then
    echo "[*] Обнаружено 2 или более версий. Запуск генератора сравнительной таблицы..."
    
    cd "$OUTPUT_DIR" || exit 1
    TXT_FILES=( $(ls *.txt 2>/dev/null | grep -vE "API_VERSIONS_DIFF") )
    OUTPUT_DIFF="API_VERSIONS_DIFF.md"
    
    ALL_ENDPOINTS=$(cat "${TXT_FILES[@]}" | sort -u)
    
    HEADER="| Название эндпоинта шлюза API "
    SEPARATOR="|:---"
    for file in "${TXT_FILES[@]}"; do
        HEADER="$HEADER | ${file%.txt} "
        SEPARATOR="$SEPARATOR |:---:"
    done
    HEADER="$HEADER |"
    SEPARATOR="$SEPARATOR |"
    
    echo "## Сравнительный анализ изменений (Diff) сетевых эндпоинтов" > "$OUTPUT_DIFF"
    echo "Сгенерировано автоматически: $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_DIFF"
    echo "" >> "$OUTPUT_DIFF"
    echo "$HEADER" >> "$OUTPUT_DIFF"
    echo "$SEPARATOR" >> "$OUTPUT_DIFF"
    
    echo "$ALL_ENDPOINTS" | while read -r endpoint; do
        if [ -z "$endpoint" ]; then continue; fi
        ROW="| \`$endpoint\` "
        for file in "${TXT_FILES[@]}"; do
            if grep -qF "$endpoint" "$file"; then ROW="$ROW |  ➕  "; else ROW="$ROW |  ❌  "; fi
        done
        echo "$ROW |" >> "$OUTPUT_DIFF"
    done
    echo "[+] Сравнительная таблица успешно создана -> $OUTPUT_DIFF"
fi

rm -rf "$TMP_DIR"
echo "========================================================================"
echo "[+] КОНВЕЙЕР УСПЕШНО СВЕРНУЛ РАБОТУ."
echo "========================================================================"
