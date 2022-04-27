from requests.models import encode_multipart_formdata
from AlpacaAPI import *
from stockAPI import *
import datetime

openTrades = 0
pricePerStock = 10000
    
def main(): 
    global openTrades
    global pricePerStock
    while True:
        updatePrices()

        for x in range(len(ary)):
            price = float(prices[x])
            buyQuantity = (pricePerStock//price)
            if (prices[x] >= bounds[x][1] and openTrades < 10 and active[x] == False):
                print(ary[x] + " is above higher bound")
                create_order(ary[x], buyQuantity, "buy", "market", "gtc")
                openTrades =+ 1
                updateActives(ary[x], True)

            elif (prices[x] <= bounds[x][0] and openTrades < 10 and active[x] == False):
                print(ary[x] + " is below lower bound")
                create_order(ary[x], buyQuantity, "sell", "market", "gtc")
                openTrades =+ 1
                updateActives(ary[x], True)
            try:
                if (openTrades >= 1 and active[x] == True):
                    time_filled = get_positions(ary[x])[0]['filled_at'][0:19].replace("-", "/")
                    time_filled = time_filled.replace("T", " ")
                    date = datetime.datetime.strptime(time_filled, '%Y/%m/%d %H:%M').timestamp()
                    timezone_aware_dt = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
                    timezone_aware_dt = str(timezone_aware_dt)[0:16].replace("-", "/")
                    timezone_aware_dt = datetime.datetime.strptime(timezone_aware_dt, '%Y/%m/%d %H:%M').timestamp()
                    if (date - timezone_aware_dt >= 1800 and active[x] == True):
                        delete_position(ary[x])
                        updateActives(ary[x], False)
                        openTrades=- 1
            except:
                print(ary[x] + ": has no active positions")

        time.sleep(60)

updateBounds()
listActives()
main()