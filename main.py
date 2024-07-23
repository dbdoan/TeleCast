import asyncio
import requests
import logging
import os
import platform
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, filters, MessageHandler

# Clear console
if platform.system() == "Windows":
    os.system("cls")
else:
    os.system("clear")

# ------------------------------------ #
# ------------------------------------ #
# Load environment variables
load_dotenv()

TG_BOT_TOKEN = os.getenv('BOT_TOKEN')
if TG_BOT_TOKEN:
    print('Bot token is set.')
else:
    print("Bot token is not set.")
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
# Function to delete a message after a delay
# async def delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
#     await asyncio.sleep(delay)
#     try:
#         await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
#     except Exception as e:
#         logging.error(f"Error deleting message: {e}")


# Function to escape text for MarkdownV2
def escape_markdown_v2(text: str) -> str:
    escape_chars = r'\*_`\[\]()~>#+-=|{}.!'
    return ''.join(f'\\{c}' if c in escape_chars else c for c in text)

ZIPCODE = range(1)

# ------------------------------------ #
# ------------------------------------ #
# Example command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Welcome to Danny\'s Telegram weather bot!\nUse /getweather to get weather information in your area!')


# Example message handler
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("pong!")
    # asyncio.create_task(delete_message(context, update.message.chat_id, update.message.message_id, 3))
    # asyncio.create_task(delete_message(context, update.message.chat_id, message.message_id, 10))


async def start_getweather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("What is your zipcode?")
    return ZIPCODE


async def receive_zipcode(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    zipcode = update.message.text
    await update.message.reply_text(f"Your ZIP code is {zipcode}.")
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operation cancelled!")
    return ConversationHandler.END


# ------------------------------------ #
# ------------------------------------ #



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
