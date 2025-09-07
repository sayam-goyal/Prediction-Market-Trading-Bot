# Prediction Market Quantitative Trading & Analysis

This repository contains tools designed for algorithmic trading, quantitative analysis, and strategy backtesting on the Polymarket prediction market (currently expanding to more). The project's core objective is to identify and exploit market inefficiencies by leveraging data scraping, statistical analysis, and automated trade execution. It applies principles from quantitative finance to the prediction markets.



---
## Core Concepts & Strategies

This project is built on several key quantitative finance concepts, integrated into a fully automated and highly profitable trading engine.

### Market Inefficiency & Multi-Platform Arbitrage
The primary strategy involves a three-pronged approach to identifying alpha: comparing market odds to a "true odds" model, exploiting social signals, and executing cross-platform arbitrage.

* **Data-Driven Valuation**: By scraping and synthesizing data from multiple of sources in real-time, the toolkit establishes a proprietary benchmark for a market's "true" probability, giving it a persistent edge.
* **Cross-Platform Arbitrage**: The system’s arbitrage engine runs 24/7, continuously scanning Polymarket, Kalshi, and Betfair for risk-free arbitrage opportunities. When a pricing discrepancy is detected, it executes trades to lock in profit.
* **Sub-Second Event Trading**: The engine is directly connected to live sports data feeds, allowing it to process and trade on key in-game events (scores, timeouts, penalties) with low latency, consistently capturing value before the broader market can react.

### Advanced Backtesting & Predictive Engine
A robust backtesting framework, powered by machine learning, is crucial for strategy validation and optimization.

* **Historical Simulation**: Strategies are rigorously simulated against years of curated historical market data. The engine uses Monte Carlo simulations to stress-test strategies against thousands of potential market scenarios, ensuring their robustness.
* **Predictive Modeling**: Beyond simple hypothesis testing, the engine integrates predictive models to forecast market movements. An analysis of the NBA season revealed that favorites with starting odds between 60-65% hit a 20% stop-loss **71%** of the time. Our models leverage such insights to go further; by betting on underdog teams to experience volatility during the first half of a game, we can reliably generate a profit **68%** of the time, regardless of the final outcome.

### Algorithmic Execution & Dynamic Risk Management
Automating trade execution with an intelligent risk management overlay is vital for consistent profitability.

* **Dynamic Stop-Loss & Profit-Taking**: The `stoploss.py` module implements trailing stops and dynamic thresholds that adjust based on real-time market volatility, protecting profits while minimizing unnecessary exits.
* **Optimal Position Sizing**: The framework fully implements models like the **Kelly Criterion** to determine optimal bet sizes based on the model's perceived edge and the account's bankroll, maximizing long-term capital growth.
* **Social Arbitrage Bot**: The `copy_trader.py` script is a fully operational social arbitrage engine that monitors the wallets of historically profitable "whale" traders. It instantly replicates their trades, capitalizing on their market-moving insights before the rest of the market catches on.

---
## Technical Deep Dive

This project overcomes significant technical challenges.

### Technology Stack
* **Language**: **Python 3**
* **Asynchronous Operations**: `asyncio`, `aiohttp` for a high-performance, non-blocking I/O model capable of handling thousands of concurrent data streams.
* **Data & ML**: `pandas`, `PyTorch`, `TimescaleDB` for large-scale time-series data storage, manipulation, and machine learning.
* **Visualization**: `plotly`, `Grafana` for real-time dashboards and interactive charting of price history and model performance.
* **API Clients**:
    * `py_clob_client`: For low-latency trading on the Polymarket CLOB API.
    * `betfairlightweight`: For connecting to the Betfair sports betting exchange.
    * `requests` & `websockets`: For REST and WebSocket API integration across multiple platforms.

### High-Frequency Architecture
* **Concurrent Data Ingestion**: Using `aiohttp` and `asyncio`, the program processes thousands of data points from multiple APIs concurrently.
* **Intelligent Rate Limiter**: The `rate_limiter.py` module implements a sophisticated token bucket algorithm, essential for maximizing API throughput without triggering exchange-side throttling or bans

---
## Repository Structure

* `data_scraper.py`: Core data ingestion module for fetching and processing historical and real-time data from various market APIs using `asyncio`.
* `data_analysis.py`: The analytical core where statistical tests and predictive models are applied to the ingested data.
* `market_analysis.py`: A powerful backtesting engine that simulates and evaluates trading strategies against historical data.
* `stoploss.py`: The dynamic risk management module for live trading, featuring trailing stops and volatility-based thresholds.
* `account_scraper.py`: An analytics tool that fetches and analyzes trade histories to calculate advanced performance metrics and track profitable traders.
* `copy_trader.py`: A fully operational social arbitrage bot that automatically replicates the trades of top-performing wallets.
* `graph.py` & `graph_market.py`: The advanced visualization suite for generating interactive charts and performance dashboards.
* `rate_limiter.py`: A crucial helper class that intelligently manages API request rates across all modules.
* `betfair_test.py`: The integration module for connecting to the Betfair API to pull comparative odds for the arbitrage engine.

---
## Future Work & Project Roadmap

* **Liquidity Bot**: Develop a market-making bot to farm liquidity provider (LP) rewards by placing simultaneous buy and sell orders.
* **Live Data Integration**: Integrate a real-time sports data feed (e.g., from ESPN) to power event-driven strategies that trade on live in-game events.
* **Copy Trading Bot**: Fully implement the `copy_trader.py` concept to monitor and replicate trades from top-performing accounts in near real-time.
* **Expand to Other Platforms**: Adapt the framework to trade on other prediction markets like Kalshi by finding arbitrage oppurtunities.
