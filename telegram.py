#!/usr/bin/env python3

import time
import sys
import requests

api_prefix = "https://api.telegram.org/bot"

# Set directory path prefix. Current folder if none is given as argument.
if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = "./"

def read_token(file = "token.txt"):
    with open(path + file, "r") as tokenfile:
        return "".join(tokenfile.readlines()).strip().split("\n")[0]

def fetch_data(url, extra_parameters = {}):
    default_parameters = {"limit":1}
    parameters = default_parameters.copy()
    parameters.update(extra_parameters)
    while True:
        try:
            request = requests.get(url, params = parameters)
            break
        except requests.exceptions.RequestException as e:
            print("Error occured:")
            print(e)
            wait_time = 5
            print("Trying again in " + str(wait_time) + " seconds...")
            time.sleep(wait_time)

    return request.json()

class TelegramBot:
    def __init__(self, token = read_token()):
        self.load_token(token)
        self.offset = 0
    def load_token(self, token):
        self.token = token
        self.api = api_prefix + self.token + "/"
    def request(self, command, parameters):
        url = self.api + command
        return fetch_data(url, parameters)
    def message_content(self, response):
        return response["result"][0]["message"]
    def next_message(self):
        response = self.request("getUpdates", {"offset":self.offset})
        if bool(response["ok"]) and len(response["result"]) > 0:
            message = self.message_content(response)
            self.offset = int(response["result"][0]["update_id"]) + 1
            return message
        else:
            return None
    def send_message(self, chat, text):
        self.request("sendMessage", {"chat_id": chat,
                                     "text": text,
                                     "parse_mode": "markdown",
                                    })
    def reply(self, message, reply_text):
        self.send_message(message["chat"]["id"], reply_text)

