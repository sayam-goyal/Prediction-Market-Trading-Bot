import json
from collections import Counter

games = {}
with open('data/NBA.json', 'r') as f:
    games = json.load(f)
price_history = {}
with open('data/price_history.json', 'r') as f:
    price_history = json.load(f)
data = {}
STOPLOSS = 0.3

win_probs = []
#Summarizing/Processing Data
for game in games.values():
    market = game["markets"][0]
    tokens = json.loads(market["clobTokenIds"])
    p1_history = price_history[tokens[0]]
    p2_history = price_history[tokens[1]]

    start = [p1_history[0]["p"], p2_history[0]["p"]]

    entry = {
        "gameDate": market["gameStartTime"],
        "teams": json.loads(market["outcomes"]),
        "start": start,
        "stoploss": False,
        "end": json.loads(market["outcomePrices"])
    }

    # Determine the better team and check for stoploss
    if start[0] > start[1]:
        win_probs.append(start[0])
        # Starting index is 7 (5 min pregame + 2 min buffer post start)
        stoploss = start[0] * (1-STOPLOSS)
        for e in p1_history[7:]:
            if e["p"] <= stoploss:
                entry["stoploss"] = True
                break
    else:
        win_probs.append(start[1])
        stoploss = start[1] * (1-STOPLOSS)
        for e in p2_history[7:]:
            if e["p"] <= stoploss:
                entry["stoploss"] = True
                break
    data[game["id"]] = entry

#Analyzing Summarized Data
stoploss_count = 0
won_games = 0
bottom = 0.60
top = 0.65
count = 0
for e in data.values():
    # if bottom <= e["start"][0] <= top or bottom <= e["start"][1] <= top:
    #     if e["stoploss"]:
    #         stoploss_count += 1

    #Don't count games that haven't ended yet
    if e["end"][0] != "1" and e["end"][0] != "0":
        continue 
    if bottom <= e["start"][0] <= top:
        if e["stoploss"]:
            stoploss_count += 1
        if e["end"][0] == "1":
            won_games += 1
        count += 1
    if bottom <= e["start"][1] <= top:
        if e["stoploss"]:
            stoploss_count += 1
        if e["end"][1] == "1":
            won_games += 1
        count += 1
print(f"Stoploss: {STOPLOSS}, Range:{bottom}-{top}")
print(f"stoploss: {stoploss_count}/{count}")
print(stoploss_count/count)
print(f"win: {won_games}/{count}")




#graph shit
# plt.hist(win_probs, bins='auto', color='blue', alpha=0.7, edgecolor='black')
# plt.xlabel('Number')
# plt.ylabel('Frequency')
# plt.title('Frequency Histogram')
# plt.grid(axis='y', linestyle='--', alpha=0.6)

# plt.show()

# # Show the graph
# plt.show()