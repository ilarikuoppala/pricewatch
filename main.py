#!/usr/bin/env python3

import telegram
import string
import sqlite3
import time
from decimal import Decimal
from pprint import pprint
import itertools
import datetime
from productgenerator import parse_product_url
import productgenerator

bot = telegram.TelegramBot()
db_location = "data.sqlite3"
products = {}

def execute_sql_statement(sql, arguments=None):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    if arguments is not None:
        cursor.execute(sql, arguments)
    else:
        cursor.execute(sql)
    results = cursor.fetchall()
    connection.close()
    return results

def product_ids_by_user(user):
    products = execute_sql_statement("""SELECT product, service
                      FROM IsWatching
                      WHERE user=?
                   """, (user,))
    return products

def get_product(key):
    key = (str(key[0]), str(key[1]))
    if key in products.keys():
        return products[key]
    else:
        product = productgenerator.get_product(key[0], key[1])
        products[key] = product
        return product

def add_product(product, user):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    product = get_product((product.id, product.service))
    price = product.price_in_cents
    cursor.execute("""INSERT OR IGNORE INTO Products
                      (productNo, service, targetPrice)
                      VALUES (?, ?, ?)
                   """, (product.id, product.service, price))
    cursor.execute("""INSERT OR IGNORE INTO Users
                      VALUES (?)
                   """, (user,))
    cursor.execute("""INSERT OR IGNORE INTO IsWatching
                      VALUES (?, ?, ?)
                   """, (user, product.id, product.service))
    connection.commit()
    connection.close()
    return product

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
    data = execute_sql_statement("SELECT * FROM Users")
    users = [user[0] for user in data]
    return users

def products_of_user(user):
    ids = product_ids_by_user(user)
    products = [get_product(id) for id in ids]
    return products

def target_price(product_id, service):
    price = execute_sql_statement("""SELECT targetPrice
                      FROM Products
                      WHERE productNo=? AND service=?
                   """, (product_id, service))[0]
    if price is None:
        return price
    else:
        return price[0]

def store_price(product_id, service, price):
    connection = sqlite3.connect(db_location)
    cursor = connection.cursor()
    cursor.execute("""
                INSERT INTO Prices
                VALUES (?, ?, ?, ?)
            """, (datetime.datetime.now().isoformat(), price, product_id, service))
    connection.commit()
    connection.close()

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
                product = parse_product_url(url)
                product = add_product(product, chat_id)
                store_price(product.id, product.service, product.price_in_cents)
                bot.reply(message, f"Added {product.markdown()}")
            except Exception as e:
                print(e)
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
        elif content.startswith("/list"):
            for product in products_of_user(chat_id):
                bot.reply(message, product.markdown())
        elif content.startswith("/start") or content.startswith("/help"):
            bot.reply(message, "Commands:\n /add link_to_product\n /delete\n /list")

    # Check for price changes and notify users
    for user in user_ids():
        for product in products_of_user(user):
            try:
                pprint(target_price(product.id, product.service))
                target = Decimal(target_price(product.id, product.service))
            except (TypeError, ValueError) as e:  # Skip updates if unable to get the price
                pprint(e)
            current_price = Decimal(product.fresh_data()["price_in_cents"])
            if current_price != target:
                store_price(product.id, product.service, current_price)
                difference = current_price - target
                bot.send_message(user, f"Price changed ({difference/100}€): {product.markdown()}")
                change_target_price(product.id, product.service, current_price)
    time.sleep(0.02)

