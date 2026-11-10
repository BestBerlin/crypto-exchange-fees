"""MCP server: crypto exchange trading fees, each figure read from the official fee page.

Data: https://github.com/BestBerlin/crypto-exchange-fees (CC BY 4.0, NexuAlpha).
The live dataset is fetched from GitHub and cached; a bundled copy is the fallback.
"""
from __future__ import annotations

import json
import time
import urllib.request
from importlib import resources
from typing import Literal, Optional

from mcp.server.mcpserver import MCPServer

DATA_URL = "https://raw.githubusercontent.com/BestBerlin/crypto-exchange-fees/main/data/exchanges.json"
CACHE_SECONDS = 6 * 3600
ATTRIBUTION = ("Fee data: NexuAlpha (https://nexualpha.com/rates), each figure read from the "
               "exchange's official fee page; confirm on the exchange before trading.")

mcp = MCPServer("crypto-exchange-fees")
_cache: dict = {"at": 0.0, "data": None}


def load(force: bool = False) -> dict:
    if not force and _cache["data"] and time.time() - _cache["at"] < CACHE_SECONDS:
        return _cache["data"]
    try:
        with urllib.request.urlopen(DATA_URL, timeout=10) as r:
            data = json.load(r)
    except Exception:
        data = json.loads(resources.files(__package__).joinpath("exchanges.json").read_text("utf-8"))
    _cache.update(at=time.time(), data=data)
    return data


def _find(name: str) -> Optional[dict]:
    key = name.strip().lower().replace(".io", "").replace(" ", "")
    for e in load()["exchanges"]:
        if key in (e["slug"], e["name"].lower().replace(" ", "")):
            return e
    return None


def _row(e: dict) -> dict:
    return {
        "exchange": e["name"],
        "type": e["type"],
        "spot": {k: e["fees"]["spot"][k] for k in ("maker_pct", "taker_pct")},
        "perp": {k: e["fees"]["perp"][k] for k in ("maker_pct", "taker_pct")},
        "status": e["status"],
        "verified_on": e["verified_on"],
        "official_source": e["sources"][0] if e["sources"] else None,
        "details": e["profile"],
    }


@mcp.tool()
def list_exchanges() -> dict:
    """List the exchanges covered, with type (cex, dex, perp-dex) and verification status."""
    d = load()
    return {"as_of": d["as_of"],
            "exchanges": [{"name": e["name"], "slug": e["slug"], "type": e["type"],
                           "status": e["status"]} for e in d["exchanges"]],
            "attribution": ATTRIBUTION}


@mcp.tool()
def get_exchange_fees(exchange: str) -> dict:
    """Base-tier spot and perpetual maker/taker fees (percent) for one exchange, with the
    official source URL, the date it was read, token discounts and a details page."""
    e = _find(exchange)
    if not e:
        return {"error": f"'{exchange}' is not covered",
                "covered": [x["name"] for x in load()["exchanges"]]}
    out = _row(e)
    out.update(notes={m: e["fees"][m]["note"] for m in ("spot", "perp")},
               fee_discount=e["fee_discount"], all_sources=e["sources"],
               attribution=ATTRIBUTION)
    return out


@mcp.tool()
def compare_fees(exchanges: list[str], market: Literal["spot", "perp"] = "spot") -> dict:
    """Compare base-tier maker/taker fees of several exchanges for spot or perpetuals,
    sorted by taker fee (lowest first; exchanges without a published figure last)."""
    rows, missing = [], []
    for name in exchanges:
        e = _find(name)
        if e:
            rows.append(_row(e))
        else:
            missing.append(name)
    rows.sort(key=lambda r: (r[market]["taker_pct"] is None, r[market]["taker_pct"] or 0))
    return {"market": market, "as_of": load()["as_of"], "rows": rows,
            "not_covered": missing, "attribution": ATTRIBUTION}


@mcp.tool()
def cheapest(market: Literal["spot", "perp"] = "spot",
             side: Literal["maker", "taker"] = "taker",
             exchange_type: Optional[Literal["cex", "dex", "perp-dex"]] = None,
             top: int = 5) -> dict:
    """Rank exchanges by base-tier fee for a market and order side (verified figures only)."""
    k = f"{side}_pct"
    rows = [_row(e) for e in load()["exchanges"]
            if e["status"] == "verified" and e["fees"][market][k] is not None
            and (exchange_type is None or e["type"] == exchange_type)]
    rows.sort(key=lambda r: r[market][k])
    return {"market": market, "side": side, "as_of": load()["as_of"],
            "ranking": rows[:max(1, min(top, 20))], "attribution": ATTRIBUTION}


@mcp.tool()
def estimate_trading_cost(exchange: str, notional_usd: float,
                          market: Literal["spot", "perp"] = "spot",
                          side: Literal["maker", "taker"] = "taker",
                          trades_per_month: int = 1) -> dict:
    """Estimate fee cost in USD at the base tier: notional x fee x trades. Excludes spread,
    slippage, funding, withdrawal fees, VIP tiers and token discounts."""
    e = _find(exchange)
    if not e:
        return {"error": f"'{exchange}' is not covered"}
    pct = e["fees"][market][f"{side}_pct"]
    if pct is None:
        return {"error": f"{e['name']} publishes no base-tier {market} {side} figure we could verify",
                "official_source": e["sources"][0] if e["sources"] else None}
    per_trade = notional_usd * pct / 100
    return {"exchange": e["name"], "market": market, "side": side, "fee_pct": pct,
            "cost_per_trade_usd": round(per_trade, 4),
            "cost_per_month_usd": round(per_trade * trades_per_month, 2),
            "excludes": "spread, slippage, funding, withdrawals, VIP tiers, token discounts",
            "details": e["profile"], "attribution": ATTRIBUTION}


def main():
    mcp.run()


if __name__ == "__main__":
    main()
