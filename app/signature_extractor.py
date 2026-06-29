import re
import os
import sys
import glob
from dynamic_url_resolver import parse_dynamic_urls
from http_method_detector import detect_http_methods
from json_body_extractor import extract_json_bodies
from literal_body_detector import detect_literal_bodies
from get_request_parameters_detector import extract_get_request_parameters
from endpoint_scanner import scan_endpoints
from closure_url_resolver import resolve_closure_urls

if len(sys.argv) < 2:
    print("[!] Ошибка: Не указан путь к папке output.")
    sys.exit(1)

output_dir = sys.argv[1]
final_output = os.path.join(output_dir, "FULL_API_SPECIFICATION.txt")

regex_registry = re.compile(r"['\"]([^'\"]+)['\"]\s*:\s*(?:['\"]([^'\"]+)['\"]|null)")
regex_prop_assign = re.compile(r"r[0-9]+(?:\[['\"]([a-zA-Z0-9_]+)['\"]\]|\.([a-zA-Z0-9_]+))\s*=\s*")

exclude_keywords = ["animated", "easing", "interpolat", "invalid", "error", "bson", "color", "style"]

api_spec = {}

print("[*] Python Engine: Анализ функциональных зависимостей и построение JSON-тел...")

js_files = glob.glob(os.path.join(output_dir, "*.js"))

for js_path in js_files:
    with open(js_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

        scanned_urls = scan_endpoints(content)

        for url in scanned_urls:
            if url not in api_spec:
                api_spec[url] = {
                    "name": "scanned",
                    "method": "GET",
                    "body_fields": set()
                }

        closure_urls = resolve_closure_urls(content)

        for url, name in closure_urls.items():
            if url not in api_spec:
                api_spec[url] = {
                    "name": name,
                    "method": "GET",
                    "body_fields": set()
                }

        dynamic_urls = parse_dynamic_urls(content)
        for url in dynamic_urls:
            if url not in api_spec:
                api_spec[url] = {
                    "name": "dynamic_resolved",
                    "method": "GET",
                    "body_fields": set()
                }

        http_methods = detect_http_methods(content)

        for url, method in http_methods.items():
            if url in api_spec:
                api_spec[url]["method"] = method

        literal_bodies = detect_literal_bodies(content)

        for url, fields in literal_bodies.items():
            if url not in api_spec:
                api_spec[url] = {
                    "name": "literal_detected",
                    "method": "POST",
                    "body_fields": set(fields.keys())
                }
            else:
                api_spec[url]["body_fields"].update(fields.keys())

        dynamic_params = extract_get_request_parameters(content)

        if dynamic_params:
            for url in api_spec:
                if api_spec[url]["method"] == "POST":
                    api_spec[url]["body_fields"].update(dynamic_params)

        # json_bodies = extract_json_bodies(content)
        #
        # for url, fields in json_bodies.items():
        #     if url not in api_spec:
        #         api_spec[url] = {
        #             "name": "dynamic_resolved",
        #             "method": "POST",
        #             "body_fields": set(fields)
        #         }
        #     else:
        #         api_spec[url]["body_fields"].update(fields)

        for line in content.splitlines():
            if "purchaseCommonInfo44" in line:
                for key, val in regex_registry.findall(line):
                    if val and val != "null" and not any(x in key.lower() for x in exclude_keywords):
                        val = val.replace("\\/", "/").replace("\\", "")
                        method = "GET"
                        if any(x in key.lower() or x in val.lower() for x in
                               ["search", "login", "create", "subscribe", "update", "unsubscribe", "rating", "choose"]):
                            method = "POST"

                        api_spec[val] = {
                            "name": key,
                            "method": method,
                            "body_fields": set()
                        }

        regex_hidden = re.compile(r"\/\/\s*Original\s*name:\s*([a-zA-Z0-9_]+)\s*\n\s*r[0-9]+\s*=\s*['\"]([^'\"]+)['\"];\s*\n\s*return")

        for key, val in regex_hidden.findall(content):
            val = val.replace("\\/", "/").replace("\\", "")
            if not any(x in key.lower() for x in exclude_keywords):
                method = "POST" if "search" in val.lower() else "GET"
                api_spec[val] = {"name": key, "method": method, "body_fields": set()}

        # for line in content.splitlines():
        #     for match in regex_prop_assign.findall(line):
        #         field = match[0] if match[0] else match[1]
        #         if field and len(field) > 2 and not any(x in field.lower() for x in exclude_keywords):
        #             if any(x in field.lower() for x in ["fz44", "fz223", "search", "page", "limit", "token", "device", "sort"]):
        #                 for url in api_spec:
        #                     if api_spec[url]["method"] == "POST":
        #                         api_spec[url]["body_fields"].add(field)

with open(final_output, "w", encoding="utf-8") as out:
    out.write("========================================================================\n")
    out.write(" ПОЛНАЯ СПЕЦИФИКАЦИЯ API ЕИС ГОСЗАКУПКИ: МЕТОДЫ, СЛУЖЕБНЫЕ ИМЕНА И JSON BODY\n")
    out.write("========================================================================\n\n")

    for url, info in sorted(api_spec.items()):
        out.write(f"🌐 ЭНДПОИНТ: {url}\n")
        out.write(f"   🔹 Назначение в коде : {info['name']}\n")
        out.write(f"   🔹 HTTP-Метод        : {info['method']}\n")

        if info['method'] == "POST":
            out.write("   🔹 JSON Request Body :\n")
            out.write("      {\n")
            if info['body_fields']:
                for f in sorted(info['body_fields']):
                    if f != info['name']:
                        out.write(f'         "{f}": "value",\n')
            else:
                out.write('         // Динамический или пустой объект\n')
            out.write("      }\n")
        else:
            out.write("   🔹 JSON Request Body : [Отсутствует / Параметры передаются в URL]\n")

        out.write("-" * 80 + "\n\n")

print(f"[+] Глубокая спецификация успешно сформирована и сохранена в: {final_output}")
