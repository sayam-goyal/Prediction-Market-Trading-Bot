from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs, ApiCreds, BalanceAllowanceParams, AssetType, OrderType, OpenOrderParams, TradeParams, MarketOrderArgs
from py_clob_client.order_builder.constants import BUY, SELL
import requests, json, time
'''
Loop:
Request for all current positions
Loop through positions we are checking for stop loss
Check if stop loss is hit
If so, set a market order that immediately sells everything
print out an update saying that this position was sold and at what loss
Wait 1 second

MUST TODO:
PNL Data currently being read from data-api link is very slow/outdated
Self-calculate PNL Data using CLOB api instead, and only use data-api to get positions
'''
clob = "https://clob.polymarket.com"
gamma = "https://gamma-api.polymarket.com/" 

#Polygon Private Key 
key = "0x67fb6d4fd02b5b29a8d652eb873f43794032abf098c88fe159c8f5aa46fe35ec"
POLYMARKET_PROXY_ADDRESS = "0x9014C136eCFB9E839652Adf61E13739EB78b2571"

### Initialization of a client that trades directly from an EOA
client = ClobClient(clob, key=key, chain_id=POLYGON, signature_type=1, funder=POLYMARKET_PROXY_ADDRESS)
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)

#Games we will be checking for stoploss
#{conditionId : stoploss percent (i.e 0.4)}
games = {}

def sell_all(token):
    #TODO: This method is very dangerous. It assumes all is sold at market price, but price might fall while placing order thus making order useless as new price is much lower.
    #Make this method more robust through checks to make sure the entire method is filled

    #get total amount held of current token
    total_held = int(client.get_balance_allowance(
        params=BalanceAllowanceParams(
            asset_type=AssetType.CONDITIONAL,
            token_id=token,
        )
    )['balance'])/(10**6)

    #get price to sell at
    #Getting best buy price cuz that sells now instead of waiting for an order, i take instead of make an order
    market_price = float(client.get(
        token, BUY
    )['price'])
    order_args = OrderArgs(
        price = market_price,
        size = total_held,
        side=SELL,
        token_id=token,
    )
    signed_order = client.create_order(order_args)

    ## GTC Order
    resp = client.post_order(signed_order, OrderType.GTC)
    print(resp)

def stoploss_check():
    while True:
        output = "Current PNL's: "
        #Get all open positions
        params = {
        'user':'0x9014C136eCFB9E839652Adf61E13739EB78b2571',
        'sizeThreshold':'.1',
        'limit':'50',
        'offset':'0',
        'sortBy':'CURRENT',
        'sortDirection':'DESC'
        }
        resp = requests.get("https://data-api.polymarket.com/positions", params=params)
        if resp.status_code != 200:
            print(f"Failed to retrieve data. Status code: {resp.status_code}")
            print("Response content:", resp.text)
            return
        resp = resp.json()
        for pos in resp:
            game = games.get(pos['conditionId'])
            if game != None:
                market_price = float(client.get_midpoint(pos['asset'], BUY)['price'])
                startPrice = float(pos['avgPrice'])
                percentPnl = (market_price-startPrice)/startPrice*100
                output += str(percentPnl) + ", "
                if percentPnl <= -1*game:
                    print(f"STOPLOSS IS HIT. SELLING POSITION IN {pos['title']}...")
                    sell_all(pos['asset'])
                    #remove game from check list
                    games[pos['conditionId']] = None
                    #TODO: make sell all function return status of sell (if it was succesful) and print that below
                    print("SOLD ALL.")
        print(output)
        time.sleep(2)



#Get all open positions
params = {
    'user':'0x9014C136eCFB9E839652Adf61E13739EB78b2571',
    'sizeThreshold':'.1',
    'limit':'50',
    'offset':'0',
    'sortBy':'CURRENT',
    'sortDirection':'DESC'
}
resp = requests.get("https://data-api.polymarket.com/positions", params=params)
if resp.status_code == 200:
    res = resp.json()
    count = 0
    for pos in res:
        print(f"{count}. {pos['title']}")
        count += 1
    ans = input("Enter game to stoploss: ")
    while int(ans) != -1:
        stop_percent = float(input("Enter stoploss % (0.4, 0.5, etc): "))*100
        games[res[int(ans)]['conditionId']] = stop_percent
        ans = input("Enter game to stoploss: ")
    #start stoploss program
    stoploss_check()

else:
    print(f"Failed to retrieve data. Status code: {resp.status_code}")
    print("Response content:", resp.text)