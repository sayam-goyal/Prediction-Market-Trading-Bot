"""
I know
How to get a market
How to turn market id into url (vice versa prolly ez as well)
how to get market price history
sort through markets 

I want to know
place orders
use websocket api to get realtime updates on price

ToDo
use matplot lib to plot live/historical price data more better than polymarket
calculate if market is over-reacting to event, if significantly below "true odds" invest and sell at true odds
backtesting strategies (aka a simulation of any bot i create using historical data)
liquidity bot to farm rewards
code a simple stop loss function that looks at all active positions and auto exits at a certian stop loss

step by step
get all nba games in the past couple of weeks (use gamma api)
    - use series_id=2 to sort for nba
    - use tag_id=745 to sort for nba
gamma api get event -> get market -> get conditionID -> get CLOB market -> get clob ID -> get price history for assigned range
set a function for proccessing each game
get game start time, and set end analyze time to 4 hours after
record before price, and after price
go through game by minute and check if price hits stop loss (for now set a hard stop at 20%)
record if stop loss was hit


aggregate all data into some structure
data to store (for now):
game name
teams
start price for each
stop loss hit on winning team?
ending result

questions to answer
what % of games where stop loss is hit end up still winning?
    - how do different starting odds affect this?
what % of games is stop loss hit at certain starting odds?

save structure
pull probabilites from data


api notes cuz polymarket docs is shit
when doing price-history query, it gets everything including startTs, up to minute before endTs
nba games from last year don't have a gameStartTime

TODOS
make this shit faster with async or smth bruh api calls are so slow
    - nvm turns out u get rate limited lmfao
    - figure out a way to make it faster but not too fast ig
analyze certain quarters
    - for example find out the odds of a team favorite to win the Q1, and if it's high just invest before and sell at Q1
analyze data for other stop losses
also download all the data next time so i dont have to fucking request it every time
    - one file for all price history (store by game ID)
    - store files for all NBA/NFL

findings so far:
overall this entire nba season, if you set a stop loss of 20% and invest in the team with better odds of winning, you will hit the stop loss 58% of the time
games with team favorite having before odds of 60-65, has a 71% chance of hitting stop loss, so bet on stop loss being hit (aka bet on underdog) and sell at 20%
"""

from py_clob_client.client import ClobClient
from datetime import datetime, timedelta
import requests, json, aiohttp, asyncio, time
from rate_limiter import RateLimiter

START = time.monotonic()
host = "https://clob.polymarket.com"
client = ClobClient(host)
gamma = "https://gamma-api.polymarket.com/" 
clob = "https://clob.polymarket.com/"
#Event ID:
# Name
# Start Price/Odds
# Stop Loss hit for winning team?
# Ending Winner
# #
data = {}
price_history = {}
games = {}

# Add a counter that will be updated each time a task completes
completed_tasks = 0
# Semaphore to ensure thread-safe access to the counter
counter_lock = asyncio.Lock()

async def fetch(session, url, id, params={}):
    """Helper function to perform a GET request."""
    # print(f"getting for task #{id}")
    async with await session.get(url, params=params) as response:
        response.raise_for_status() # raises an exception if there was any status error on the get request
        return await response.json()  # Assuming JSON response

async def processGameAsync(session, game, id):
    """Process game information asynchronously."""
    global completed_tasks
    eventID = game["id"]
    market = game["markets"][0]
    entry = {
        "name": game["title"],
        "gameDate": market["gameStartTime"],
        "teams": json.loads(market["outcomes"]),
        "start": [0, 0],
        "stoploss": False,
        "end": json.loads(market["outcomePrices"])
    }

    #add game to games file storing by ID (gamma event ID)
    games[game["id"]] = game
    
    tokens = json.loads(market["clobTokenIds"])
    start = datetime.fromisoformat(market["gameStartTime"]) - timedelta(minutes=5)
    end = int((start + timedelta(hours=4)).timestamp())
    start = int(start.timestamp())

    params = {
        "market": tokens[0],
        "startTs": start,
        "endTs": end,
        "fidelity": "1"
    }
    try:
        # Fetch price histories concurrently
        # p1_task = fetch_price_history(params, session)
        # p1_history = requests.get(f"{clob}prices-history", params=params).json()
        p1_history = await fetch(session, f"{clob}prices-history", id, params=params)
        params["market"] = tokens[1]
        p2_history = await fetch(session, f"{clob}prices-history", id, params=params)
        # p2_history = requests.get(f"{clob}prices-history", params=params).json()
        # p2_task = fetch_price_history(params, session)

        # p1_history, p2_history = await asyncio.gather(p1_task, p2_task)

        # Extract histories
        p1_history = p1_history["history"]
        p2_history = p2_history["history"]

        #store history in file
        price_history[tokens[0]] = p1_history
        price_history[tokens[1]] = p2_history

        
    except Exception as e:
        print(f"Error processing game {eventID}: {e}")
        return None
    
    async with counter_lock:
        completed_tasks += 1
        print(f"Completed {completed_tasks} tasks")


    # Record starting prices
    entry["start"] = [p1_history[0]["p"], p2_history[0]["p"]]

    # Determine the better team and check for stoploss
    if entry["start"][0] > entry["start"][1]:
        # Starting index is 7 (5 min pregame + 2 min buffer post start)
        stoploss = entry["start"][0] * 0.8
        for e in p1_history[7:]:
            if e["p"] <= stoploss:
                entry["stoploss"] = True
                break
    else:
        stoploss = entry["start"][1] * 0.8
        for e in p2_history[7:]:
            if e["p"] <= stoploss:
                entry["stoploss"] = True
                break
    # Save the processed entry
    data[eventID] = entry

async def processGames(games):
    tasks = []
    async with aiohttp.ClientSession() as session:
        session = RateLimiter(session)
        ct = 1
        for i in games:
            tasks.append(processGameAsync(session, i, ct))
            ct += 1
        results = await asyncio.gather(*tasks)

# Get all NBA games since the date given
iparams = {
    "series_id": "2",
    "start_date_min": "2024-09-01",
    "limit" : "10000"
}
response = requests.get(gamma+"events", params=iparams)


if response.status_code == 200:
    res = response.json()
    print(f"Total Games: {len(res)}")
    asyncio.run(processGames(res))
    with open('price_history.json', 'w') as f:
        json.dump(price_history, f)
    with open('NBA.json', 'w') as f:
        json.dump(games, f)

else:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    print("Response content:", response.text)



### Initialization of a client using a Polymarket Proxy associated with an Email/Magic account
# client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1, funder=POLYMARKET_PROXY_ADDRESS)

# ### Initialization of a client using a Polymarket Proxy associated with a Browser Wallet(Metamask, Coinbase Wallet, etc)
# client = ClobClient(host, key=key, chain_id=chain_id, signature_type=2, funder=POLYMARKET_PROXY_ADDRESS)