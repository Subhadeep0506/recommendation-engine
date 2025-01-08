import json
import os
import datetime

from typing import Dict, Any, List
from collections import Counter


def capture_mode_category(products: List[Dict[str, Any]]):
    categories = []
    if isinstance(products, list):
        for product in products:
            categories.append(product["main_category"])
    else:
        categories.append(products["main_category"])

    categories_count = Counter(categories)
    categories = sorted(categories_count.items(), key=lambda x: x[1], reverse=True)
    return categories[0][0]


def capture_mode_brand(products: List[Dict[str, Any]]):
    brands = []
    if isinstance(products, list):
        for product in products:
            brands.append(product["brand"])
    else:
        brands.append(products["brand"])

    brands_count = Counter(brands)
    brands = sorted(brands_count.items(), key=lambda x: x[1], reverse=True)
    return brands[0][0]


def save_results(result: str, type: str):
    directory = "results"
    if not os.path.exists(directory):
        os.makedirs(directory)

    file_name = os.path.join(
        directory, f"results-{str(datetime.datetime.now().date())}-{type}.json"
    )
    with open(file_name, "w+") as f:
        json.dump(json.loads(result), f)

    return file_name


def read_products_from_file(file_name: str):
    with open(file_name, "r") as f:
        products = json.load(f)

    return products
