import json
import pathlib

import pytest

from crypto_exchange_fees_mcp import server

DATA = json.loads((pathlib.Path(__file__).parent.parent / "data" / "exchanges.json").read_text())


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    monkeypatch.setattr(server, "load", lambda force=False: DATA)


def test_get_exchange_fees_by_name_and_alias():
    r = server.get_exchange_fees("Gate.io")
    assert r["exchange"] == "Gate" and r["spot"]["taker_pct"] == 0.1
    assert r["details"].startswith("https://nexualpha.com/") and "NexuAlpha" in r["attribution"]


def test_unknown_exchange_lists_coverage():
    r = server.get_exchange_fees("nonexistent")
    assert "error" in r and "Binance" in r["covered"]


def test_compare_sorts_by_taker_and_reports_missing():
    r = server.compare_fees(["kraken", "okx", "foo"], "spot")
    assert [x["exchange"] for x in r["rows"]] == ["OKX", "Kraken"] and r["not_covered"] == ["foo"]


def test_cheapest_only_verified_and_filtered():
    r = server.cheapest("perp", "taker", "perp-dex")
    assert r["ranking"] and all(x["type"] == "perp-dex" for x in r["ranking"])
    takers = [x["perp"]["taker_pct"] for x in r["ranking"]]
    assert takers == sorted(takers)


def test_estimate_cost():
    r = server.estimate_trading_cost("binance", 10000, "spot", "taker", 4)
    assert r["cost_per_trade_usd"] == 10.0 and r["cost_per_month_usd"] == 40.0


def test_estimate_cost_without_figure():
    assert "error" in server.estimate_trading_cost("mexc", 1000)
