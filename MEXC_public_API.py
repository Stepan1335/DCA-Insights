import requests
import time
import json
import os
from datetime import datetime

# Функція для відправки запиту на API
def make_request(endpoint, params=None):
    base_url = "https://api.mexc.com"
    response = requests.get(base_url + endpoint, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Помилка запиту: {response.status_code}")
        return []

# Функція для перевірки наявності пари
def check_pair_exists(dca_coin, outcoin):
    endpoint = "/api/v3/exchangeInfo"
    data = make_request(endpoint)
    
    if data:
        symbols = data.get("symbols", [])
        for symbol in symbols:
            if symbol['symbol'] == f"{dca_coin}{outcoin}":
                return True
    return False

# Функція для отримання валідної пари
def find_valid_outcoin(dca_coin, outcoin):
    if outcoin in ['USDT', 'USDC'] and check_pair_exists(dca_coin, outcoin):
        return outcoin
    
    if check_pair_exists(dca_coin, outcoin):
        return outcoin
    
    for alternative in ['USDT', 'USDC']:
        if alternative != outcoin and check_pair_exists(dca_coin, alternative):
            return alternative
    
    return None

# Функція для отримання цін у визначених інтервалах
def get_price_and_volume(dca_coin, outcoin, start_time, end_time):
    endpoint = "/api/v3/klines"
    params = {
        "symbol": f"{dca_coin}{outcoin}",
        "interval": "1m",
        "startTime": start_time,
        "endTime": end_time
    }
    
    data = make_request(endpoint, params)
    if data:
        open_price = float(data[0][1])
        close_price = float(data[-1][4])
        max_price = max(float(candle[2]) for candle in data)
        min_price = min(float(candle[3]) for candle in data)
        volume = sum(float(candle[5]) for candle in data)
        
        interval_prices = [None] * 10
        if len(data) >= 10:
            step = len(data) // 10
            for i in range(10):
                interval_prices[i] = float(data[i * step][4])
        
        return open_price, close_price, max_price, min_price, volume, interval_prices
    
    return None, None, None, None, None, [None] * 10

# Функція для обробки повідомлень
def process_messages(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    counter = 0
    processed_messages = []

    for message in data:  # Обробляємо лише перші 100 повідомлень
        #if counter >= 100:
            #break

        dca_coin = message["DCA_coin"]
        outcoin = message["OutCoin"]
        date = message["date"]
        time_of_message = message["time"]
        timezone = message["timezone"]
        duration = message["duration"]
        
        # Визначаємо остаточну тривалість
        final_duration = max(duration, 15)  # Якщо duration < 15, то збільшуємо до 15
        
        valid_outcoin = find_valid_outcoin(dca_coin, outcoin)
        
        if valid_outcoin is None:
            print(f"Пара {dca_coin}/{outcoin} не існує на біржі.")
            processed_message = {**message, "open_price": None, "close_price": None,
                                "max_price": None, "min_price": None, "volume": None,
                                "found_outcoin": None, "final_duration": final_duration,
                                **{f"interval_price_{i+1}": None for i in range(10)}}
            processed_messages.append(processed_message)
            continue
        
        start_time_str = f"{date} {time_of_message} {timezone}"
        start_time = int(time.mktime(time.strptime(start_time_str, "%Y-%m-%d %H:%M:%S %z"))) * 1000
        end_time = start_time + (final_duration * 60 * 1000)
        
        open_price, close_price, max_price, min_price, volume, interval_prices = get_price_and_volume(dca_coin, valid_outcoin, start_time, end_time)
        
        processed_message = {**message, "open_price": open_price, "close_price": close_price,
                            "max_price": max_price, "min_price": min_price, "volume": volume,
                            "found_outcoin": valid_outcoin, "final_duration": final_duration,
                            **{f"interval_price_{i+1}": interval_prices[i] for i in range(10)}}
        processed_messages.append(processed_message)
    
    save_processed_messages(processed_messages)

# Функція для збереження результатів
def save_processed_messages(messages):
    folder_path = os.path.join(os.getcwd(), "data")
    os.makedirs(folder_path, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(folder_path, f"processed_messages_{timestamp}.json")
    
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(messages, file, indent=4)
    
    print(f"Оброблено і збережено {len(messages)} повідомлень у файл: {file_path}")

# Виконання коду
file_path = "messages/processed_messages_2025-02-12_09-26-40.json" 
process_messages(file_path)
