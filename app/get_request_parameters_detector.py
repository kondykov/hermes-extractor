import re

REGEX_GET_REQUEST_PARAMETERS = re.compile(
    r"getRequestParameters\s*[:=]\s*function\s*\(([^)]*)\)\s*\{([^}]+)\}",
    re.DOTALL
)

def extract_get_request_parameters(js_code):
    matches = REGEX_GET_REQUEST_PARAMETERS.findall(js_code)
    fields = set()

    for args, body in matches:
        for line in body.splitlines():
            m = re.search(r"['\"]([a-zA-Z0-9_]+)['\"]\s*:", line)
            if m:
                fields.add(m.group(1))

    return fields
