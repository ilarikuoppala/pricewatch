import requests
import sys
from product import Product
from pprint import pprint

price_url = "https://api.ec.nintendo.com/v1/price?country=FI&lang=en&ids="
name_url = "https://ec.nintendo.com/FI/en/titles/"

def get_id_and_name(url):
    id_locator = 'offdeviceNsuID'
    name_locator = "pn:"
    text = requests.get(url, timeout=10).text
    id_line = None
    name_line = None
    for line in text.split('\n'):
        if id_locator in line:
            id_line = line
        if name_locator in line:
            name_line = line
    if not (id_line and name_line):
        raise Exception("Unable to read id or name")
    print(id_line)
    game_id = id_line.split(":")[1].strip(' ",')
    game_name = name_line.split(":")[1].strip(' ",')
    return game_id, game_name.strip("'")

def get_id(url):
    return get_id_and_name(url)[0]

def get_prices_json(game_id_list):
    url = price_url + ",".join(game_id_list)
    data = requests.get(url, timeout=10).json()
    return data

def get_price_json(game_id):
    return get_prices_json([game_id])

def get_price(game_id):
    prices = get_price_json(game_id)['prices'][0]
    return prices.get('discount_price', prices['regular_price'])['raw_value']

def get_name(game_id):
    game_id, name = get_id_and_name(name_url + game_id)
    return name.strip("'")

class NintendoProduct(Product):
    def fetch_name_and_price(self):
        try:
            return get_name(self.id), str(get_price(self.id))
        except Exception as e:
            print(e) ## Log and skip errors
            return self.name, str(self.price)

    @property
    def url(self):
        return name_url + self.id

    @url.setter
    def url(self, url):
        pass

if __name__ == "__main__":
    url = sys.argv[1]
    game_id, name = get_id_and_name(url)
    pprint(get_price_json(game_id))
    print(get_price(game_id))
    print(get_name(game_id))
    print(name)
