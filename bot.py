import os
import telebot
import threading
import time
from datetime import datetime

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)
bot.send_message(-801071288, "I'm alive!")

def save_members():
    with open("members.txt", "w") as f:
        for member in group_members:
            f.write(f"{member}\n")

def load_members():
    try:
        with open("members.txt", "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

group_members = load_members()

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    user_name = message.from_user.username
    if user_name:
        group_members.add(user_name)
        save_members()
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['add'])
def add_member(message):
    try:
        member_name = message.text.split()[1]  # Extract the member name after the '/add' command
        group_members.add(member_name)
        save_members()  # Save the updated list
        bot.reply_to(message, f"Added {member_name} to the group members list.")
    except IndexError:
        bot.reply_to(message, "Please provide a member name after the /add command.")
    
@bot.message_handler(commands=['members'])
def show_members(message):
    if group_members:
        members_list = '\n'.join(group_members)
        bot.send_message(message.chat.id, "Group members:\n" + members_list)
    else:
        bot.send_message(message.chat.id, "No members have been added yet.")

def check_time():
    while True:
        now = datetime.now()
        if now.hour == 17 and now.minute == 35:  # Adjust the time as needed
            bot.send_message(-801071288, "It's 5am! Time for something special!")
            time.sleep(60)  # Sleep for 60 seconds to avoid multiple notifications
        else:
            time.sleep(10)  # Sleep for 10 seconds before checking again

thread = threading.Thread(target=check_time)
thread.start()

bot.infinity_polling()
