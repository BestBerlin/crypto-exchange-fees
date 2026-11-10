# Crypto Exchange Fees

Base-tier maker/taker trading fees for major crypto exchanges (CEX, DEX and perp DEX), **each figure read from the exchange's own fee page and dated**. No estimates: a value an official page does not state is left empty.

- Machine-readable: [`data/exchanges.json`](data/exchanges.json) · [`data/exchanges.csv`](data/exchanges.csv)
- Fees are percent of notional at the lowest (regular user) tier, before token discounts (e.g. BNB) and before any VIP tier.
- Every row links to the official source it was read from.

<!-- TABLE:START -->
_Data as of 2026-11-07._

| Exchange | Type | Spot maker | Spot taker | Perp maker | Perp taker | Verified | Source |
|---|---|---|---|---|---|---|---|
| [Backpack](https://nexualpha.com/exchanges/backpack) | CEX | 0.08% | 0.1% | 0.02% | 0.05% | 2026-11-07 | [official](https://backpack.exchange/fees) |
| [Binance](https://nexualpha.com/exchanges/binance) | CEX | 0.1% | 0.1% | 0.02% | 0.05% | 2026-11-07 | [official](https://www.binance.com/en/fee/schedule) |
| [Bitget](https://nexualpha.com/exchanges/bitget) | CEX | 0.1% | 0.1% | 0.02% | 0.06% | 2026-11-07 | [official](https://www.bitget.com/support/articles/12560603892734) |
| [Bybit](https://nexualpha.com/exchanges/bybit) | CEX | 0.1% | 0.1% | 0.02% | 0.055% | 2026-11-07 | [official](https://www.bybit.com/en/help-center/article/Trading-Fee-Structure) |
| [Deribit](https://nexualpha.com/exchanges/deribit) | CEX | 0.02% | 0.05% | 0.015% | 0.035% | 2026-10-10 | [official](https://www.deribit.com/api/v2/public/get_instruments?currency=USDC&kind=future) |
| [dYdX](https://nexualpha.com/exchanges/dydx) | Perp DEX | — | — | 0.01% | 0.05% | 2026-10-10 | [official](https://docs.dydx.xyz/concepts/trading/rewards) |
| [Gate](https://nexualpha.com/exchanges/gate-io) | CEX | 0.1% | 0.1% | 0.02% | 0.05% | 2026-11-07 | [official](https://www.gate.com/fee) |
| [HTX](https://nexualpha.com/exchanges/htx) | CEX | 0.2% | 0.2% | 0.02% | 0.06% | 2026-11-07 | [official](https://www.htx.com/fee/) |
| [Hyperliquid](https://nexualpha.com/exchanges/hyperliquid) | Perp DEX | 0.04% | 0.07% | 0.015% | 0.045% | 2026-11-07 | [official](https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees) |
| [Kraken](https://nexualpha.com/exchanges/kraken) | CEX | 0.4% | 0.8% | 0.02% | 0.05% | 2026-11-07 | [official](https://www.kraken.com/pro/fees) |
| [KuCoin](https://nexualpha.com/exchanges/kucoin) | CEX | — | — | 0.02% | 0.06% | 2026-10-10 | [official](https://www.kucoin.com/vip/level) |
| [OKX](https://nexualpha.com/exchanges/okx) | CEX | 0.08% | 0.1% | 0.02% | 0.05% | 2026-11-07 | [official](https://www.okx.com/fees) |
| [Uniswap](https://nexualpha.com/exchanges/uniswap) | DEX | — | — | — | — | 2026-10-08 | [official](https://support.uniswap.org/hc/en-us/articles/20131678274957-What-fees-do-I-pay-on-Uniswap) |
| [Coinbase](https://nexualpha.com/exchanges/coinbase) | CEX | — | — | — | — | unverifiable (2026-10-08) | [official](https://help.coinbase.com/en/coinbase/trading-and-funding/advanced-trade/advanced-trade-fees) |
| MEXC | CEX | — | — | — | — | unverifiable (2026-11-07) | [official](https://www.mexc.com/fee) |
<!-- TABLE:END -->

## Why this exists

Fee schedules change quietly. Many comparison pages still quote numbers that the exchanges have since replaced (for example, Kraken Pro moved to cross-platform tiers on 2026-07-09 and its tier-1 spot rate is now 0.40% / 0.80%). This dataset records what each official page says, when it was read, and where.

## Use it

```bash
curl -s https://raw.githubusercontent.com/BestBerlin/crypto-exchange-fees/main/data/exchanges.json
```

```python
import json, urllib.request
url = "https://raw.githubusercontent.com/BestBerlin/crypto-exchange-fees/main/data/exchanges.json"
data = json.load(urllib.request.urlopen(url))
cheapest_spot_taker = min(
    (e for e in data["exchanges"] if e["fees"]["spot"]["taker_pct"] is not None),
    key=lambda e: e["fees"]["spot"]["taker_pct"])
print(cheapest_spot_taker["name"])
```

## MCP server (for Claude, ChatGPT, Cursor and other AI agents)

Let an AI assistant answer "which exchange has the lowest taker fee?" from official, dated figures. Requires [uv](https://docs.astral.sh/uv/).

```json
{
  "mcpServers": {
    "crypto-exchange-fees": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/BestBerlin/crypto-exchange-fees", "crypto-exchange-fees-mcp"]
    }
  }
}
```

Tools: `list_exchanges`, `get_exchange_fees`, `compare_fees`, `cheapest`, `estimate_trading_cost`. The server reads the live dataset from this repository (cached 6 hours) and falls back to a bundled copy offline. Every answer carries the official source URL and the date it was read.

## Fields

| Field | Meaning |
|---|---|
| `fees.spot` / `fees.perp` | `maker_pct`, `taker_pct` (percent) and the note quoting the official page |
| `status` | `verified` = read from an official page; `unverifiable` = the official page showed no base-tier table |
| `verified_on` | date the official page was read |
| `fee_discount` | token-based discounts stated on the official page, if any |
| `sources` | official URLs the figures were read from |

## Method and limits

Figures are read from each exchange's public fee page or official help article and re-checked periodically. Fees can differ by region, account type, trading pair and promotion; always confirm on the exchange's own page before trading. This is not financial advice. Corrections are welcome as issues or pull requests with an official source link.

Maintained by [NexuAlpha](https://nexualpha.com/rates), which compares exchange fees, account conditions and security controls. Full methodology: <https://nexualpha.com/methodology>.

## License

Data: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — please credit "NexuAlpha (nexualpha.com/rates)" with a link. Code: MIT.
