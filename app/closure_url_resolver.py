import re

# Ищем присваивания вида:
# _closure1_slot5 = rNN
REGEX_CLOSURE_ASSIGN = re.compile(
    r"_closure\d+_slot\d+\s*=\s*(r\d+)"
)

# Ищем объекты вида:
# rNN = { ... }
REGEX_OBJECT_LITERAL = re.compile(
    r"(r\d+)\s*=\s*\{([^}]*)\}",
    re.DOTALL
)

# Ищем обращения вида:
# _closure1_slot5.default.url.newPurchases
REGEX_CLOSURE_ACCESS = re.compile(
    r"_closure\d+_slot\d+(?:\.[a-zA-Z0-9_]+)*\.url\.([a-zA-Z0-9_]+)"
)

# Ищем строки внутри объекта:
REGEX_STRING_VALUE = re.compile(
    r"['\"]([^'\"]+)['\"]"
)


def resolve_closure_urls(js_code: str):
    """
    Возвращает словарь:
    {
        "/epz/api/priz/mobile/search/getTopOrders": "newPurchases",
        "/epz/api/priz/mobile/search": "purchases",
        ...
    }
    """

    closures = {}        # closureSlot -> rNN
    objects = {}         # rNN -> { key: value }
    resolved = {}        # url -> name

    # --- 1. Собираем closure-assign ---
    for r_id in REGEX_CLOSURE_ASSIGN.findall(js_code):
        closures[r_id] = True

    # --- 2. Собираем объектные литералы ---
    for r_id, body in REGEX_OBJECT_LITERAL.findall(js_code):
        fields = {}
        for line in body.split(","):
            if ":" in line:
                key, val = line.split(":", 1)
                key = key.strip().strip("'\"")
                val = val.strip()
                fields[key] = val
        objects[r_id] = fields

    # --- 3. Ищем обращения closureSlot.default.url.X ---
    for name in REGEX_CLOSURE_ACCESS.findall(js_code):
        # Ищем объект, который лежит в closure
        for r_id in closures:
            if r_id in objects:
                obj = objects[r_id]
                # Ищем ключ name внутри объекта
                if name in obj:
                    raw = obj[name]
                    # Извлекаем строку
                    m = REGEX_STRING_VALUE.search(raw)
                    if m:
                        url = m.group(1).replace("\\/", "/")
                        resolved[url] = name

    return resolved
