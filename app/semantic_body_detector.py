import re

FIELD_NAMES = [
    "deviceId",
    "deviceType",
    "deviceName",
    "token",
    "signedAuthToken",
    "apnsToken",
    "platform",
    "rating",
    "comment",
    "searchString",
    "page",
    "limit",
    "fz223",
    "fz44",
]


REGEX_CALL = re.compile(r"(get[A-Za-z0-9_]+)\s*\(")


def extract_semantic_body(js_code: str):
    """
    Возвращает set полей, которые участвуют в построении тела запроса.
    """
    fields = set()

    for func in REGEX_CALL.findall(js_code):
        if func in FUNCTION_PATTERNS:
            fields.add(FUNCTION_PATTERNS[func])

    return fields
