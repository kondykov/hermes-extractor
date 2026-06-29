import re

with open("/output/decompiled.js", "r", encoding="utf-8") as f:
    js = f.read()

urls = set(re.findall(r'["\'](https?:\/\/[^"\']+)["\']', js))
urls.update(re.findall(r'["\'](\/api\/[^"\']+)["\']', js))

with open("/output/urls.txt", "w") as f:
    for u in sorted(urls):
        f.write(u + "\n")

print(f"[+] Найдено {len(urls)} URL-ов")
