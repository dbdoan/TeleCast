# import asyncio
# import requests
import logging
import os
import sys

from clear import clean
from datetime import datetime
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, filters, MessageHandler

clean()

# ------------------------------------ #
# ------------------------------------ #
# Load environment variables
load_dotenv()

TG_BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('WEATHER_API_KEY')
if TG_BOT_TOKEN and API_KEY:
    print('Both tokens is set.')
elif TG_BOT_TOKEN and not (API_KEY):
    print("Only TG_BOT_TOKEN set")
else:
    print("Only WEATHER_API_KEY token set")
    sys.exit(1)

# ------------------------------------ #
# ------------------------------------ #
# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ------------------------------------ #
# ------------------------------------ #
def obtain_weather(zip):
    try:
        url = f'https://api.tomorrow.io/v4/weather/realtime?location={zip} US]&apikey={API_KEY}'
        response = requests.get(url, timeout=10)
        # Raise an HTTPError for bad responses
        response.raise_for_status()
        data = response.json()
        return data

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)


def iso_to_mdy(iso_time):
    # converting the iso-time format output by API to a date-time object
    iso_obj = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%SZ')

    # converting date-time object to desired format
    formatted_date = iso_obj.strftime("%m-%d-%Y %H:%M %p")

    return formatted_date

# ------------------------------------ #
# ------------------------------------ #
# Function to delete a message after a delay
# async def delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
#     await asyncio.sleep(delay)
#     try:
#         await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
#     except Exception as e:
#         logging.error(f"Error deleting message: {e}")

ZIPCODE = range(1)

# ------------------------------------ #
# ------------------------------------ #
# Function to escape text for MarkdownV2
def escape_markdown_v2(text: str) -> str:
    escape_chars = r'\*_`\[\]()~>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

# Example command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Welcome to Danny\'s Telegram weather bot!\nUse /getweather to get weather information in your area!')


# Example message handler
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("pong!")
    # asyncio.create_task(delete_message(context, update.message.chat_id, update.message.message_id, 3))
    # asyncio.create_task(delete_message(context, update.message.chat_id, message.message_id, 10))


async def start_getweather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("What is your zipcode?")
    return ZIPCODE


async def receive_zipcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    zipcode = update.message.text
    info = obtain_weather(zipcode)

    time = escape_markdown_v2(iso_to_mdy(info["data"]["time"]))

    location = info['location']['name']



    # await update.message.reply_text(f"Your ZIP code is {zipcode}.")
    await update.message.reply_text(f"__***Weather data as of {time} UTC***__:\n"
                                    "\n"
                                    f"***Location***: {location}",parse_mode="MarkdownV2")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled!")
    return ConversationHandler.END

# ------------------------------------ #
# ------------------------------------ #
if __name__ == '__main__':
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ping', ping))

    weather_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('getweather', start_getweather)], 
        states={
            ZIPCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_zipcode)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(weather_conv_handler)

    # Log bot startup
    logger.info("Bot started")

    # Run the bot
    application.run_polling()