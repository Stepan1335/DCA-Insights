import asyncio
import os
import json
from datetime import datetime
from telethon import TelegramClient
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

# API credentials (API_ID and API_HASH must be obtained from Telegram's developer portal)
api_id = int(os.getenv("API_ID"))  # Replace with your actual API ID
api_hash = os.getenv("API_HASH")  # Replace with your actual API Hash

# Channel or group from which to fetch messages
channel_identifier = -1002322080877  # Use ID or username

# User ID whose messages need to be fetched
target_user_id = 7679686095  # User ID

# Create a session for the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Function to save all messages to a JSON file
async def save_all_messages_to_json(channel_id_or_username, user_id):
    try:
        # Fetch the channel using get_entity
        entity = await client.get_entity(channel_id_or_username)

        # Create the folder if it doesn't exist
        folder_path = "messages"
        os.makedirs(folder_path, exist_ok=True)

        # Generate file name with current date and time
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"{folder_path}/messages_{current_time}.json"

        # Create a list to store the messages
        messages_data = []
        
        # Fetch messages
        messages = client.iter_messages(entity)
        count = 0
        total_count = 0  # Counter for all messages being checked

        # Collect messages from the user
        async for message in messages:
            total_count += 1
            if message.sender_id == user_id:
                count += 1
                # Check for message text and clean it of extra spaces
                message_text = message.text.strip() if message.text else "No text"
                
                # Get date and timezone information
                message_date = message.date.strftime("%Y-%m-%d")
                message_time = message.date.strftime("%H:%M:%S")
                timezone = message.date.strftime("%z")  # Timezone
                
                # Add message to the list
                messages_data.append({
                    "message_id": message.id,
                    "message_text": message_text,
                    "date": message_date,
                    "time": message_time,
                    "timezone": timezone if timezone else "UTC"
                })

            # Show progress
            if total_count % 100 == 0:  # Show progress every 100 messages processed
                print(f"Processed {total_count} messages...")

        # If messages were found, save them to a JSON file
        if messages_data:
            with open(file_name, 'w', encoding='utf-8') as json_file:
                json.dump(messages_data, json_file, ensure_ascii=False, indent=4)
            print(f"\n✅ Saved {count} messages to file: {file_name}")
        else:
            print(f"\n❌ No messages found from user with ID {user_id}")

    except ValueError as e:
        print(f"❌ Error: Invalid channel ID or username. {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Main function to run the script
async def main():
    await client.start()  # Start the client session
    await save_all_messages_to_json(channel_identifier, target_user_id)  # Fetch and save messages
    await client.disconnect()  # Disconnect after finishing

# Run the script
if __name__ == "__main__":
    asyncio.run(main())
