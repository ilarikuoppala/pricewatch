#!/usr/bin/env python3

import telegram
from product import Product
import string
import time
import itertools
import json
from decimal import Decimal

bot = telegram.TelegramBot()
db_location = "data.sqlite3"
products = {}
with open("services.json", "r") as json_file:
    services = json.load(json_file)

def product_ids_by_user(user):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    cursor.execute(f"""SELECT product, service
                       FROM IsWatching
                       WHERE user="{user}"
                    """)
    products = cursor.fetchall()
    connection.close()
    return products

def get_product(key):
    key = (str(key[0]), str(key[1]))
    if key in products.keys():
        return products[key]
    else:
        product = Product(key[0], key[1])
        products[key] = product
        return product

def add_product(product_id, service, user):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    price = get_product((product_id, service)).price
    cursor.execute(f"""INSERT OR IGNORE INTO Products
                       (productNo, service, targetPrice)
                       VALUES ("{product_id}", "{service}", "{price}")
                    """)
    cursor.execute(f"""INSERT OR IGNORE INTO Users
                       VALUES ("{user}")
                    """)
    cursor.execute(f"""INSERT OR IGNORE INTO isWatching
                       VALUES ("{user}", "{product_id}", "{service}")
                    """)
    connection.commit()
    connection.close()
def user_ids():
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM Users")
    users = [user[0] for user in cursor.fetchall()]
    connection.close()
    return users

def products_of_user(user):
    ids = product_ids_by_user(user)
    products = [get_product(id) for id in ids]
    return products

def target_price(product_id, service):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    cursor.execute(f"""SELECT targetPrice
                       FROM Products
                       WHERE productNo="{product_id}" AND service="{service}"
                    """)
    price = cursor.fetchone()
    connection.close()
    if price is None:
        return price
    else:
        return price[0]

def change_target_price(product_id, service, new_target):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    cursor.execute(f"""UPDATE Products
                       SET targetPrice={new_target}
                       WHERE productNo="{product_id}" AND service="{service}"
                    """)
    connection.commit()
    connection.close()

while True:
    # Handle new messages
    message = bot.next_message()
    if message:
        chat_id = message["chat"]["id"]
        content = message["text"]
        if content.startswith("/add"):
            url = content.split()[1]
            try:
                service = [service for service in services.keys() if services[service]["url"] in content][0]
                is_not_product = lambda x: x != "product"
                product_id = list(itertools.dropwhile(is_not_product, url.split("/")))[1]
                if set(product_id).issubset(string.digits):
                    add_product(product_id, service, chat_id)
                else:
                    raise ValueError("Link is invalid or not supported")
                product = get_product((product_id, service))
                bot.reply(message, f"[{product}]({product.url})")
            except ZeroDivisionError:
                bot.reply(message, "Something went wrong 🙊")
    # Check for price changes and notify users
    for user in user_ids():
        for product in products_of_user(user):
            target = Decimal(target_price(product.id, product.service))
            current_price = Decimal(product.fresh_data()["price"])
            if current_price != target:
                difference = target - current_price
                bot.send_message(user, f"Price changed ({difference}€): [{product}]({product.url})")
                change_target_price(product.id, product.service, current_price)
    time.sleep(0.02)

