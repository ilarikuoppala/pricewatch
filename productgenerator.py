from product import Product
import nintendo
import json
from urllib.parse import urlparse

with open("services.json", "r") as json_file:
    services = json.load(json_file)

def parse_product_url(url):
    service = [service for service in services.keys() if services[service]["url"] in url][0]
    if services[service]["style"] == "product_no":
        # Select the longest digits-only part of the url
        product_id = max([part for part in url.split("/") if is_digits(part)])
    elif services[service]["style"] == "url":
        # Select the url path without leading /
        product_id = urlparse(url).path.lstrip("/")
    elif services[service]["style"] == "nintendo":
        product_id = nintendo.get_id(url)
        print("nintendo", services[service])
        return nintendo.NintendoProduct(product_id, service)
    print(services[service])
    return Product(product_id, service)

def get_product(product_id, service):
    if services[service]["style"] == "nintendo":
        return nintendo.NintendoProduct(product_id, service)
    return Product(product_id, service)
