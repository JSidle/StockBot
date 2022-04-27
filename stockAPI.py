import requests
import json
import time

#Array declarations
ary = ["TSLA", "AAPL", "MSFT"]
prices = []
bounds = []
active = []
temp = ""

#Converts array to string for URL
for x in ary:
  temp = temp + x + ","
temp = temp[0:len(temp) - 1]

#URLs
url = "https://api.twelvedata.com/time_series?symbol=" + temp + "&interval=1min&apikey=d9679c0216da4627ab281952f2da1a85"
bounds_url = "https://api.twelvedata.com/time_series?symbol=" + temp + "&interval=1day&apikey=d9679c0216da4627ab281952f2da1a85"

#Update current prices
def updatePrices():
  api_result = requests.get(url)
  api_response = api_result.json()

  if (len(prices) == 0):
    for i in range(len(ary)):
      prices.append(float(api_response[ary[i]]['values'][0]['close']))
  else:
    prices.clear()
    for i in range(len(ary)):
      prices.append(float(api_response[ary[i]]['values'][0]['close']))
  
  print(prices)

#Update bounds array
def updateBounds():
  api_bounds_result = requests.get(bounds_url)
  api_bounds_response = api_bounds_result.json()
  for i in range(len(ary)):
    high = api_bounds_response[ary[i]]['values'][1]['high']
    low = api_bounds_response[ary[i]]['values'][1]['low']
    delta = (float(high) - float(low)) / 2
    bounds.append([float(low) - delta, float(high) + delta])

  print(bounds)

#Sets up active array
def listActives():
  for i in range(len(ary)):
    active.append(False)

#Updates active array
def updateActives(name, activated):
  if (activated == True):
    active[ary.index(name)] = True
  elif (activated == False):
    active[ary.index(name)] = False