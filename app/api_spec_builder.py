urls = open("/output/urls.txt").read().splitlines()
methods = dict(line.split(" ", 1) for line in open("/output/methods.txt"))
bodies = dict(line.split(": ", 1) for line in open("/output/bodies.txt"))

with open("/output/API_SPEC.txt", "w") as f:
    for url in urls:
        method = methods.get(url, "GET")
        body = bodies.get(url, "{}")
        f.write(f"{method} {url}\nBODY: {body}\n\n")

print("[+] API_SPEC готов")
