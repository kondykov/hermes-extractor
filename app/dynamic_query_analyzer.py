import re

QUERY_ANY_REGEX = re.compile(r"[?&]([^?&#/=]+)")

QUERY_KEY_VALUE_REGEX = re.compile(r"[?&]([a-zA-Z0-9_\-]+)\s*=\s*([^&#]*)")

DYNAMIC_TEMPLATE_REGEX = re.compile(r"\$\{([a-zA-Z0-9_\-]+)\}")

CONCAT_REGEX = re.compile(r"[?&]([a-zA-Z0-9_\-]+)\s*=\s*['\"]?\s*\+")

URLSEARCHPARAMS_REGEX = re.compile(r"URLSearchParams\s*\(\s*\{([^}]+)\}\s*\)")
OBJECT_PARAM_REGEX = re.compile(r"([a-zA-Z0-9_\-]+)\s*:")


def extract_all_query_params(url: str, content: str):
    params = set()

    # 1. Любые параметры после ? или &
    params.update(QUERY_ANY_REGEX.findall(url))

    # 2. key=value
    for key, val in QUERY_KEY_VALUE_REGEX.findall(url):
        params.add(key)

    # 3. Динамические шаблоны ${var}
    params.update(DYNAMIC_TEMPLATE_REGEX.findall(url))

    # 4. Конкатенации "?id=" + r123
    params.update(CONCAT_REGEX.findall(content))

    # 5. URLSearchParams({page:1,limit:20})
    for block in URLSEARCHPARAMS_REGEX.findall(content):
        params.update(OBJECT_PARAM_REGEX.findall(block))

    return params
