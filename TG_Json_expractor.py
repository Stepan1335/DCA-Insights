import json
import re
import datetime

# Get the current date and time in the format YYYY-MM-DD_HH-MM-SS
current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Input file
INPUT_FILE = "messages/messages_2025-02-11_08-46-04.json"
# Create a new file name by appending the current date and time
OUTPUT_FILE = f"messages/processed_messages_{current_time}.json"

# Loading data
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to process values with K, M, or B suffixes
def convert_to_float(value_str):
    # Remove commas and spaces
    value_str = value_str.replace(',', '').strip()

    # Check for K, M, or B and multiply by corresponding values
    if 'K' in value_str:
        return float(value_str.replace('K', '').strip()) * 1000
    elif 'M' in value_str:
        return float(value_str.replace('M', '').strip()) * 1000000
    elif 'B' in value_str:
        return float(value_str.replace('B', '').strip()) * 1000000000
    else:
        # Try to convert to float after removing commas
        try:
            return float(value_str)
        except ValueError as e:
            raise ValueError(f"Failed to convert value '{value_str}' to a number. Error: {str(e)}")


# Function to process a single message
def process_message(entry):
    message = entry["message_text"]
    if not message:
        return None, "Message has no text"

    try:
        # Check for presence of important elements in the message
        if "$" not in message or "Route:" not in message:
            return None, "Missing '$' or 'Route:' in the text"

        # Determine position
        position = "short" if "Продает" in message else "long" if "Покупает" in message else "unknown"

        # Find the full fragment from "Покупает" or "Продает" to \n
        match_section = re.search(r"(Покупает|Продает)[^\n]*", message)

        buy_amount = None
        sell_amount = None
        sell_interval = None

        if match_section:
            section = match_section.group(0)  # Extracted fragment

            # Find all values with $ (assuming two numbers are given through |)
            amounts = re.findall(r"\$(\d+\.\d+[KM])", section)
            if len(amounts) >= 2:
                buy_amount = convert_to_float(amounts[0])  # First value
                sell_amount = convert_to_float(amounts[1])  # Second value

            # Find interval "every X seconds"
            interval_match = re.search(r"каждые\s(\d+)\sсек", section)
            if interval_match:
                sell_interval = int(interval_match.group(1))

        # Extract duration
        duration = 0  # Initial duration value

        # Find the entire fragment after "Продолжительность" to the first \n
        match_section = re.search(r"Продолжительность[^\n]*", message)

        if match_section:
            section = match_section.group(0)  # Extracted fragment

            # Find all numbers and their corresponding units (hours, minutes)
            matches = re.findall(r"(\d+)\s*([\w]+)", section)

            for number, unit in matches:
                number = int(number)  # Convert to number
                unit = unit.lower()  # Convert to lowercase

                if unit in ["часов", "hour", "hours", "h", "hs"]:  # Convert hours to minutes
                    duration += number * 60
                elif unit in ["минут", "minute", "minutes", "min", "mins"]:  # Add minutes
                    duration += number

        # Find the entire fragment starting from "Route:" and ending at \n
        route_match = re.search(r"Route:[^\n]*", message)

        DCA_coin = None
        OutCoin = None

        if route_match:
            section = route_match.group(0)  # Extract the whole line starting with "Route:"

            # Extract two currencies
            coin_match = re.findall(r"\$(\w+)", section)

            if len(coin_match) == 2:
                DCA_coin = coin_match[0]
                OutCoin = coin_match[1]

        # Extract MC, Liq, Price, VI1h, V-5m, V-1h
        mc = liq = price = vi1h = v_5m = v_1h = None
        mc_match = re.search(r"MC\s*:\s*\$([\d\.\,]+[KMB])", message)
        if mc_match:
            mc = convert_to_float(mc_match.group(1))
        liq_match = re.search(r"Liq\s*:\s*\$([\d\.\,]+[KMB])", message)
        if liq_match:
            liq = convert_to_float(liq_match.group(1))
        price_match = re.search(r"Price\s*:\s*\$([\d\.\,]+)", message)
        if price_match:
            price = convert_to_float(price_match.group(1))
        vi1h_match = re.search(r"VI1h\s*:\s*([\d\.\,]+)%", message)
        if vi1h_match:
            vi1h = convert_to_float(vi1h_match.group(1))
        v_5m_match = re.search(r"V-5m\s*:\s*\$([\d\.\,]+[KMB])", message)
        if v_5m_match:
            v_5m = convert_to_float(v_5m_match.group(1))
        v_1h_match = re.search(r"V-1h\s*:\s*\$([\d\.\,]+[KMB])", message)
        if v_1h_match:
            v_1h = convert_to_float(v_1h_match.group(1))

        # Extract MEXC
        mexc = 1 if "MEXC" in message else 0

        # Create processed_entry
        processed_entry = {
            "message_id": entry["message_id"],
            "date": entry["date"],
            "time": entry["time"],
            "timezone": entry["timezone"],
            "position": position,
            "buy_amount": buy_amount,
            "sell_amount": sell_amount,
            "sell_interval": sell_interval,
            "duration": duration,
            "DCA_coin": DCA_coin,
            "OutCoin": OutCoin,
            "MC": mc,
            "Liq": liq,
            "Price": price,
            "VI1h": vi1h,
            "V-5m": v_5m,
            "V-1h": v_1h,
            "MEXC": mexc,
            "original_message": message  # Add original message
        }

        return processed_entry, None

    except Exception as e:
        return None, str(e)

# Create list for processed messages
processed_data = []
failed_messages = []  # List for errors

for entry in data:
    processed_entry, error = process_message(entry)
    if processed_entry:
        processed_data.append(processed_entry)
    else:
        failed_messages.append({
            "message_id": entry["message_id"],
            "error": error,
            "message_text": entry["message_text"]
        })

# Save the result to a new file
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(processed_data, f, ensure_ascii=False, indent=4)

# Output error statistics
"""
print(f"Processed {len(processed_data)} messages.")
print(f"Failed to process {len(failed_messages)} messages. Reasons:")
for failed in failed_messages:
    print(f"ID: {failed['message_id']}, Error: {failed['error']}")   
print(f"Failed to process {len(failed_messages)} messages. Reasons:") 
"""
print(f"Processed {len(processed_data)} messages.")
print(f"Processed data has been successfully saved to file {OUTPUT_FILE}.")
