import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Clear console
os.system("clear")

# ------------------------------------ #
# ------------------------------------ #

load_dotenv()

TG_BOT_TOKEN = os.getenv('BOT_TOKEN')
if TG_BOT_TOKEN:
    print('Bot token is set.')
else:
    print("Bot token is not set.")
    sys.exit(1)  # Exit the script if the token is not set

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
async def delete_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        logging.error(f"Error deleting message: {e}")

# ------------------------------------ #
# ------------------------------------ #


# Example command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! Welcome to frognep\'s weather bot!')


# Example message handler
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = await update.message.reply_text("pong!")
    asyncio.create_task(delete_message(context, update.message.chat_id, update.message.message_id, 3))
    asyncio.create_task(delete_message(context, update.message.chat_id, message.message_id, 10))


# ------------------------------------ #
# ------------------------------------ #

if __name__ == '__main__':
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('ping', ping))

    # Log bot startup
    logger.info("Bot started")

    # Run the bot
    application.run_polling()