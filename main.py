import asyncio
import logging
import os
import sys

from datetime import datetime
from delete_message import delete_message
from dotenv import load_dotenv
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler, ConversationHandler, filters, MessageHandler
from urllib.parse import quote
from weather_codes import weather_codes

# ------------------------------------ #
# Load environment variables
load_dotenv()

TG_BOT_TOKEN = os.getenv('BOT_TOKEN')
TOMORROW_IO_TOKEN = os.getenv('TOMORROW_TOKEN')
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')

# Check if all tokens are set
if not TG_BOT_TOKEN or not TOMORROW_IO_TOKEN or not MAPBOX_TOKEN:
    if not TG_BOT_TOKEN:
        print("BOT_TOKEN is not set")
    if not TOMORROW_IO_TOKEN:
        print("TOMORROW_TOKEN is not set")
    if not MAPBOX_TOKEN:
        print("MAPBOX_TOKEN is not set")
    sys.exit(1)
else:
    print('All tokens are set.')

# ------------------------------------ #
# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ------------------------------------ #
# Data functions
def user_location_img(longitude, latitude, MAPBOX_TOKEN):
    url = f'https://api.mapbox.com/styles/v1/mapbox/outdoors-v12/static/{longitude},{latitude},{16},0/{300}x{200}?access_token={MAPBOX_TOKEN}'
    return url

def extra_uv_info(uv_index):
    if uv_index >= 0 and uv_index <= 2:
        message = "Low UV levels, no sun protection needed."
    elif uv_index > 2 and uv_index <= 7:
        message = "Moderate to high UV levels, consider protecting your skin."
    elif uv_index > 7 and uv_index <= 9:
        message = "Very high UV levels, everyone should protect their skin."
    elif uv_index >= 11:
        message = "Extreme risk of harm, avoid outdoor activities and take precautions if you must go outside."
    return message

def obtain_status(code):
    return weather_codes["weatherCode"].get(str(code), "Unknown")

def obtain_weather(longitude, latitude):
    try:
        url = f'https://api.tomorrow.io/v4/weather/forecast?location={longitude},{latitude}&apikey={TOMORROW_IO_TOKEN}'
        response = requests.get(url, timeout=10)
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

def obtain_coordinates(address_line_1):
    try:
        url = f'https://api.mapbox.com/search/geocode/v6/forward?q={address_line_1}&proximity=ip&types=address&&access_token={MAPBOX_TOKEN}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        coordinates = (data['features'][0]['geometry']['coordinates'])
        return coordinates
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error: ", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Connection Error: ", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error: ", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong: ", err)

def iso_to_mdy(iso_time):
    iso_obj = datetime.strptime(iso_time, '%Y-%m-%dT%H:%M:%SZ')
    formatted_date = iso_obj.strftime("%m-%d-%Y %H:%M %p")
    return formatted_date

def c_to_f(celcius_temperature):
    converted_f = (9/5 * celcius_temperature) + 32
    return converted_f

# ------------------------------------ #
# Global variables for conversation
ADDRESS_LINE_1, CITY, STATE, ZIPCODE, CONFIRM = range(5)

# ------------------------------------ #
# Function to escape text for MarkdownV2
def escape_markdown_v2(text: str) -> str:
    escape_chars = r'\*_`\[\]()~>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Welcome to Danny\'s Telegram weather bot!\nUse /getweather to get weather information in your area!')

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("pong!")
    asyncio.create_task(delete_message(context, update.message.chat_id, update.message.message_id, 3))
    asyncio.create_task(delete_message(context, update.message.chat_id, message.message_id, 10))

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To reach out for inquiries or concerns:\nTelegram: @dbdoan_dev")

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
                      "If anything is incorrect, you may correct entry by using /restart\.\n"
                      "Otherwise, click Proceed to output the weather data in your area\.")
    
    keyboard = [
        [InlineKeyboardButton("Proceed", callback_data='proceed')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text=format_message, parse_mode="MarkdownV2", reply_markup=reply_markup)
    return CONFIRM

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message:
        await update.message.reply_text("Operation cancelled!")
    elif update.callback_query:
        await update.callback_query.message.reply_text("Operation cancelled!")
    context.user_data.clear()
    return ConversationHandler.END

async def proceed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    message = query.message
    address_line_1 = context.user_data.get('address_line_1', '')
    city = context.user_data.get('city', '')
    state = context.user_data.get('state', '')
    zipcode = context.user_data.get('zipcode', '')

    user_full_address = f"{address_line_1} {city} {state} {zipcode} United States"
    formatted_address = quote(user_full_address)

    user_coordinates = obtain_coordinates(formatted_address)
    if not user_coordinates:
        await message.reply_text("Failed to fetch coordinates data. Please try again later.", parse_mode="MarkdownV2")
        return ConversationHandler.END

    weather_data = obtain_weather(user_coordinates[1], user_coordinates[0])
    if not weather_data:
        await message.reply_text("Failed to fetch weather data. Please try again later.", parse_mode="MarkdownV2")
        return ConversationHandler.END

    iso_date_time = weather_data["timelines"]["minutely"][0]["time"]
    converted_date_time = iso_to_mdy(iso_date_time)
    markdown_date_time = escape_markdown_v2(converted_date_time)

    user_dewpoint_c = weather_data["timelines"]["minutely"][0]["values"]["dewPoint"]
    user_dewpoint_f = c_to_f(user_dewpoint_c)
    user_temperature_c = weather_data["timelines"]["minutely"][0]["values"]["temperature"]
    user_temperature_f = c_to_f(user_temperature_c)
    user_precipitation = weather_data["timelines"]["minutely"][0]["values"]["precipitationProbability"]
    user_status = weather_data["timelines"]["minutely"][0]["values"]["weatherCode"]
    user_uv = weather_data["timelines"]["minutely"][0]["values"]["uvIndex"]

    url = user_location_img(user_coordinates[0], user_coordinates[1], MAPBOX_TOKEN)
    response = requests.get(url)

    if user_coordinates:
        keyboard = [
            [InlineKeyboardButton("Yes, this is correct.", callback_data=f"yes_correct")],
            [InlineKeyboardButton("No, this is not correct.", callback_data=f"no_incorrect")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await message.reply_photo(photo=response.content, 
                                        caption=
                                        f"__*Weather data as of {markdown_date_time} UTC*__\n"
                                            "\n"
                                            f"🌤️ Condition: {obtain_status(user_status)}\n"
                                            f"☔ Chance of Rain: {str(user_precipitation)}%\n"
                                            f"💧 Dew Point: {escape_markdown_v2(str(user_dewpoint_c))}°C / {escape_markdown_v2(str(round(user_dewpoint_f, 2)))}°F\n"
                                            f"🌡️ Temperature: {escape_markdown_v2(str(user_temperature_c))}°C / {escape_markdown_v2(str(round(user_temperature_f, 2)))}°F\n"
                                            f"🕶️ UV Index: {user_uv}\n\n\({escape_markdown_v2(extra_uv_info(user_uv))}\)", 
                                            parse_mode="MarkdownV2", reply_markup=reply_markup)
    else:
        await message.reply_text("Failed to fetch coordinates data. Please try again later.", parse_mode="MarkdownV2")

    return await end_conversation(update, context)

async def end_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"Conversation ended after processing with user data: {context.user_data}")
    context.user_data.clear()
    return ConversationHandler.END

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'proceed':
        await proceed(update, context)
    elif query.data == 'yes_correct':
        await context.bot.send_message(chat_id=query.message.chat_id, text="I hope this bot helped you today 😎, use /getweather to use again.")
        return ConversationHandler.END
    elif query.data == 'no_incorrect':
        contact_button = InlineKeyboardButton(text="Contact me on Telegram ❤️", url="https://t.me/dbdoan_dev")
        reply_markup = InlineKeyboardMarkup([[contact_button]])

        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="I am sorry this bot did not meet your expectations. Please forward the error[s] to me so I can promptly fix the issue!",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

# ------------------------------------ #
if __name__ == '__main__':
    application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ping', ping))
    application.add_handler(CommandHandler('contact', contact))
    application.add_handler(CallbackQueryHandler(button_handler))

    weather_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('getweather', start_getweather)], 
        states={
            ADDRESS_LINE_1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_add_line_1)],
            CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_city)],
            STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_state)],
            ZIPCODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_zipcode)],
            CONFIRM: [CallbackQueryHandler(button_handler)]  
        },
        fallbacks=[CommandHandler('cancel', cancel), CommandHandler('restart', start_getweather), CommandHandler('getweather', start_getweather)]
    )

    application.add_handler(weather_conv_handler)

    logger.info("Bot started")
    application.run_polling()