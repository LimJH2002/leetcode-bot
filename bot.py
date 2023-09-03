import os
from datetime import datetime


import telebot

BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, message.text)

def echo_all(message):
    now = datetime.now()
    if now.hour == 5 and now.minute == 0:
        # Do something specific at 5am
        bot.reply_to(message, "It's 5am! Time for something special!")
    else:
        bot.reply_to(message, message.text)


bot.infinity_polling()