import re

REGEX_LITERAL_OBJECT = re.compile(
    r"(r\d+)\s*=\s*\{([^}]*)\}",
    re.DOTALL
)

REGEX_CLOSURE_ASSIGN = re.compile(
    r"_closure\d+_slot\d+\s*=\s*(r\d+)"
)

REGEX_AXIOS_POST = re.compile(
    r"post\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*(r\d+)",
    re.IGNORECASE
)

REGEX_FETCH_POST = re.compile(
    r"fetch\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{[^}]*JSON\.stringify\((r\d+)\)",
    re.IGNORECASE
)

REGEX_DO_REQUEST = re.compile(
    r"doRequest\s*\(\s*['\"]POST['\"]\s*,\s*['\"]([^'\"]+)['\"]\s*,\s*(r\d+)",
    re.IGNORECASE
)

NETWORK_FIELDS = {
    "placeOfSearch", "sortBy", "pageNumber", "recordsPerPage",
    "isGoz", "currencyId", "fz44", "fz223", "limit", "page",
    "searchString", "purchaseId", "customerId"
}


def detect_literal_bodies(js_code: str):
    """
    Возвращает:
    {
        "/api/mobile/.../newPurchases": {
            "placeOfSearch": null,
            "sortBy": "PUBLISH_DATE",
            ...
        }
    }
    """

    literals = {}
    closures = {}
    bodies = {}

    for r_id, body_raw in REGEX_LITERAL_OBJECT.findall(js_code):
        fields = {}
        for pair in body_raw.split(","):
            if ":" in pair:
                key, val = pair.split(":", 1)
                key = key.strip().strip("'\"")
                val = val.strip()
                fields[key] = val
        literals[r_id] = fields

    for r_id in REGEX_CLOSURE_ASSIGN.findall(js_code):
        closures[r_id] = True

    post_calls = []
    post_calls += REGEX_AXIOS_POST.findall(js_code)
    post_calls += REGEX_FETCH_POST.findall(js_code)
    post_calls += REGEX_DO_REQUEST.findall(js_code)

    for url, r_id in post_calls:
        if r_id in literals or r_id in closures:
            for lit_id, fields in literals.items():
                if lit_id in closures:
                    filtered = {
                        k: v for k, v in fields.items()
                        if k in NETWORK_FIELDS
                    }
                    if filtered:
                        bodies[url] = filtered

    return bodies
