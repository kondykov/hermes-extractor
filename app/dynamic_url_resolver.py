import re

REGEX_LITERAL = re.compile(r"r(\d+)\s*=\s*['\"]([^'\"]+)['\"];")

REGEX_ASSIGN = re.compile(r"r(\d+)\s*=\s*(.+?);")

REGEX_TOKEN = re.compile(r"(r\d+|\"[^\"]*\"|'[^']*')")


def parse_dynamic_urls(js_code: str):
    """
    Основная функция: принимает JS-код Hermes-декомпиляции,
    возвращает множество восстановленных динамических URL.
    """

    literals = {}
    concat = {}
    resolved_cache = {}

    for m in REGEX_LITERAL.finditer(js_code):
        r_id = int(m.group(1))
        val = m.group(2)
        literals[r_id] = val

    for m in REGEX_ASSIGN.finditer(js_code):
        r_id = int(m.group(1))
        rhs = m.group(2)

        tokens = []
        for t in REGEX_TOKEN.findall(rhs):
            if t.startswith("r"):
                tokens.append(int(t[1:]))
            else:
                tokens.append(t.strip("\"'"))

        if tokens:
            concat[r_id] = tokens

    def resolve(r_id, visited=None):
        if visited is None:
            visited = set()

        if r_id in resolved_cache:
            return resolved_cache[r_id]

        if r_id in visited:
            return ""

        visited.add(r_id)

        if r_id in literals:
            resolved_cache[r_id] = literals[r_id]
            return literals[r_id]

        if r_id in concat:
            parts = []
            for token in concat[r_id]:
                if isinstance(token, str):
                    parts.append(token)
                elif isinstance(token, int):
                    parts.append(resolve(token, visited))
            final = "".join(parts)
            resolved_cache[r_id] = final
            return final

        return ""

    dynamic_urls = set()

    for r_id in concat:
        url = resolve(r_id)
        if "api/" in url:
            url = re.sub(r"/+", "/", url)
            url = url.rstrip("/")
            dynamic_urls.add(url)

    return dynamic_urls
