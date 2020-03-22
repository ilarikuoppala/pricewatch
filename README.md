# pricewatch
A simple Telegram bot that will watch for price changes so you don't have to.
## Setup
Create a virtual environment for python

    virtualenv -p python3 venv/
Start using the virtualenv and install packages
    
    source venv/bin/activate
    pip3 install -r requirements.txt
Create the database
    
    python3 createdatabase.py
Make a [Telegram bot](https://core.telegram.org/bots#3-how-do-i-create-a-bot)

## Usage
Change to virtualenv, if not already using it
    
    source venv/bin/activate
Run main.py
    
    python3 main.py

## Telegram interface
Adding an item to watchlist
    
    /add link_to_product
Please note the service(s) currently supported. They can be found in [services.json](/services.json).

## Feature requests and bugs
Please use issues.

