#!/usr/bin/env python3

import sqlite3
import os
import sys

filename = "data.sqlite3"

if os.path.isfile(filename):
    answer = input("Database file already exists. Write 'yes' if you really mean to override it: ")
    if answer == "yes":
        os.remove(filename)
    else:
        print("Exiting")
        sys.exit()

print("Creating database")
connection = sqlite3.connect(filename)
cursor = connection.cursor()

cursor.execute("""CREATE TABLE Products (
                      productNo TEXT,
                      service TEXT,
                      targetPrice INTEGER,
                      PRIMARY KEY (productNo, service)
                  )""")
cursor.execute("""CREATE TABLE Users (
                      chatID TEXT PRIMARY KEY
                  )""")
cursor.execute("""CREATE TABLE IsWatching (
                      user TEXT,
                      product TEXT,
                      service TEXT,
                      FOREIGN KEY (user) REFERENCES Users(chatID),
                      FOREIGN KEY (product) REFERENCES Products(productNo)
                      FOREIGN KEY (service) REFERENCES Products(service)
                      PRIMARY KEY (user, product, service)
                  )""")
cursor.execute("""CREATE TABLE Prices (
            datetime TEXT,
            price INTEGER,
            product TEXT,
            service TEXT,
            FOREIGN KEY (product) REFERENCES Products(productNo),
            FOREIGN KEY (service) REFERENCES Products(service)
        )""")
print("Database created.")

