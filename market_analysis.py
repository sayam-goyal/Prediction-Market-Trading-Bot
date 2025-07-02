'''
https://gamma-api.polymarket.com/markets?order=startDate
"outcomes": "["Yes", "No"]",
"outcomePrices": "["0", "1"]",
Loop through last 6 months of markets
Check 12 hrs before market end time if NO price >= 0.8, buy it
Add profit/loss to total
TODO-Stop loss, so like before market end if price drops below 0.6
'''

from py_clob_client.client import ClobClient
from datetime import datetime, timedelta
import requests, json, aiohttp, asyncio, time, ast, sys
from rate_limiter import RateLimiter
import matplotlib.pyplot as plt

START = time.monotonic()
host = "https://clob.polymarket.com/"
client = ClobClient(host)
gamma = "https://gamma-api.polymarket.com/" 
clob = "https://clob.polymarket.com/"

# iparams = {
#     "start_date_min": "2025-01-01",
#     "order" : "startDate",
#     "closed" : "true",
#     "limit" : "500",
#     #Tag ID 2 is for "Politics"
#     # "tag_id" : "2",
#     # "related_tags" : "true",
#     "offset" : "0",
# }
# #keep increasing offset by 500 until response data is empty, store all data in one giant variable
# offset = 0
# data = []
# while True:
#     iparams["offset"] = str(offset)
#     response = requests.get(gamma+"markets", params=iparams)
#     d = response.json()
#     if len(d) == 0:
#         break
#     for i in d:
#         if i.get("gameStartTime") is not None:
#             continue
#         data.append(i)
#     offset += 500
#     print(offset/500)
# #store data in a file
# print(len(data))
# with open("markets.json", "w") as f:
#     json.dump(data, f)

# sys.exit(0)

async def fetch(session, url, params={}):
    """Helper function to perform a GET request."""
    async with await session.get(url, params=params) as response:
        response.raise_for_status() # raises an exception if there was any status error on the get request
        return await response.json()  # Assuming JSON response

async def processMarket(session, market):
    global pnl, wins, losses, ct, totalInvested, stopFailCounter, history_data
    vol = market.get("volume")
    if vol is None or float(vol) < 10000:
        return  # Skip markets with volume less than 10,000
    #if no side wins
    noWins = ast.literal_eval(market["outcomePrices"])[1] == '1'
    
    end = market["closedTime"].split('.')[0].replace("+00", "")
    try:
        end = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Error parsing closedTime:", market["closedTime"])
        sys.exit(1)
    start = end - timedelta(hours=12)
    # try:
    #     volumes.append(float(market.get("volume")))
    # except TypeError:
    #     print("NO VOLUME")
    # fetches history data
    # history = await fetch(session, clob + "prices-history", params={
    #     "market" : ast.literal_eval(market["clobTokenIds"])[1],
    #     "startTs" : int(start.timestamp()),
    #     "endTs" : int(end.timestamp()),
    #     "fidelity" : "5",
    # })
    # history = history["history"]
    
    #used if fetching history data from file
    history = history_data.get(ast.literal_eval(market["clobTokenIds"])[1])

    #stores history data in dictionary (used when fetching from online):
    # history_data[ast.literal_eval(market["clobTokenIds"])[1]] = history

    half = int(len(history) * 0.5)
    # half = 0
    startPrice = history[half]["p"]
    #implenet increased investement if start price is higher
    lost = False
    invest = 100 + (startPrice - 0.7)*400
    stoploss = startPrice-0.05
    if startPrice >= 0.6 and startPrice <= 0.95:
        totalInvested += invest
        #start looping through history list starting from index half
        for i in range(half, len(history)):
            if history[i]['p'] <= stoploss:
                lost = True
                break
        if lost:
            if noWins:
                #stop loss hit, but no side won anyway
                stopFailCounter += 1
            losses += 1
            pnl -= invest - (invest/startPrice*stoploss)
        else:
            wins += 1
            pnl += (invest/startPrice) - invest
    ct += 1
    # if (ct%100==0):
    #     print(ct)
            

async def processMarkets(markets):
    global history_data
    tasks = []
    async with aiohttp.ClientSession() as session:
        session = RateLimiter(session)
        for market in markets:
            tasks.append(processMarket(session, market))
        await asyncio.gather(*tasks)

    #stores history data in a file
    # with open("history_data.json", "w") as f:
    #     json.dump(history_data, f)


pnl = 0
wins = 0
losses = 0
ct = 0
totalInvested = 0
#counts how many times stop loss was hit, but the side won anyway
stopFailCounter = 0
history_data = {}
# volumes = []
with open("history_data.json", "r") as f:
    history_data = json.load(f)
with open("markets.json", "r") as f:
    data = json.load(f)
asyncio.run(processMarkets(data))
print(f"PNL: {pnl:.2f}, %PNL: {(pnl/totalInvested):.2%}, Wins: {wins}, Losses: {losses}, Win Rate: {wins/(wins+losses):.2%}")
print(stopFailCounter)
# plt.hist(volumes, bins=5000, edgecolor='black')
# plt.show()