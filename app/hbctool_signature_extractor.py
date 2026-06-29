import os
import json
from hbctool_body_reconstructor import reconstruct_bodies
from hbctool_method_detector import detect_methods_from_instructions

def load_urls(path):
    urls = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            urls.append(line.strip())
    return urls

def build_api_spec(output_dir):
    urls = load_urls(os.path.join(output_dir, "hbctool_urls.txt"))
    methods = detect_methods_from_instructions(os.path.join(output_dir, "instructions.json"))
    bodies = reconstruct_bodies(os.path.join(output_dir, "instructions.json"))

    api_spec = {}

    for url in urls:
        api_spec[url] = {
            "method": methods.get(url, "GET"),
            "body": bodies.get(url, set())
        }

    return api_spec

def write_full_spec(api_spec, output_dir):
    out_path = os.path.join(output_dir, "FULL_API_SPECIFICATION.txt")

    with open(out_path, "w", encoding="utf-8") as out:
        out.write("========================================================================\n")
        out.write(" ПОЛНАЯ СПЕЦИФИКАЦИЯ API ЕИС ГОСЗАКУПКИ (hbctool)\n")
        out.write("========================================================================\n\n")

        for url, info in sorted(api_spec.items()):
            out.write(f"🌐 ЭНДПОИНТ: {url}\n")
            out.write(f"   🔹 HTTP-Метод        : {info['method']}\n")

            if info["method"] == "POST":
                out.write("   🔹 JSON Request Body :\n")
                out.write("      {\n")
                if info["body"]:
                    for f in sorted(info["body"]):
                        out.write(f'         "{f}": "value",\n')
                else:
                    out.write("         // Пустой или динамический объект\n")
                out.write("      }\n")
            else:
                out.write("   🔹 JSON Request Body : [GET — параметры в URL]\n")

            out.write("-" * 80 + "\n\n")

    print(f"[+] FULL API SPEC готов: {out_path}")
