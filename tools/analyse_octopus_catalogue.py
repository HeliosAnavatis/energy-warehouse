#!/usr/bin/env python3

import requests
from urllib.parse import urlparse, parse_qs


BASE_URL = "https://api.octopus.energy/v1"


def extract_page(next_url):

    if not next_url:
        return None

    parsed = urlparse(next_url)
    params = parse_qs(parsed.query)

    return int(params["page"][0])


def get_all_products():

    products = []

    page = 1

    while True:

        response = requests.get(
            f"{BASE_URL}/products",
            params={"page": page},
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        products.extend(data["results"])

        next_page = extract_page(data["next"])

        if next_page is None:
            break

        page = next_page

    return products


def get_product(product_code):

    response = requests.get(
        f"{BASE_URL}/products/{product_code}",
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def classify_from_link(rate_url):

    response = requests.get(
        rate_url,
        params={
            "period_from": "2026-11-11T00:00:00Z",
            "period_to": "2026-11-12T00:00:00Z",
        },
        timeout=30,
    )

    response.raise_for_status()

    data = response.json()

    count = len(data.get("results", []))

    if count == 1:
        return "STANDARD", count

    return "FLEXIBLE", count


def classify_single_register(detail):

    tariffs = detail.get(
        "single_register_electricity_tariffs",
        {}
    )

    tariff = tariffs.get("_A")

    if not tariff:
        return None

    for payment_method, rate_data in tariff.items():

        if not isinstance(rate_data, dict):
            continue

        for link in rate_data.get("links", []):

            if link.get("rel") == "standard_unit_rates":

                return classify_from_link(
                    link["href"]
                )

    return None


def classify_four_rate(detail):

    tariffs = detail.get(
        "four_rate_ev_electricity_tariffs",
        {}
    )

    tariff = tariffs.get("_A")

    if not tariff:
        return None

    return "FOUR_RATE", None


def classify_product(product_code):

    detail = get_product(product_code)

    result = classify_four_rate(detail)

    if result:
        return result

    result = classify_single_register(detail)

    if result:
        return result

    return "UNKNOWN", None


def main():

    products = get_all_products()

    live_products = [
        p
        for p in products
        if p.get("available_to") is None
    ]

    print(
        f"{'PRODUCT':<45}"
        f"{'CLASSIFICATION':<15}"
        f"{'COUNT'}"
    )

    print("-" * 75)

    for product in sorted(
        live_products,
        key=lambda p: p["code"],
    ):

        code = product["code"]

        try:

            classification, count = classify_product(
                code
            )

            print(
                f"{code:<45}"
                f"{classification:<15}"
                f"{count if count is not None else ''}"
            )

        except Exception as ex:

            print(
                f"{code:<45}"
                f"ERROR           "
                f"{ex}"
            )


if __name__ == "__main__":
    main()