import re

with open("/output/decompiled.js", "r", encoding="utf-8") as f:
    js = f.read()

methods = {}

for m in re.finditer(r'fetch\s*\(\s*["\']([^"\']+)["\']\s*,\s*\{([^}]+)\}', js):
    url = m.group(1)
    body = m.group(2)

    if "method" in body:
        if "POST" in body:
            methods[url] = "POST"
        elif "PUT" in body:
            methods[url] = "PUT"
        elif "DELETE" in body:
            methods[url] = "DELETE"
        else:
            methods[url] = "GET"
    else:
        methods[url] = "GET"

with open("/output/methods.txt", "w") as f:
    for url, method in methods.items():
        f.write(f"{method} {url}\n")

print(f"[+] Методы определены для {len(methods)} URL-ов")
