from dotenv import load_dotenv
import logging
import os
import sys
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

# Example command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! I am your bot.')

# Example message handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

if __name__ == '__main__':
    # Create the Application and pass it your bot's token
    application = ApplicationBuilder().token(TG_BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Log bot startup
    logger.info("Bot started")

    # Run the bot
    application.run_polling()