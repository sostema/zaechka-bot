import logging
import os
import random
import sys
from threading import Thread

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

mode = os.getenv("MODE")
TOKEN = os.getenv("TOKEN")
freq = int(os.getenv("FREQ"))

random_good_replies = []
trigger_words = []
trigger_replies = []

if mode == "dev":

    def run(updater):
        updater.start_polling()
        updater.idle()

elif mode == "prod":

    def run(updater):
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        updater.bot.set_webhook(
            "https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN)
        )
        updater.idle()

else:
    logger.error("No MODE specified!")
    sys.exit(2)


def init_messages():
    global random_good_replies
    global trigger_words
    global trigger_replies
    with open("random_good_replies.txt", encoding="utf-8") as f:
        random_good_replies = f.read().split("; ")[0:-1]

    with open("trigger_words.txt", encoding="utf-8") as f:
        trigger_words = f.read().split("; ")[0:-1]

    with open("trigger_replies.txt", encoding="utf-8") as f:
        trigger_replies = f.read().split("; ")[0:-1]


def trigger_reply(update, context):
    if any(ext in update.message.text.lower() for ext in trigger_words):
        update.message.reply_text(random.choice(trigger_replies))
    else:
        good_reply(update, context)


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def good_reply(update, context):
    """Good replies for my beloved"""
    r = random.randint(1, 100)
    if r < int(freq):
        update.message.reply_text(random.choice(random_good_replies))


def welcome_handler(update, context):
    """Welcome new users"""
    for new_user_obj in update.message.new_chat_members:
        try:
            new_user = "@" + new_user_obj["username"]
        except Exception as e:
            new_user = new_user_obj["first_name"]

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=("Приветули, " + str(new_user)),
            parse_mode="HTML",
        )


def stop_and_kill():
    """Gracefully stop the Updater and replace the current process with a new one"""
    updater.stop()
    sys.exit(1)


def stop_and_restart():
    """Gracefully stop the Updater and replace the current process with a new one"""
    updater.stop()
    os.execl(sys.executable, sys.executable, *sys.argv)


def stop(update, context):
    update.message.reply_text("Bot is dying...")
    Thread(target=stop_and_kill).start()


def restart(update, context):
    update.message.reply_text("Bot is restarting...")
    Thread(target=stop_and_restart).start()


if __name__ == "__main__":
    logger.info("Starting bot")
    init_messages()
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(
        CommandHandler(
            "restart", restart, filters=Filters.user(username="@real_sostema")
        )
    )
    dp.add_handler(
        CommandHandler("kill", stop, filters=Filters.user(username="@real_sostema"))
    )
    dp.add_handler(
        MessageHandler(Filters.status_update.new_chat_members, welcome_handler)
    )
    dp.add_handler(
        MessageHandler((Filters.all & (~Filters.status_update)), trigger_reply)
    )

    dp.add_error_handler(error)

    run(updater)
