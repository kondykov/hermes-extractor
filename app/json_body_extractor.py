import re

REGEX_AXIOS_POST = re.compile(
    r"axios\.post\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*(r\d+)",
    re.IGNORECASE
)

REGEX_FETCH_BODY = re.compile(
    r"fetch\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{[^}]*body\s*:\s*JSON\.stringify\((r\d+)\)",
    re.IGNORECASE
)

REGEX_DO_REQUEST = re.compile(
    r"doRequest\s*\(\s*['\"]POST['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*(r\d+)",
    re.IGNORECASE
)

REGEX_OBJECT_INIT = re.compile(r"(r\d+)\s*=\s*\{\s*\}")

REGEX_FIELD_ASSIGN = re.compile(r"(r\d+)\s*(?:\[['\"]([a-zA-Z0-9_]+)['\"]\]|\.([a-zA-Z0-9_]+))\s*=", re.IGNORECASE)


def extract_json_bodies(js_code: str):
    """
    Возвращает:
    {
        "/api/mobile/orders/1010/app-rating": {
            "token": "...",
            "deviceId": "...",
            "searchString": "...",
            ...
        }
    }
    """

    bodies = {}
    objects = {}

    for r_id in REGEX_OBJECT_INIT.findall(js_code):
        objects[r_id] = set()

    for r_id, f1, f2 in REGEX_FIELD_ASSIGN.findall(js_code):
        field = f1 or f2
        if r_id in objects:
            objects[r_id].add(field)

    matches = []

    matches += REGEX_AXIOS_POST.findall(js_code)
    matches += REGEX_FETCH_BODY.findall(js_code)
    matches += REGEX_DO_REQUEST.findall(js_code)

    for url, r_id in matches:
        if r_id in objects:
            bodies[url] = objects[r_id]

    return bodies
