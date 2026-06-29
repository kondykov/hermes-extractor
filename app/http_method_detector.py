import re

REGEX_FETCH = re.compile(
    r"fetch\s*\(\s*['\"]([^'\"]+)['\"]\s*,\s*\{[^}]*method\s*:\s*['\"]([A-Z]+)['\"]",
    re.IGNORECASE
)

REGEX_AXIOS = re.compile(
    r"axios\.(get|post|put|patch|delete)\s*\(\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE
)

REGEX_CUSTOM = re.compile(
    r"doRequest\s*\(\s*['\"]([A-Z]+)['\"]\s*,\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE
)

REGEX_DIRECT = re.compile(
    r"r(\d+)\.method\s*=\s*['\"]([A-Z]+)['\"]",
    re.IGNORECASE
)


def detect_http_methods(js_code: str):
    """
    Возвращает словарь:
    {
        "/api/mobile/orders/917/info": "GET",
        "/api/mobile/orders/917/bidders": "POST",
        ...
    }
    """

    methods = {}

    for url, method in REGEX_FETCH.findall(js_code):
        methods[url] = method.upper()

    for method, url in REGEX_AXIOS.findall(js_code):
        methods[url] = method.upper()

    for method, url in REGEX_CUSTOM.findall(js_code):
        methods[url] = method.upper()

    for r_id, method in REGEX_DIRECT.findall(js_code):
        # здесь мы не знаем URL → он будет заполнен позже,
        # когда dynamic_url_resolver восстановит rNN → строку
        methods[f"__r{r_id}"] = method.upper()

    return methods
