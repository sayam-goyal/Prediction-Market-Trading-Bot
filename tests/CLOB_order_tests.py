from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs, ApiCreds, BalanceAllowanceParams, AssetType, OrderType, OpenOrderParams, TradeParams
from py_clob_client.order_builder.constants import BUY, SELL
from rate_limiter import RateLimiter

'''
General API Notes:
get balance allowance allows you to get current cash balance and check # of shares owned in a market
    - the number it gives is 10^6 larger than the actual value, so divide by 10^6
An order means an OPEN order
So get order gets all open orders

Get current positions:
https://data-api.polymarket.com/positions?user=0x9014C136eCFB9E839652Adf61E13739EB78b2571&sizeThreshold=.1&limit=50&offset=0&sortBy=CURRENT&sortDirection=DESC
user= proxy wallet key

Analyze Polymarket Data:
https://www.polymarketanalytics.com/
https://www.betmoar.fun/

For a collection of games: check the games where the favorite won at the end and graph the lowest % each of them hit during that game to see where to set stoploss


TODO's of today:
Scrape/Analyze NFL data
Fix stoploss code
Get started on web client
'''

host = "https://clob.polymarket.com"
gamma = "https://gamma-api.polymarket.com/" 

#Polygon Private Key 
key = "0x67fb6d4fd02b5b29a8d652eb873f43794032abf098c88fe159c8f5aa46fe35ec"
POLYMARKET_PROXY_ADDRESS = "0x9014C136eCFB9E839652Adf61E13739EB78b2571"

chain_id = POLYGON

### Initialization of a client that trades directly from an EOA
client = ClobClient(host, key=key, chain_id=chain_id, signature_type=1, funder=POLYMARKET_PROXY_ADDRESS)
creds = client.create_or_derive_api_creds()
client.set_api_creds(creds)


'Get trade history, look at docs for more params'
# resp = client.get_trades(
#     # TradeParams(
#     #     maker_address=client.get_address()
#     # ),
# )
# print(resp[0])


'Get current open orders, market param is not needed'
# resp = client.get_orders(
#         # OpenOrderParams(
#         #     market="0x2b1493a81ba1359189a2471de0e029139001c8bc17f0e3af6e45e4f35e45a592",
#         # )
#     )
# print(resp)

'Create a BUY Order (also works for sell)'
# order_args = OrderArgs(
#     price=0.56,
#     size=1,
#     side=BUY,
#     token_id="100343507737043506832347269316473363523057356300343606982662885138091663562954",
# )
# signed_order = client.create_order(order_args)

# ## GTC Order
# resp = client.post_order(signed_order, OrderType.GTC)
# print(resp)

'Get cash allowance (use diff assettype to get shares in a certain market, check github example get allowance for this)'
# collateral = client.get_balance_allowance(
#         params=BalanceAllowanceParams(asset_type=AssetType.COLLATERAL)
#     )
# print(collateral)