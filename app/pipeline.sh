#!/bin/bash
set -e

INPUT_DIR="/input"
OUTPUT_DIR="/output"
TMP_DIR="/tmp/apk"

rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

echo "[*] Поиск APK..."
APK=$(ls "$INPUT_DIR"/*.apk | head -n 1)

if [ -z "$APK" ]; then
    echo "[!] APK не найден в /input"
    exit 1
fi

echo "[*] Распаковка APK..."
unzip -o "$APK" -d "$TMP_DIR"

echo "[*] Поиск JS bundle..."
BUNDLE=$(find "$TMP_DIR" -name "*.bundle" -o -name "*.jsbundle" -o -name "index.android.bundle" | head -n 1)

if [ -z "$BUNDLE" ]; then
    echo "[!] JS bundle не найден."
    exit 1
fi

echo "[*] Декомпиляция через hermes-dec..."
hermes-dec "$BUNDLE" > "$OUTPUT_DIR/decompiled.js"

echo "[*] Извлечение URL-ов..."
python3 /app/url_scanner.py

echo "[*] Извлечение методов..."
python3 /app/method_detector.py

echo "[*] Извлечение JSON-тел..."
python3 /app/body_reconstructor.py

echo "[*] Построение API-спека..."
python3 /app/api_spec_builder.py

rm -rf "$TMP_DIR"
echo "[*] Готово."
