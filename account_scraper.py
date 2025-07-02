import requests
import json
from collections import defaultdict

def analyze_trade_data(all_trades):
    """
    Analyzes trade data to calculate P&L, entry/exit prices, and other stats per market.
    P&L accounts for held shares as $0 value (their cost is a loss).
    Filters out markets with no buy orders.

    Args:
        all_trades (list): A list of dictionaries, where each dictionary represents a trade.
    Returns:
        list: A list of dictionaries, where each dictionary contains summary
              statistics for a market (only for markets with at least one buy order).
    """
    if not isinstance(all_trades, list):
        print("Error: Input to analyze_trade_data must be a list of trade dictionaries.")
        return []

    markets = defaultdict(list)
    for trade in all_trades:
        if trade.get('type') == 'TRADE' and 'conditionId' in trade:
            markets[trade['conditionId']].append(trade)

    market_summaries = []

    for condition_id, trades_in_market in markets.items():
        if not trades_in_market:
            continue

        trades_in_market.sort(key=lambda x: x['timestamp'])

        held_shares_lots = []
        pnl_from_closed_trades = 0.0 # P&L from sales using FIFO cost
        
        all_buy_transactions_info = [] 
        all_sell_transactions_info = []

        market_title = trades_in_market[0].get('title', "Unknown Market")

        total_shares_ever_bought = 0.0
        total_cost_ever_spent = 0.0 # This is Sum(All Costs from Buys)
        total_shares_ever_sold = 0.0
        total_proceeds_ever_received = 0.0 # This is Sum(All Proceeds from Sells)
        
        first_entry_trade_details = None 
        last_exit_trade_details = None   

        for trade in trades_in_market:
            if not all(k in trade for k in ['size', 'usdcSize', 'price', 'side', 'timestamp']):
                continue

            trade_size = float(trade['size'])
            trade_usdc_size = float(trade['usdcSize'])
            trade_price = float(trade['price'])

            if trade['side'] == "BUY":
                held_shares_lots.append({
                    'size': trade_size,
                    'cost': trade_usdc_size, 
                    'price_per_share': trade_price 
                })
                all_buy_transactions_info.append(trade)
                total_shares_ever_bought += trade_size
                total_cost_ever_spent += trade_usdc_size
                if first_entry_trade_details is None: 
                    first_entry_trade_details = trade
            
            elif trade['side'] == "SELL":
                all_sell_transactions_info.append(trade)
                total_shares_ever_sold += trade_size
                total_proceeds_ever_received += trade_usdc_size
                last_exit_trade_details = trade 

                shares_to_sell_count = trade_size
                cost_of_shares_sold_this_tx = 0.0
                
                temp_held_lots = []
                for lot in held_shares_lots:
                    if shares_to_sell_count == 0:
                        temp_held_lots.append(lot)
                        continue

                    if lot['size'] <= shares_to_sell_count: 
                        cost_of_shares_sold_this_tx += lot['cost']
                        shares_to_sell_count -= lot['size']
                    else: 
                        if lot['size'] == 0: 
                           continue 
                        
                        cost_for_portion = (lot['cost'] / lot['size']) * shares_to_sell_count
                        cost_of_shares_sold_this_tx += cost_for_portion
                        
                        remaining_size_in_lot = lot['size'] - shares_to_sell_count
                        remaining_cost_in_lot = lot['cost'] - cost_for_portion
                        temp_held_lots.append({
                            'size': remaining_size_in_lot,
                            'cost': remaining_cost_in_lot,
                            'price_per_share': lot['price_per_share']
                        })
                        shares_to_sell_count = 0
                
                held_shares_lots = temp_held_lots
                pnl_from_closed_trades += (trade_usdc_size - cost_of_shares_sold_this_tx)

        # Only proceed if there were any buy transactions for this market
        if len(all_buy_transactions_info) > 0:
            avg_entry_price_all_buys = (total_cost_ever_spent / total_shares_ever_bought) if total_shares_ever_bought > 0 else 0.0
            avg_exit_price_all_sells = (total_proceeds_ever_received / total_shares_ever_sold) if total_shares_ever_sold > 0 else 0.0
            
            net_shares_currently_held = sum(lot['size'] for lot in held_shares_lots)
            cost_basis_of_held_shares = sum(lot['cost'] for lot in held_shares_lots)

            first_entry_price_market = first_entry_trade_details.get('price') if first_entry_trade_details else None
            last_exit_price_market = last_exit_trade_details.get('price') if last_exit_trade_details else None
            
            # Adjusted P&L: P&L from closed trades minus the cost of shares still held (now valued at $0)
            # This is equivalent to total_proceeds_ever_received - total_cost_ever_spent
            adjusted_pnl_final = pnl_from_closed_trades - cost_basis_of_held_shares
            # Alternative calculation for verification: adjusted_pnl_final = total_proceeds_ever_received - total_cost_ever_spent

            percent_adjusted_pnl = None
            if total_cost_ever_spent > 0: # Denominator is total cost of all buys
                percent_adjusted_pnl = (adjusted_pnl_final / total_cost_ever_spent) * 100.0
            elif adjusted_pnl_final == 0: # No cost from buys, no P&L
                percent_adjusted_pnl = 0.0
            # If total_cost_ever_spent is 0 and adjusted_pnl_final is non-zero, percent_adjusted_pnl remains None

            market_summaries.append({
                'market_title': market_title,
                'condition_id': condition_id,
                'adjusted_pnl': round(adjusted_pnl_final, 2), # Renamed for clarity in dict
                'percent_adjusted_pnl': round(percent_adjusted_pnl, 2) if percent_adjusted_pnl is not None else None, # Renamed
                'average_entry_price_all_buys': round(avg_entry_price_all_buys, 6) if avg_entry_price_all_buys else None,
                'average_exit_price_all_sells': round(avg_exit_price_all_sells, 6) if avg_exit_price_all_sells else None,
                'first_entry_price_in_market': first_entry_price_market,
                'last_exit_price_in_market': last_exit_price_market,
                'total_shares_bought': round(total_shares_ever_bought, 6),
                'total_usdc_spent_on_buys': round(total_cost_ever_spent, 2),
                'total_shares_sold': round(total_shares_ever_sold, 6),
                'total_usdc_received_from_sells': round(total_proceeds_ever_received, 2),
                'net_shares_currently_held': round(net_shares_currently_held, 6),
                'cost_basis_of_held_shares': round(cost_basis_of_held_shares, 2),
                'number_of_buy_trades': len(all_buy_transactions_info),
                'number_of_sell_trades': len(all_sell_transactions_info)
            })
            
    return market_summaries

def fetch_polymarket_activity(api_url):
    """
    Fetches activity data from the Polymarket API.
    """
    try:
        print(f"Fetching data from {api_url}...")
        response = requests.get(api_url)
        response.raise_for_status() 
        data = response.json()
        if not isinstance(data, list):
            print(f"Error: API did not return a list. Response type: {type(data)}")
            return None
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
        return None

# --- Main execution ---
if __name__ == "__main__":
    polymarket_api_url = "https://data-api.polymarket.com/activity?user=0x6cff25615924313a189d3bcd5ca99db452cdc3da&limit=500&offset=0"
    
    fetched_activities = fetch_polymarket_activity(polymarket_api_url)
    
    if fetched_activities:
        trade_data = [activity for activity in fetched_activities if activity.get('type') == 'TRADE']
        
        if not trade_data:
            print("No trade activities (type: 'TRADE') found in the fetched data.")
        else:
            print(f"Fetched {len(fetched_activities)} activities in total.")
            print(f"Processing {len(trade_data)} trade activities...")
            
            analysis_results = analyze_trade_data(trade_data)
            
            if analysis_results:
                print("\n📊 Trade Analysis Results (Markets with buy orders only):")
                for summary in analysis_results:
                    print(f"\n--- Market Summary: {summary['market_title']} (ID: {summary['condition_id']}) ---")
                    
                    final_pnl_val = summary['adjusted_pnl'] # Using the new key
                    print(f"  📈 P&L: ${final_pnl_val:.2f}")
                    
                    pnl_percentage_val = summary['percent_adjusted_pnl'] # Using the new key
                    total_buy_cost_val = summary['total_usdc_spent_on_buys']
                    
                    pnl_percentage_display = "N/A"
                    if pnl_percentage_val is not None:
                        pnl_percentage_display = f"{pnl_percentage_val:.2f}%"
                    elif final_pnl_val > 0 and total_buy_cost_val == 0:
                        pnl_percentage_display = "Infinite (Profit with $0.00 total buy cost)"
                    elif final_pnl_val < 0 and total_buy_cost_val == 0:
                         pnl_percentage_display = "Undefined (Loss with $0.00 total buy cost)"
                    
                    print(f"   % P&L: {pnl_percentage_display}")

                    print(f"  ➡️ Avg Entry Price (All Buys): ${summary['average_entry_price_all_buys']:.4f}" if summary['average_entry_price_all_buys'] is not None else "  ➡️ Average Entry Price (All Buys): N/A")
                    print(f"  ⬅️ Avg Exit Price (All Sells): ${summary['average_exit_price_all_sells']:.4f}" if summary['average_exit_price_all_sells'] is not None else "  ⬅️ Average Exit Price (All Sells): N/A")
                    print(f"  ▶️ First Entry Price: ${summary['first_entry_price_in_market']:.4f}" if summary['first_entry_price_in_market'] is not None else "  ▶️ First Entry Price in Market: N/A")
                    print(f"  ◀️ Last Exit Price: ${summary['last_exit_price_in_market']:.4f}" if summary['last_exit_price_in_market'] is not None else "  ◀️ Last Exit Price in Market: N/A")
                    print(f"  🛒 Total Shares Bought: {summary['total_shares_bought']:.4f} for ${summary['total_usdc_spent_on_buys']:.2f}")
                    print(f"  💰 Total Shares Sold: {summary['total_shares_sold']:.4f} for ${summary['total_usdc_received_from_sells']:.2f}")
                    print(f"  🏦 Net Shares Currently Held: {summary['net_shares_currently_held']:.4f}")
                    print(f"  🧾 Cost Basis of Held Shares: ${summary['cost_basis_of_held_shares']:.2f}") # Clarified label
                    print(f"  #️⃣  of Buy Trades: {summary['number_of_buy_trades']}")
                    print(f"  #️⃣  of Sell Trades: {summary['number_of_sell_trades']}")
                    print("----------------------------------------------------")
            else:
                print("Analysis completed. No markets with buy orders found or no valid trades to analyze.")
    else:
        print("Could not retrieve or process data from Polymarket API for analysis.")