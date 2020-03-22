# pricewatch
A simple Telegram bot that will watch for price changes so you don't have to. My other motivators for this project are practicing of using database with python and using requests + beautifulsoup for crawling data from websites.
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
Please note the services currently supported: [services.json](/services.json).

## Support for services
This app is designed so that adding new services should be easy. Ideal case is that adding a service does not require changes in program code, but only in services.json configuration file. This requires that there is already at least one supported service that has similar way of showing product information.

## Feature requests and bugs
Please use Github issues.

