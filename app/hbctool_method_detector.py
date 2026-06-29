import json
import os

def detect_methods_from_instructions(path):
    methods = {}

    if not os.path.exists(path):
        return methods

    with open(path, "r", encoding="utf-8") as f:
        instr = json.load(f)

    for fn in instr.get("functions", []):
        url = None
        method = None

        for op in fn.get("ops", []):
            if op["op"] == "LoadString":
                val = op.get("value", "")
                if "api/" in val or "epz/" in val or "223/" in val:
                    url = val
                if val.upper() == "POST":
                    method = "POST"
                if val.upper() == "GET":
                    method = "GET"

        if url:
            methods[url] = method or "GET"

    return methods
