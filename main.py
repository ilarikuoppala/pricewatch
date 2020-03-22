#!/usr/bin/env python3

import telegram
from product import Product
import string
import sqlite3
import time
import json
from decimal import Decimal
import itertools

bot = telegram.TelegramBot()
db_location = "data.sqlite3"
products = {}
with open("services.json", "r") as json_file:
    services = json.load(json_file)

def product_ids_by_user(user):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    cursor.execute("""SELECT product, service
                      FROM IsWatching
                      WHERE user=?
                   """, (user,))
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
    cursor.execute("""INSERT OR IGNORE INTO Products
                      (productNo, service, targetPrice)
                      VALUES (?, ?, ?)
                   """, (product_id, service, price))
    cursor.execute("""INSERT OR IGNORE INTO Users
                      VALUES (?)
                   """, (user,))
    cursor.execute("""INSERT OR IGNORE INTO IsWatching
                      VALUES (?, ?, ?)
                   """, (user, product_id, service))
    connection.commit()
    connection.close()

def remove_product(product_id, service, user):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    # Remove product from user's watchlist
    cursor.execute("""DELETE FROM IsWatching
                      WHERE product=? AND service=? AND user=?
                   """, (product_id, service, user))
    # Remove any products that no one is watching
    cursor.execute("""DELETE FROM Products
                      WHERE productNo NOT IN (
                          SELECT product
                          FROM IsWatching
                      )
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
    cursor.execute("""SELECT targetPrice
                      FROM Products
                      WHERE productNo=? AND service=?
                   """, (product_id, service))
    price = cursor.fetchone()
    connection.close()
    if price is None:
        return price
    else:
        return price[0]

def change_target_price(product_id, service, new_target):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    cursor.execute("""UPDATE Products
                      SET targetPrice=?
                      WHERE productNo=? AND service=?
                   """, (str(new_target), str(product_id), str(service)))
    connection.commit()
    connection.close()

def is_digits(input_string):
    return set(str(input_string)).issubset(string.digits)

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
                if services[service]["style"] == "product_no":
                    # Select the longest digits-only part of the url
                    product_id = max([part for part in url.split("/") if is_digits(part)])
                elif services[service]["style"] == "url":
                    # Select the url after the domain
                    not_domain = lambda x: service in x
                    parts = list(itertools.dropwhile(not_domain, url.split("/")))
                    product_id = "/".join(parts[1:])
                add_product(product_id, service, chat_id)
                product = get_product((product_id, service))
                bot.reply(message, f"Added {product.markdown()}")
            except:
                bot.reply(message, "Something went wrong 🙊")
        elif content.startswith("/delete"):
            product_list = products_of_user(chat_id)
            commands = "\n\n".join([f"Delete {p.markdown()}\nby clicking /rem{p.hash}" for p in product_list])
            bot.reply(message, commands)
        elif content.startswith("/rem"):
            # Take exactly 40 chars after first four
            sha1_sum = content[4:44]
            for product in products_of_user(chat_id):
                if product.hash == sha1_sum:
                    remove_product(product.id, product.service, chat_id)
                    bot.reply(message, f"Deleted {product.markdown()}")
                    break

    # Check for price changes and notify users
    for user in user_ids():
        for product in products_of_user(user):
            target = Decimal(target_price(product.id, product.service))
            current_price = Decimal(product.fresh_data()["price"])
            if current_price != target:
                difference = current_price - target
                bot.send_message(user, f"Price changed ({difference}€): {product.markdown()}")
                change_target_price(product.id, product.service, current_price)
    time.sleep(0.02)

