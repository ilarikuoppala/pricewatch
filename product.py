from bs4 import BeautifulSoup
import requests
import time

class Product:
    def __init__(self, id, service):
        self.id = id
        self.service = service
        if self.service == "verkkokauppa.com":
            self.url = f"https://www.verkkokauppa.com/fi/product/{self.id}/"
        else:
            self.url = None
        self.name = None
        self.price = None
        self.updated = time.time()
        self.update()
    def update(self):
        request = requests.get(self.url)
        if request.status_code == 200:
            soup = BeautifulSoup(request.text, "html.parser")
            name_span = soup.find_all(class_="product-header-title")[0]
            price_span = soup.find_all(class_="price-tag-price__euros")[0]
            self.name = name_span.text
            self.price = price_span.text
            self.updated = time.time()
            return True 
        else:
            return False
    def fresh_data(self):
        if time.time() - self.updated > 60*60:
            self.update()
        return {
            "url": self.url,
            "name": self.name,
            "price": self.price,
            "updated": self.updated,
        }
    def __str__(self):
        return f"{self.name} ({self.price}€)"

