import re
import os
import sys
import glob
import json

from garbage_values_filter import is_noise
from dynamic_url_resolver import parse_dynamic_urls
from http_method_detector import detect_http_methods
from literal_body_detector import detect_literal_bodies
from get_request_parameters_detector import extract_get_request_parameters
from endpoint_scanner import scan_endpoints
from closure_url_resolver import resolve_closure_urls
from dynamic_query_analyzer import extract_all_query_params


if len(sys.argv) < 2:
    print("[!] Ошибка: Не указан путь к папке output.")
    sys.exit(1)

output_dir = sys.argv[1]

def normalize_url(url: str) -> str:
    if "?" in url:
        url = url.split("?", 1)[0]

    return url.strip().strip('"').strip("'")

# ============================================================
# ПАПКА ДЛЯ СПЕЦИФИКАЦИИ
# ============================================================

spec_dir = os.path.join(output_dir, "spec")
os.makedirs(spec_dir, exist_ok=True)

bodies_dir = os.path.join(spec_dir, "bodies")
os.makedirs(bodies_dir, exist_ok=True)

final_output = os.path.join(spec_dir, "FULL_API_SPECIFICATION.txt")
diff_path = os.path.join(spec_dir, "API_VERSIONS_DIFF.md")

regex_registry = re.compile(r"['\"]([^'\"]+)['\"]\s*:\s*(?:['\"]([^'\"]+)['\"]|null)")
regex_prop_assign = re.compile(r"r[0-9]+(?:\[['\"]([a-zA-Z0-9_]+)['\"]\]|\.([a-zA-Z0-9_]+))\s*=\s*")

exclude_keywords = ["animated", "easing", "interpolat", "invalid", "error", "bson", "color", "style"]

api_spec = {}

print("[*] Python Engine: Анализ функциональных зависимостей и построение JSON-тел...")

# ============================================================
# 1. ПЕРВИЧНЫЙ ИСТОЧНИК: ВЕРСИОННЫЕ TXT-ФАЙЛЫ
# ============================================================

version_endpoints = set()
version_files = []

for file in os.listdir(output_dir):
    if file.endswith(".txt") and not file.startswith("API_") and not file.startswith("FULL_API_SPECIFICATION"):
        version_files.append(file)
        with open(os.path.join(output_dir, file), "r", encoding="utf-8") as f:
            for line in f:
                ep = normalize_url(line.strip())
                if ep:
                    version_endpoints.add(ep)

# ============================================================
# 2. ЗАГРУЗКА РУЧНЫХ ДАННЫХ (overrides.json)
# ============================================================

manual_path = os.path.join(output_dir, "overrides.json")
manual_overrides = {}

if os.path.exists(manual_path):
    with open(manual_path, "r", encoding="utf-8-sig") as mf:
        manual_overrides = json.load(mf)

# ============================================================
# 3. АНАЛИЗ JS-ФАЙЛОВ
# ============================================================

js_files = glob.glob(os.path.join(output_dir, "*.js"))

for js_path in js_files:
    with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

        scanned_urls = scan_endpoints(content)
        for url in scanned_urls:
            url = normalize_url(url)
            if url not in api_spec:
                api_spec[url] = {"name": "scanned", "method": "GET", "body_fields": set(), "query_fields": set()}

        closure_urls = resolve_closure_urls(content)
        for url, name in closure_urls.items():
            url = normalize_url(url)
            if url not in api_spec:
                api_spec[url] = {"name": name, "method": "GET", "body_fields": set(), "query_fields": set()}

        dynamic_urls = parse_dynamic_urls(content)
        for url in dynamic_urls:
            url = normalize_url(url)
            if url not in api_spec:
                api_spec[url] = {"name": "dynamic_resolved", "method": "GET", "body_fields": set(), "query_fields": set()}

        http_methods = detect_http_methods(content)
        for url, method in http_methods.items():
            url = normalize_url(url)
            if url in api_spec:
                api_spec[url]["method"] = method

        literal_bodies = detect_literal_bodies(content)
        for url, fields in literal_bodies.items():
            url = normalize_url(url)
            clean_fields = {f for f in fields.keys() if not is_noise(f)}
            if url not in api_spec:
                api_spec[url] = {"name": "literal_detected", "method": "POST", "body_fields": clean_fields, "query_fields": set()}
            else:
                api_spec[url]["body_fields"].update(clean_fields)

        dynamic_params = extract_get_request_parameters(content)
        if dynamic_params:
            clean_params = {p for p in dynamic_params if not is_noise(p)}
            for url in api_spec:
                url = normalize_url(url)
                if api_spec[url]["method"] == "POST":
                    api_spec[url]["body_fields"].update(clean_params)

        regex_hidden = re.compile(
            r"\/\/\s*Original\s*name:\s*([a-zA-Z0-9_]+)\s*\n\s*r[0-9]+\s*=\s*['\"]([^'\"]+)['\"];\s*\n\s*return"
        )

        for key, val in regex_hidden.findall(content):
            val = val.replace("\\/", "/").replace("\\", "")
            if not any(x in key.lower() for x in exclude_keywords):
                method = "POST" if "search" in val.lower() else "GET"
                api_spec[val] = {"name": key, "method": method, "body_fields": set(), "query_fields": set()}

        for line in content.splitlines():
            for match in regex_prop_assign.findall(line):
                field = match[0] if match[0] else match[1]
                if field and len(field) > 2 and not any(x in field.lower() for x in exclude_keywords):
                    if not is_noise(field):
                        for url in api_spec:
                            if api_spec[url]["method"] == "POST":
                                api_spec[url]["body_fields"].add(field)

# ============================================================
# 4. ДОБАВЛЕНИЕ ЭНДПОИНТОВ ИЗ TXT
# ============================================================

for ep in version_endpoints:
    if ep not in api_spec:
        api_spec[ep] = {
            "name": "unknown",
            "method": "GET",
            "body_fields": set(),
            "query_fields": set()
        }

# ============================================================
# 5. ДИНАМИЧЕСКИЕ QUERY-ПАРАМЕТРЫ
# ============================================================

all_query_params = set()

for js_path in js_files:
    with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

        for url in api_spec.keys():
            params = extract_all_query_params(url, content)
            all_query_params.update(params)

clean_query_params = {p for p in all_query_params if not is_noise(p)}

for url, info in api_spec.items():
    if info["method"] == "GET":
        info["query_fields"].update(clean_query_params)

# ============================================================
# 6. ПРИМЕНЕНИЕ OVERRIDES
# ============================================================

for ep, override in manual_overrides.items():

    # если эндпоинта нет — создаём
    if ep not in api_spec:
        api_spec[ep] = {
            "closed": override.get("closed", False),
            "name": override.get("name", "manual"),
            "method": override.get("method", "GET"),
            "body_fields": set(override.get("body_fields", [])),
            "query_fields": set(override.get("query_fields", []))
        }
        api_spec[ep]["manual_override"] = True
        continue

    info = api_spec[ep]

    # новый флаг closed
    info["closed"] = override.get("closed", False)

    if "method" in override:
        info["method"] = override["method"]

    if "name" in override:
        info["name"] = override["name"]

    if "body_fields" in override:
        info["body_fields"].update(override["body_fields"])

    if "query_fields" in override:
        info["query_fields"] = set(override["query_fields"])
    else:
        if info.get("manual_override"):
            info["query_fields"] = set()

    info["manual_override"] = True

# ============================================================
# 7. ГЕНЕРАЦИЯ PAYLOAD ТОЛЬКО ДЛЯ POST
# ============================================================

for endpoint, info in api_spec.items():
    if info["method"] == "POST":
        payload = info["body_fields"]
        body_path = os.path.join(bodies_dir, f"{endpoint.replace('/', '-')}.json")
        with open(body_path, "w", encoding="utf-8") as bf:
            bf.write("{\n")
            for f in sorted(payload):
                bf.write(f'  "{f}": "value",\n')
            bf.write("}\n")

# ============================================================
# 8. ГЕНЕРАЦИЯ ПОЛНОЙ СПЕЦИФИКАЦИИ
# ============================================================

with open(final_output, "w", encoding="utf-8") as out:
    out.write("========================================================================\n")
    out.write(" ПОЛНАЯ СПЕЦИФИКАЦИЯ API ЕИС ГОСЗАКУПКИ\n")
    out.write("========================================================================\n\n")

    for url in sorted(version_endpoints):
        info = api_spec[url]
        out.write(f"🌐 ЭНДПОИНТ: {url}\n")
        out.write(f"   🔹 Назначение в коде : {info['name']}\n")
        out.write(f"   🔹 HTTP-Метод        : {info['method']}\n")
        status = "closed" if info.get("closed") else "active"
        out.write(f"   🔹 Статус эндпоинта : {status}\n")

        if info.get("manual_override"):
            out.write("   🔹 Источник данных   : manual override\n")
        else:
            out.write("   🔹 Источник данных   : auto\n")

        if info['method'] == "POST":
            out.write(f"   🔹 Payload           : spec/bodies/{url.replace('/', '-')}.json\n")
        else:
            if info["query_fields"]:
                out.write(f"   🔹 Query Parameters  : {', '.join(sorted(info['query_fields']))}\n")
            else:
                out.write("   🔹 Query Parameters  : отсутствуют\n")

        out.write("-" * 80 + "\n\n")

print(f"[+] Спецификация сохранена в: {final_output}")

# ============================================================
# 9. ГЕНЕРАЦИЯ СРАВНИТЕЛЬНОЙ ТАБЛИЦЫ
# ============================================================

versions = sorted([f.replace(".txt", "") for f in version_files])
all_endpoints = sorted(version_endpoints)

with open(diff_path, "w", encoding="utf-8") as diff:
    diff.write("# Сравнительный анализ API версий\n\n")
    diff.write("Автоматически сгенерировано\n\n")

    header = "| Endpoint | Method | Active | Payload | Query Params | " + " | ".join(versions) + " |"
    sep = "|:---|:---:|:---:|:---:|:---:|" + "|".join([":---:" for _ in versions]) + "|"

    diff.write(header + "\n")
    diff.write(sep + "\n")

    for endpoint in all_endpoints:
        info = api_spec[endpoint]

        payload_anchor = (
            f"[payload](spec/bodies/{endpoint.replace('/', '-')}.json)"
            if info["method"] == "POST"
            else "—"
        )

        if info["method"] == "GET" and info.get("manual_override"):
            if info["query_fields"]:
                query_anchor = ", ".join(sorted(info["query_fields"])) \
                    if info["method"] == "GET" and info.get("manual_override") else "—"
            else:
                query_anchor = "—"
        else:
            query_anchor = "—"

        closed_flag = "❌" if info.get("closed") else "✔"
        row = f"| `{endpoint}` | {info['method']} | {closed_flag} | {payload_anchor} | {query_anchor} "

        for v in versions:
            txt_file = os.path.join(output_dir, f"{v}.txt")
            if os.path.exists(txt_file):
                with open(txt_file, "r", encoding="utf-8") as f:
                    present = any(endpoint == line.strip() for line in f)
                row += "| ➕ " if present else "| ❌ "
            else:
                row += "| ❓ "

        row += "|"
        diff.write(row + "\n")
