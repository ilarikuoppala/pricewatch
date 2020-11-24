from bs4 import BeautifulSoup
from hashlib import sha1
import requests
import time
import json
import string
from pprint import pprint


with open("services.json", "r") as json_file:
    services = json.load(json_file)

class Product:
    def __init__(self, id, service):
        self.id = id
        self.service = service
        self.url = services[service]["url"] + self.id
        self.name = None
        self.price_in_cents = None
        self.updated = 0
        self.update()
        self.hash = sha1(str.encode(self.id + self.service)).hexdigest()
    
    @property
    def price(self):
        return self.price_in_cents/100

    @price.setter
    def price(self, value):
        raise Exception("Setting of price in euros not supported")

    def fetch_name_and_price(self):
        request = requests.get(self.url, timeout=10)
        pprint([self.url, request])
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, "html.parser")
            if "name_container_class" in services[self.service].keys():
                name_span = soup.find(class_=services[self.service]["name_container_class"])
            elif "name_container_element" in services[self.service].keys():
                name_span = soup.find(services[self.service]["name_container_element"])
            if "price_container_class" in services[self.service].keys():
                # Select the last element found with the certain class
                # This makes it work at least for service verkkokauppa.com
                price_span = soup.find_all(class_=services[self.service]["price_container_class"])[-1]
                price = price_span.text.strip()
                price = price.replace(',','.')
            elif "price_meta_property" in services[self.service].keys():
                price_element = soup.find("meta", property=services[self.service]["price_meta_property"])
                price = price_element["content"].replace(",", ".")
                price = price.split(".")[0]     # Only considering full euros for now 
                price = "".join([char for char in price if char in string.digits])
            name = name_span.text.strip()
            return name, price
        else:
            raise Exception("Response code was not 200")

    def update(self):
        try:
            self.name, price = self.fetch_name_and_price()
        except Exception as e:
            print(e)  # If unable to fetch name and price, log error and return false
            return False
        euros, cents = price.split('.')
        self.price_in_cents = int(euros)*100+int(cents)
        print(f"Data updated (last time {time.time() - self.updated}s ago) {self}")
        self.updated = time.time()
        return True 

    def fresh_data(self):
        if time.time() - self.updated > 60*60:
            self.update()
        return {
            "url": self.url,
            "name": self.name,
            "price_in_cents": self.price_in_cents,
            "updated": self.updated,
        }

    def __str__(self):
        return f"{self.name} ({self.price}€)"

    def markdown(self):
        return f"[{self}]({self.url})"

