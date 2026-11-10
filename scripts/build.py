"""Build the public dataset from NexuAlpha's verified exchange-facts file.

Usage: python scripts/build.py <path to exchange-facts-*.json>
Writes data/exchanges.json, data/exchanges.csv and the fee table inside README.md.
Only fields an official page states are kept; nothing is estimated.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE = "https://nexualpha.com/exchanges/{slug}"
TYPE_LABEL = {"cex": "CEX", "dex": "DEX", "perp-dex": "Perp DEX"}
# NexuAlpha profile slugs that differ from dataset slugs
PROFILE_SLUG = {"gate": "gate-io"}
# exchanges without a live NexuAlpha profile page
NO_PROFILE = {"mexc"}


def clean(src: dict) -> dict:
    out = []
    for e in src["exchanges"]:
        fees = {}
        for market in ("spot", "perp"):
            f = (e.get("fees") or {}).get(market) or {}
            fees[market] = {"maker_pct": f.get("maker"), "taker_pct": f.get("taker"),
                            "note": f.get("note")}
        out.append({
            "slug": e["slug"],
            "name": e["name"],
            "type": e["type"],
            "status": e["status"],
            "verified_on": e["verified_on"],
            "fees": fees,
            "fee_discount": e.get("discount") or None,
            "sources": e.get("source_urls", []),
            "profile": None if e["slug"] in NO_PROFILE
            else PROFILE.format(slug=PROFILE_SLUG.get(e["slug"], e["slug"])),
        })
    out.sort(key=lambda x: (x["status"] != "verified", x["name"].lower()))
    return {
        "name": "crypto-exchange-fees",
        "description": "Base-tier maker/taker trading fees of major crypto exchanges, "
                       "each figure read from the exchange's own fee page and dated.",
        "as_of": src["as_of"],
        "units": "percent of notional",
        "tier": "lowest (regular user) tier, before token discounts",
        "license": "CC-BY-4.0",
        "attribution": "NexuAlpha (https://nexualpha.com/rates)",
        "exchanges": out,
    }


def fmt(v):
    return "—" if v is None else f"{v:g}%"


def table(data: dict) -> str:
    rows = ["| Exchange | Type | Spot maker | Spot taker | Perp maker | Perp taker | Verified | Source |",
            "|---|---|---|---|---|---|---|---|"]
    for e in data["exchanges"]:
        s, p = e["fees"]["spot"], e["fees"]["perp"]
        src = f"[official]({e['sources'][0]})" if e["sources"] else "—"
        verified = e["verified_on"] if e["status"] == "verified" else f"unverifiable ({e['verified_on']})"
        name = f"[{e['name']}]({e['profile']})" if e["profile"] else e["name"]
        rows.append(f"| {name} | {TYPE_LABEL.get(e['type'], e['type'])} | "
                    f"{fmt(s['maker_pct'])} | {fmt(s['taker_pct'])} | {fmt(p['maker_pct'])} | "
                    f"{fmt(p['taker_pct'])} | {verified} | {src} |")
    return "\n".join(rows)


def main(path: str):
    data = clean(json.load(open(path, encoding="utf-8")))
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    # same file in data/ (public dataset) and in the MCP package (offline fallback)
    for target in (os.path.join(ROOT, "data", "exchanges.json"),
                   os.path.join(ROOT, "src", "crypto_exchange_fees_mcp", "exchanges.json")):
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
    with open(os.path.join(ROOT, "data", "exchanges.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["slug", "name", "type", "spot_maker_pct", "spot_taker_pct", "perp_maker_pct",
                    "perp_taker_pct", "status", "verified_on", "source"])
        for e in data["exchanges"]:
            s, p = e["fees"]["spot"], e["fees"]["perp"]
            w.writerow([e["slug"], e["name"], e["type"], s["maker_pct"], s["taker_pct"],
                        p["maker_pct"], p["taker_pct"], e["status"], e["verified_on"],
                        e["sources"][0] if e["sources"] else ""])
    readme = os.path.join(ROOT, "README.md")
    text = open(readme, encoding="utf-8").read()
    block = f"<!-- TABLE:START -->\n_Data as of {data['as_of']}._\n\n{table(data)}\n<!-- TABLE:END -->"
    text = re.sub(r"<!-- TABLE:START -->.*?<!-- TABLE:END -->", lambda _: block, text, flags=re.S)
    open(readme, "w", encoding="utf-8").write(text)
    print(f"built {len(data['exchanges'])} exchanges, as of {data['as_of']}")


if __name__ == "__main__":
    main(sys.argv[1])
