import re

# Мусорные подстроки (ищем в любом месте ключа)
NOISE_SUBSTRINGS = [
    # UI / RN
    "search", "Search", "SEARCH",
    "page", "Page", "PAGE",
    "screen", "Screen",
    "sort", "Sort", "SORT",
    "parallax", "Parallax",
    "sensor", "Sensor",

    # Hermes / Tokenizer
    "token", "Token", "_token", "Tokenizer", "TokenStream",

    # Axios
    "Axios", "CancelToken", "URLSearchParams",

    # Errors
    "Error", "TypeError", "BSON",

    # Device
    "device", "Device", "getDevice", "isDevice",

    # Sorting internals
    "sorted", "uniq", "unsorted",
]

# Белый список — бизнес‑поля, которые нельзя удалять
WHITELIST = {
    "fz44", "fz223", "customerFz223id",
    "limit", "pageNumber", "recordsPerPage",
    "purchaseDetailSearch", "selectedPurchaseIdBySearch",
    "authToken", "signedAuthToken"
}


def is_noise(field: str) -> bool:
    """Возвращает True, если поле мусорное."""
    if field in WHITELIST:
        return False

    lower = field.lower()

    for sub in NOISE_SUBSTRINGS:
        if sub.lower() in lower:
            return True

    return False


def filter_noise(data: dict) -> dict:
    """Фильтрует мусорные поля из JSON."""
    return {k: v for k, v in data.items() if not is_noise(k)}
