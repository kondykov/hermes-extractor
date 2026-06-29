import json
import os
import re

# Регулярки для поиска URL-подобных строк
URL_PATTERNS = [
    re.compile(r"(api\/[^\s\"']+)"),
    re.compile(r"(epz\/[^\s\"']+)"),
    re.compile(r"(223\/[^\s\"']+)"),
    re.compile(r"(mobile\/[^\s\"']+)"),
    re.compile(r"(purchase\/[^\s\"']+)"),
    re.compile(r"(order\/[^\s\"']+)"),
]

def extract_urls_from_string(s: str):
    urls = set()
    for pattern in URL_PATTERNS:
        for match in pattern.findall(s):
            urls.add(match)
    return urls


def scan_json_file(path: str):
    urls = set()
    if not os.path.exists(path):
        return urls

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return urls

    # Если файл — массив строк
    if isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                urls.update(extract_urls_from_string(item))

    # Если файл — словарь
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                urls.update(extract_urls_from_string(value))
            elif isinstance(value, list):
                for v in value:
                    if isinstance(v, str):
                        urls.update(extract_urls_from_string(v))
            elif isinstance(value, dict):
                for v2 in value.values():
                    if isinstance(v2, str):
                        urls.update(extract_urls_from_string(v2))

    return urls


def scan_hbctool_output(output_dir: str):
    urls = set()

    # hbctool обычно создаёт такие файлы:
    candidates = [
        "string_table.json",
        "strings.json",
        "literals.json",
        "modules.json",
        "bytecode.json",
        "instructions.json",
    ]

    for filename in candidates:
        path = os.path.join(output_dir, filename)
        urls.update(scan_json_file(path))

    return sorted(urls)


if __name__ == "__main__":
    output_dir = "/output"
    urls = scan_hbctool_output(output_dir)

    out_path = os.path.join(output_dir, "hbctool_urls.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

    print(f"[+] hbctool_url_scanner: найдено {len(urls)} URL-ов. Результат: {out_path}")
