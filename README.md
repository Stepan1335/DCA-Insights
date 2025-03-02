# DCA Meme Coin Trading Analysis

## Project Overview

In this project, we aim to analyze the profitability of DCA (Dollar-Cost Averaging) strategies applied to meme coins in Telegram channels. The core hypothesis is that despite being executed by bots, these strategies may influence the prices of low-cap meme coins due to their low liquidity.

The objective is to determine whether DCA strategies are profitable by observing how prices change over time, identifying key parameters that affect price fluctuations, and eventually creating a model to filter good trading signals. If successful, this can lead to the development of an automated trading bot.

## Goal of the Project

The main goals of this project are:

1. **Validate Hypothesis**: Test if DCA bots have an impact on meme coin prices, especially those with low liquidity.
2. **Identify Key Parameters**: Find the most influential factors affecting price changes and how they relate to buy/sell signals.
3. **Model Creation**: Develop a model that filters good trading signals to improve DCA strategies.
4. **Automated Trading Bot**: Build a bot that trades meme coins based on the identified good signals.

## Data Collection and Structure

### 1. Telegram Data:
The first part of the project involves gathering data from Telegram channels. We use the following fields from parsed messages:

- **message_id**: Unique ID for each message.
- **date, time, timezone**: Timestamp information for the message.
- **position**: The position of the signal in the sequence.
- **buy_amount**: Total amount of money for buying/selling the token.
- **sell_amount**: Portion of **buy_amount** used at each interval.
- **sell_interval**: Time interval at which **sell_amount** is spent.
- **duration**: Duration for which the strategy is active.
- **DCA_coin**: Coin being bought.
- **OutCoin**: Coin used for selling.
- **MC, Liq**: Market cap and liquidity of the coin.
- **Price**: Coin price at the time of the signal.
- **VI1h, V-5m, V-1h**: Market volatility indicators.
- **MEXC**: Data source from the MEXC exchange.
- **original_message**: The original message text.

### 2. Price Data from MEXC:
We fetch price data for the specified coins on the MEXC exchange, including:

- **open_price, close_price**: Opening and closing price during the period.
- **max_price, min_price**: Highest and lowest price during the period.
- **volume**: Trading volume during the period.
- **interval_price_1 to interval_price_10**: Price at ten intervals during the period.

### 3. Additional Considerations:
- **found_outcoin**: If **OutCoin** is not suitable for trading, search for trading pairs with USDC or USDT.
- **final_duration**: Adjust the analysis period to at least 15 minutes if the original duration is too short.

## Data Analysis Steps

### 1. Data Cleaning:
- Remove rows with missing or corrupted data.

### 2. Data Enrichment:
Calculate the following to better understand price dynamics:
- **pct_change_close_price**: Percentage change from the signal to the closing price.
- **pct_change_interval_price_1 to pct_change_interval_price_10**: Price changes at each interval.
- **pct_change_max_price**: Percentage increase from the signal to the maximum price.
- **pct_change_min_price**: Percentage decrease from the signal to the minimum price.

### 3. Data Analysis:
- Merge Telegram trading signals with MEXC price data.
- Analyze price movements following DCA signals to assess their impact.
- Identify trends, patterns, and correlations between signal types and market behavior.
- Visualize the results to evaluate the effectiveness of the DCA strategy in real-world scenarios.

## Files

1. **TG_Bot_messages_in_channel_parser.py**: This file connects to the specified Telegram channel and parses messages containing DCA trading signals. It stores the parsed messages in a JSON format.

2. **TG_Json_expractor.py**: Extracts necessary information from the parsed messages using regular expressions and stores them in a structured JSON format.

3. **MEXC_public_API.py**: Fetches price data for the coins mentioned in the parsed messages from the MEXC exchange. It calculates price fluctuations over specified periods and stores the data for analysis.

4. **DCA_Strategy_Analysis.ipynb**: The Jupyter notebook where the data is analyzed. It includes cleaning, enrichment, and statistical analysis to determine the effectiveness of the DCA strategy.
