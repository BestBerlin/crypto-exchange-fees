"""Fail if the dataset breaks its own rules (run before every publish)."""
import datetime as dt
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "data", "exchanges.json"), encoding="utf-8"))
errors = []
dt.date.fromisoformat(data["as_of"])
slugs = set()
for e in data["exchanges"]:
    where = e["slug"]
    if where in slugs:
        errors.append(f"{where}: duplicate slug")
    slugs.add(where)
    if e["status"] not in ("verified", "unverifiable"):
        errors.append(f"{where}: bad status")
    dt.date.fromisoformat(e["verified_on"])
    if not e["sources"] or not all(u.startswith("https://") for u in e["sources"]):
        errors.append(f"{where}: every row needs https official sources")
    for market in ("spot", "perp"):
        for k in ("maker_pct", "taker_pct"):
            v = e["fees"][market][k]
            if v is not None and not (-1 < v < 2):
                errors.append(f"{where}: {market}.{k}={v} out of range")
    blob = json.dumps(e).lower()
    for word in ("invite code", "ref=", "affiliate"):
        if word in blob:
            errors.append(f"{where}: contains '{word}' - dataset must stay neutral")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"ok: {len(data['exchanges'])} exchanges valid")
