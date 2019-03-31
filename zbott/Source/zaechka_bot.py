import logging
import random as rand
import os
import sys
from threading import Thread

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from main_core import TOKEN, good_words, welcome_words

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def welcome(update, context):
    """Echo the user message."""
    if any(ext in update.message.text.lower() for ext in welcome_words):
        logger.info('Greeted by ' + repr(update.message.from_user.id) + ' in ' + repr(update.message.chat_id))
        update.message.reply_text('Привет, дорогие!')

def good_reply(update, context):
    """Good replies for my beloved"""
    r = rand.randint(1, 100)
    if r < 4:
        update.message.reply_text(rand.choice(good_words))

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dp.add_handler(CommandHandler('restart', restart, Filters.user(user_id=260917779)))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, welcome))
    dp.add_handler(MessageHandler(Filters.all, good_reply))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()