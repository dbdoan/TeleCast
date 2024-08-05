import asyncio
import logging
import os
import sys

from clear import clean
from datetime import datetime
from delete_message import delete_message
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
    print('Both tokens are set.')
elif TG_BOT_TOKEN and not API_KEY:
    print("Only TG_BOT_TOKEN is set")
else:
    print("Only WEATHER_API_KEY token is set")
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
# Data functions
def obtain_weather(zip):
    try:
        url = f'https://api.tomorrow.io/v4/weather/realtime?location={zip},US&apikey={API_KEY}'
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
    return None

def iso_to_mdy(iso_time):
    # converting the iso-time format output by API to a date-time object
    iso_obj = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%SZ')
    # converting date-time object to desired format
    formatted_date = iso_obj.strftime("%m-%d-%Y %H:%M %p")
    return formatted_date

# ------------------------------------ #
# ------------------------------------ #
# Global variables for conversation
ADDRESS_LINE_1, CITY, STATE, ZIPCODE = range(4)

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
    message = await update.message.reply_text("pong!")
    asyncio.create_task(delete_message(context, update.message.chat_id, update.message.message_id, 3))
    asyncio.create_task(delete_message(context, update.message.chat_id, message.message_id, 10))

async def start_getweather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Enter address line 1: ")
    return ADDRESS_LINE_1

async def receive_add_line_1(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    address_line_1 = update.message.text
    context.user_data['address_line_1'] = address_line_1

    await update.message.reply_text(f"Address Line 1 is set to: {address_line_1.title()}")
    await update.message.reply_text("Enter city: ")
    return CITY

async def receive_city(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    city = update.message.text
    context.user_data['city'] = city

    await update.message.reply_text(f"City is set to: {city.capitalize()}")
    await update.message.reply_text("Enter state (CA, TX, etc.): ")

    return STATE

async def receive_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    state = update.message.text
    context.user_data['state'] = state

    await update.message.reply_text(f"State is set to: {state.upper()}")
    await update.message.reply_text("Enter zipcode: ")

    return ZIPCODE

async def receive_zipcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    zipcode = update.message.text

    context.user_data['zipcode'] = zipcode
    address_line_1 = context.user_data.get('address_line_1', '')
    city = context.user_data.get('city', '')
    state = context.user_data.get('state', '')

    await update.message.reply_text(f"Zipcode is set to: {zipcode}")

    format_message = ("__*Here is your entered data*__\n"
                    f"Address Line 1: {address_line_1.title()}\n"
                    f"City: {city.capitalize()}\n"
                    f"State: {state.upper()}\n"
                    f"Zipcode: {zipcode}\n"
                    "\n"
                    "If anything is incorrect, you may correct entry by using /restart.\n"
                    "Otherwise, click /proceed to output the weather data in your area.")
    await update.message.reply_text(text=format_message, parse_mode="MarkdownV2")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled!")
    return ConversationHandler.END

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Restarting the process. Please enter address line 1:")
    return ADDRESS_LINE_1

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
            ADDRESS_LINE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add_line_1)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city)],
            STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_state)],
            ZIPCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_zipcode)],
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('restart', restart)]
    )

    application.add_handler(weather_conv_handler)

    # Log bot startup
    logger.info("Bot started")

    # Run the bot
    application.run_polling()
