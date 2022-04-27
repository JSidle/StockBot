import requests
import json
import time

#Alpaca API
BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_URL)
POSITIONS_URL = "{}/v2/positions".format(BASE_URL)
HEADERS = {'APCA-API-KEY-ID': 'PKSQG0IJIPYCYDCDEYAC', 'APCA-API-SECRET-KEY': 'Gz3iPu2dR95Y56Yi1yWBYcbvtDhZIOtjjWjH80lu'}
CLOSE_HEADERS = {'percentage': '100'}

# Gets account information
def get_account():
  r = requests.get(ACCOUNT_URL, headers=HEADERS)
  return json.loads(r.content)

#Creates a basic buy order
def create_order(symbol, qty, side, type, time_in_force):
  data = {
    "symbol": symbol,
    "qty": qty,
    "side": side,
    "type": type,
    "time_in_force": time_in_force
  }

  r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
  return json.loads(r.content)

#Returns a list of current orders
def get_orders():
  r = requests.get(ORDERS_URL, headers=HEADERS)
  return json.loads(r.content)

#Returns a list of current positions
def get_positions(symbol):
  r = requests.get(POSITIONS_URL + '/' + symbol,  headers=HEADERS)
  return json.loads(r.content)

def delete_position(symbol):
  r = requests.delete(POSITIONS_URL + '/' + symbol, headers=CLOSE_HEADERS)
  return json.loads(r.content)