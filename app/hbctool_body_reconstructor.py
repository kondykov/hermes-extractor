import json
import os

def reconstruct_bodies(path):
    bodies = {}

    if not os.path.exists(path):
        return bodies

    with open(path, "r", encoding="utf-8") as f:
        instr = json.load(f)

    for fn in instr.get("functions", []):
        current_url = None
        fields = set()

        for op in fn.get("ops", []):
            if op["op"] == "LoadString":
                val = op.get("value", "")
                if "api/" in val:
                    current_url = val

            if op["op"] in ("PutById", "PutByVal"):
                key = op.get("key")
                if key:
                    fields.add(key)

        if current_url:
            bodies[current_url] = fields

    return bodies
