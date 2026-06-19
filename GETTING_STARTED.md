# Getting Started

This project fetches the current sale price and list price for an appliance model from AJ Madison.

## Requirements

- Python 3
- `requests`
- `beautifulsoup4`

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python fetch_model_price.py DLEX4000W
```

If you want to inspect the JSON output with formatting:

```bash
python fetch_model_price.py DLEX4000W | python -m json.tool
```

## Help

```bash
python fetch_model_price.py -h
```