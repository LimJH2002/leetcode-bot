import os
import telebot
import threading
import time
from datetime import datetime

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

def check_time():
    while True:
        now = datetime.now()
        if now.hour == 5 and now.minute == 0:
            # Do something specific at 5am
            print("It's 5am! Time for something special!")
            time.sleep(60)  # Sleep for 60 seconds to avoid multiple notifications
        else:
            time.sleep(10)  # Sleep for 10 seconds before checking again

thread = threading.Thread(target=check_time)
thread.start()

bot.infinity_polling()