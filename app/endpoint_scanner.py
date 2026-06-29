import re

URL_PATTERNS = [
    r'["\'](api/mobile/[^\s"\']+)["\']',
    r'["\'](epz/api/[^\s"\']+)["\']',
    r'["\'](mess/profiles-api/[^\s"\']+)["\']',
]

REGEX_URLS = [re.compile(p) for p in URL_PATTERNS]


def scan_endpoints(js_code: str):
    """
    Возвращает set всех урлов, которые встретились в коде,
    независимо от того, используются ли они в запросах.
    """
    urls = set()
    for rx in REGEX_URLS:
        for m in rx.findall(js_code):
            # чуть чистим
            url = m.replace("\\/", "/")
            urls.add(url)
    return urls
