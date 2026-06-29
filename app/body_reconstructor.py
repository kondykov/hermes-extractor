import re

with open("/output/decompiled.js", "r", encoding="utf-8") as f:
    js = f.read()

bodies = {}

for m in re.finditer(r'fetch\s*\(\s*["\']([^"\']+)["\']\s*,\s*\{([^}]+)\}', js):
    url = m.group(1)
    body = m.group(2)

    json_match = re.search(r'body\s*:\s*(\{[^}]+\})', body)
    if json_match:
        bodies[url] = json_match.group(1)

with open("/output/bodies.txt", "w") as f:
    for url, body in bodies.items():
        f.write(f"{url}: {body}\n")

print(f"[+] JSON-тела восстановлены для", len(bodies))
