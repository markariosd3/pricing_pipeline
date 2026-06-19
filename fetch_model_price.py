import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

SEARCH_URL_TEMPLATE = "https://www.ajmadison.com/c?q={model}"
DEFAULT_URL_TEMPLATE = "https://www.ajmadison.com/cgi-bin/ajmadison/{model}.html"


class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"


def supports_color(stream):
    return stream.isatty() and os.environ.get("NO_COLOR") is None


def colorize(text, style, enabled):
    if not enabled:
        return text
    return f"{style}{text}{Style.RESET}"


class ColoredArgumentParser(argparse.ArgumentParser):
    def format_help(self):
        help_text = super().format_help()
        if not supports_color(sys.stdout):
            return help_text

        replacements = [
            ("usage:", colorize("usage:", Style.CYAN + Style.BOLD, True)),
            (
                "positional arguments:",
                colorize("positional arguments:", Style.GREEN + Style.BOLD, True),
            ),
            ("options:", colorize("options:", Style.YELLOW + Style.BOLD, True)),
        ]
        for old, new in replacements:
            help_text = help_text.replace(old, new)
        return help_text

    def error(self, message):
        if supports_color(sys.stderr):
            self._print_message(colorize(f"error: {message}\n", Style.RED + Style.BOLD, True), sys.stderr)
            self.print_help(sys.stderr)
            self.exit(2)
        super().error(message)


def parse_price(text):
    if not text:
        return None
    cleaned = text.strip().replace("$", "").replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def resolve_model(model):
    """Use AJ Madison search/redirect to resolve base model to full model slug."""
    response = requests.get(
        SEARCH_URL_TEMPLATE.format(model=model),
        headers={**DEFAULT_HEADERS, "Referer": "https://www.ajmadison.com/"},
        allow_redirects=True,
        timeout=10,
    )
    response.raise_for_status()
    resolved = response.url.split("/")[-1].replace(".html", "")
    return resolved, response


def fetch_prices(
    model,
    sale_price_attr_name="itemprop",
    sale_price_attr_value="price",
    sale_price_value_attr="content",
    regular_price_attr_name="class",
    regular_price_attr_value="pc-pricing__list-price",
    regular_price_inner_tag="del",
):
    resolved_model, response = resolve_model(model)

    soup = BeautifulSoup(response.text, "html.parser")

    sale_price_el = soup.find(attrs={sale_price_attr_name: sale_price_attr_value})
    sale_price = parse_price(
        sale_price_el.get(sale_price_value_attr) if sale_price_el else None
    )

    regular_price_el = soup.find(attrs={regular_price_attr_name: regular_price_attr_value})
    list_price = None
    if regular_price_el:
        regular_price_value_el = regular_price_el.find(regular_price_inner_tag)
        list_price = parse_price(
            regular_price_value_el.get_text() if regular_price_value_el else None
        )

    return {
        "model": resolved_model,
        "url": response.url,
        "timestamp_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "sale_price": sale_price,
        "list_price": list_price,
    }


def build_parser():
    parser = ColoredArgumentParser(
        description="Fetch sale and list prices for a product model and print JSON."
    )
    parser.add_argument("model", help='Product model, for example "DLEX4000W" or "DGC7785"')
    parser.add_argument(
        "--sale-price-attr-name",
        default="itemprop",
        help='HTML attribute name used to find the sale price element. Default: "itemprop"',
    )
    parser.add_argument(
        "--sale-price-attr-value",
        default="price",
        help='HTML attribute value used to find the sale price element. Default: "price"',
    )
    parser.add_argument(
        "--sale-price-value-attr",
        default="content",
        help='Attribute read from the sale price element. Default: "content"',
    )
    parser.add_argument(
        "--regular-price-attr-name",
        default="class",
        help='HTML attribute name used to find the regular price element. Default: "class"',
    )
    parser.add_argument(
        "--regular-price-attr-value",
        default="pc-pricing__list-price",
        help=(
            'HTML attribute value used to find the regular price element. '
            'Default: "pc-pricing__list-price"'
        ),
    )
    parser.add_argument(
        "--regular-price-inner-tag",
        default="del",
        help='Tag inside the regular price element that contains the price text. Default: "del"',
    )
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = fetch_prices(
            args.model,
            sale_price_attr_name=args.sale_price_attr_name,
            sale_price_attr_value=args.sale_price_attr_value,
            sale_price_value_attr=args.sale_price_value_attr,
            regular_price_attr_name=args.regular_price_attr_name,
            regular_price_attr_value=args.regular_price_attr_value,
            regular_price_inner_tag=args.regular_price_inner_tag,
        )
    except requests.RequestException as exc:
        print(
            colorize(f"Failed to fetch prices: {exc}", Style.RED + Style.BOLD, supports_color(sys.stderr)),
            file=sys.stderr,
        )
        return 1

    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())