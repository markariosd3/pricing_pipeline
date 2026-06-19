# Fetch Model Price

Fetches the current sale price and manufacturer list price for an appliance model from AJ Madison and prints JSON. Designed as a building block for automated pricing decisions.

## Project Docs

- [Getting Started](GETTING_STARTED.md)
- [Contributing](CONTRIBUTING.md)

Version: 0.1.0

## Why This Matters

Pricing appliances — especially open-box, damaged, or slow-moving units — requires knowing where the market is right now. AJ Madison is one of the largest appliance retailers in the US and a reliable pricing benchmark.

This script gives you two numbers that matter:

- **Sale price** — what AJ Madison is actually selling the unit for today
- **List price** — the manufacturer's suggested retail price

The spread between your cost basis (from HomeSource) and AJ Madison's sale price tells you how much room you have. The list price anchors the customer's perception of value.

## How It Works

AJ Madison's search endpoint (`/c?q=<model>`) redirects to the canonical product page for a given model number. This handles model number variations automatically — for example, a base model like `DGC7785` redirects to the full trim variant `DGC7785CTS`. The script follows that redirect, lands on the correct page, and parses the prices from the HTML.

This means you can pass the model number exactly as it appears in HomeSource and the script resolves it correctly without a separate lookup step.

## Requirements

- Python 3
- `requests`
- `beautifulsoup4`

```bash
pip install requests beautifulsoup4
```

## Usage

```bash
python fetch_model_price.py DLEX4000W
```

Works with base model numbers too:

```bash
python fetch_model_price.py DGC7785
```

Example output:

```json
{
  "model": "DGC7785CTS",
  "url": "https://www.ajmadison.com/cgi-bin/ajmadison/DGC7785CTS.html",
  "timestamp_utc": "2026-06-19T17:03:28Z",
  "sale_price": 9299.0,
  "list_price": null
}
```

The `model` in the output reflects what AJ Madison resolved to, which may differ from your input. The `timestamp_utc` records when the price was fetched — useful for tracking price changes over time.

## Chainable Output

Prints JSON only, no extra output, so it composes cleanly with other tools:

```bash
python fetch_model_price.py DLEX4000W | python -m json.tool
```

## Customization

The HTML selectors used to find prices can be overridden if the page structure changes:

```bash
python fetch_model_price.py DLEX4000W \
  --sale-price-attr-name itemprop \
  --sale-price-attr-value price \
  --sale-price-value-attr content \
  --regular-price-attr-name class \
  --regular-price-attr-value pc-pricing__list-price \
  --regular-price-inner-tag del
```

## Help

```bash
python fetch_model_price.py -h
```