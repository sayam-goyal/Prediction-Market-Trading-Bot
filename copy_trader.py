'''
async or smth to run in parralel the acc tracker and the trade exec
check acc activity 5-10 times /sec
once trade is detected, check market and if:
buy trade: check if ask price is at the price what account bought at
sell trade: check if bid price is at the price what account sold at
if not, log the trade, what price we were able to have entered at
'''