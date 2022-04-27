import websocket, json, requests, time, threading
import pandas as pd

# ----------------------------------------------------- MAIN -----------------------------------------------------

def main():
    # INITIALIZE DATA
    initialize()

    # WEBSOCKET THREAD
    thread1 = threading.Thread(target=websocket_dataflow)

    # POSITION THREAD
    thread2 = threading.Thread(target=position_payload)

    # STARTS THREADS
    thread1.start()
    thread2.start()

# ----------------------------------------------------- GLOBAL -----------------------------------------------------

# DATA
stock = []
stock_filtered = []
stock_ordered = {}
stock_data = {}
orders = {}

# KEYS
API_KEY = 'PKNWDZT640Q786J4Q3ZP'
API_SECRET_KEY = 'CnHr41rc62hIzxh27bqrSBLnq1kZa3yENBg1BKp4'
SUB = "sip"

# TRADING URLS
BASE_TRADE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = "{}/v2/account".format(BASE_TRADE_URL)
ORDERS_URL = "{}/v2/orders".format(BASE_TRADE_URL)
POSITIONS_URL = "{}/v2/positions".format(BASE_TRADE_URL)
HEADERS = {'APCA-API-KEY-ID': API_KEY, 'APCA-API-SECRET-KEY': API_SECRET_KEY}

# DATA URLS
BASE_DATA_URL = "https://data.alpaca.markets/v2/stocks/snapshots?symbols="
CLOCK_URL = "https://api.alpaca.markets/v2/clock"

# ----------------------------------------------------- INITIALIZE -----------------------------------------------------

def initialize():
    # STOCK LIST SETUP (S&P 500 LIST)
    sp_500_ticker = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    sp_500_ticker = sp_500_ticker[0]
    stock = sp_500_ticker['Symbol'].values.tolist()
    symbol_string = ""
    for symbol in stock:
        symbol_string = symbol_string + symbol + ","
    symbol_string = symbol_string[0:len(symbol_string)-1]
    DATA_URL = BASE_DATA_URL + symbol_string

    # DATA REQUEST
    request = requests.get(DATA_URL, headers=HEADERS)
    data = request.json()

    # BOUNDS + DICT SETUP
    for key in data:
        if (data[key] != None): 
            stock_data[key] = {}
            stock_data[key]["current_price"] = ""
            delta = (data[key]["prevDailyBar"]["h"] - data[key]["prevDailyBar"]["l"]) / 2
            stock_data[key]["current_bar"] = [data[key]["dailyBar"]["l"], data[key]["dailyBar"]["h"]]
            stock_data[key]["bounds"] = [data[key]["prevDailyBar"]["l"] - delta, data[key]["prevDailyBar"]["h"] + delta]
            if (stock_data[key]["current_bar"][0] < stock_data[key]["bounds"][0] or stock_data[key]["current_bar"][1] > stock_data[key]["bounds"][1]):
                del stock_data[key]
            else:
                stock_filtered.append(key)

# ----------------------------------------------------- WEBSOCKET -----------------------------------------------------

def websocket_dataflow():

    # SOCKET LINK
    socket = "wss://stream.data.alpaca.markets/v2/" + SUB

    # SUBSCRIBE
    def on_open(ws):
        print("\nConnection sucess...", "\n")
        # AUTH
        message = {"action": "auth", "key": API_KEY, "secret": API_SECRET_KEY}
        ws.send(json.dumps(message))
        # MESSAGE TO SEND
        message = {"action":"subscribe", "bars":stock_filtered}
        ws.send(json.dumps(message))

    # PARSE DATA
    def on_message(ws, message):
        recieved = json.loads(message)
        for x in recieved:
            if (x["T"] == "b"):
                stock_data[x["S"]]["current_price"] = x["c"]
                #print(x["S"], " updated: ", stock_data[x["S"]], "\n")
                
    # ERROR
    def on_error(ws, message):
        print("Error: " + message, "\n")

    def on_close():
        print("Connection terminated...", "\n")

    # CONNECT TO SERVER
    ws = websocket.WebSocketApp(socket, on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.run_forever()

# ----------------------------------------------------- POSITION PAYLOAD -----------------------------------------------------

def position_payload():
    open_trades = 0
    while True:
        # RUNS EVERY 60 SEC
        time.sleep(60)

        # BUYS STOCK (SWAPPED THE IF STATEMENT </>)
        for stock in stock_data:
            if (stock_data[stock]["current_price"] != "" and not(stock in stock_ordered) and open_trades < 10):
                if (stock_data[stock]["current_price"] < stock_data[stock]["bounds"][0] and open_trades < 10):
                    short_order(stock)
                    open_trades += 1
                    print(open_trades)
                elif (stock_data[stock]["current_price"] > stock_data[stock]["bounds"][1] and open_trades < 10):
                    buy_order(stock)
                    open_trades += 1
                    print(open_trades)

        # UPDATES ORDERS
        update_orders()

        # SELLS STOCK
        for order in list(orders):
            if ((orders[order]["status"] == "new" or orders[order]["status"] == "filled" or orders[order]["status"] == "accepted")):
                print("order: ", order)
                if (time_to_sell(orders[order]["filled_at"])):
                    print("completed time_to_sell")
                    sell_position(orders[order]["symbol"])
                    del orders[order]
                    open_trades -= 1
                    print(open_trades)
                    
# COMPARE TIME

def time_to_sell(order_time):
    print("time_to_sell")
    request = requests.get(CLOCK_URL, headers=HEADERS)
    data = request.json()
    current_time = data['timestamp']
    order_time = order_time[11 : 16]
    current_time = current_time[11 : 16]
    print(current_time)
    print(order_time)
    difference = (int((int(current_time[0:2]) - int(order_time[0:2])) * 60) + int((int(current_time[3:5]) - int(order_time[3:5])))) + 240
    print(difference)
    return difference >= 30

# POSITIONS

def sell_position(symbol):
    url = POSITIONS_URL + "/" + symbol 
    r = requests.delete(url, headers=HEADERS)
    print("Position Sold: ", json.loads(r.content), "\n")

def sell_all_position():
    url = POSITIONS_URL + "?cancel_orders=true"
    r = requests.delete(url, headers=HEADERS)
    print("All Position Sold: ", json.loads(r.content), "\n")

# ORDERS
def buy_order(symbol):
    data = {
        "symbol": symbol,
        "notional": "10000.00",
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    order(data)


def short_order(symbol):
    qty = int(10000/stock_data[symbol]["current_price"])
    data = {
        "symbol": symbol,
        "qty": qty,
        "side": "sell",
        "type": "market",
        "time_in_force": "day"
    }
    order(data)

def order(data):
    stock_ordered[data["symbol"]] = True
    r = requests.post(ORDERS_URL, json=data, headers=HEADERS)
    print("Order Bought: ", json.loads(r.content), "\n")

def cancel_orders():
    r = requests.delete(ORDERS_URL, headers=HEADERS)
    print("Order Canceled: ", json.loads(r.content), "\n")

def update_orders():
    r = requests.get(ORDERS_URL, headers=HEADERS)
    data = json.loads(r.content)
    for order in data:
        orders[order['client_order_id']] = {"symbol":order['symbol'], "status": order['status'], "filled_at":order['created_at']}
    print("Updated Orders: ", orders, "\n")

# ----------------------------------------------------- RUN -----------------------------------------------------

if __name__ == "__main__":
    main()

# ---------------------------------------------------------------------------------------------------------------