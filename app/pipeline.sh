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

echo "[*] Распаковка APK во временную директорию..."
unzip -o "$APK" -d "$TMP_DIR"

echo "[*] Поиск Hermes bundle..."
HBC=$(find "$TMP_DIR" -name "*.hbc" | head -n 1)
JSBUNDLE=$(find "$TMP_DIR" -name "*.bundle" -o -name "*.jsbundle" | head -n 1)

if [ -n "$HBC" ]; then
    BYTECODE_SOURCE="$HBC"
elif [ -n "$JSBUNDLE" ]; then
    /hermes/hermes-cli/build/install/hermes/bin/hermesc -emit-bc -out "$TMP_DIR/main.hbc" "$JSBUNDLE"
    BYTECODE_SOURCE="$TMP_DIR/main.hbc"
else
    echo "[!] Ни HBC, ни JS bundle не найдены."
    exit 1
fi

echo "[*] Декомпиляция HBC → HASM..."
hbctool disasm "$BYTECODE_SOURCE" "$OUTPUT_DIR/decompiled.hasm"

echo "[*] Извлечение bytecode JSON..."
/hermes/hermes-cli/build/install/hermes/bin/hermesc -dump-bytecode -out "$OUTPUT_DIR/bytecode.json" "$BYTECODE_SOURCE"

echo "[*] Извлечение URL-ов..."
python3 /app/hbctool_url_scanner.py

echo "[*] Построение API-спека..."
python3 /app/hbctool_signature_extractor.py

echo "[*] Очистка временных файлов..."
rm -rf "$TMP_DIR"

echo "[*] Готово."
