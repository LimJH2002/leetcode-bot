import os
import telebot
import threading
import time
from datetime import datetime

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

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

def save_data():
    with open("daily_progress.txt", "w") as dp_file:
        for user, progress in daily_progress.items():
            dp_file.write(f"{user},{progress}\n")

    with open("penalties.txt", "w") as pen_file:
        for user, penalty in penalties.items():
            pen_file.write(f"{user},{penalty}\n")

def load_data():
    daily_progress = {}
    penalties = {}

    try:
        with open("daily_progress.txt", "r") as dp_file:
            for line in dp_file:
                user, progress = line.strip().split(',')
                daily_progress[user] = progress == 'True'
    except FileNotFoundError:
        pass

    try:
        with open("penalties.txt", "r") as pen_file:
            for line in pen_file:
                user, penalty = line.strip().split(',')
                penalties[user] = int(penalty)
    except FileNotFoundError:
        pass

    return daily_progress, penalties

group_members = load_members()
daily_progress, penalties = load_data()

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    user_name = message.from_user.username
    if user_name:
        group_members.add(user_name)
        save_members()
    bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(commands=['status'])
def check_status(message):
    user_name = message.from_user.username
    if user_name:
        progress = daily_progress.get(user_name, False)
        penalty = penalties.get(user_name, 0)
        
        progress_status = "completed" if progress else "not completed"
        bot.reply_to(message, f"Your daily LeetCode progress: {progress_status}\nYour total penalties: ${penalty}")
    else:
        bot.reply_to(message, "Error: Couldn't retrieve your username. Please ensure you have a username set on Telegram.")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Here are the commands you can use:
    /start, /hello - Start the bot and add your username to the group members.
    /add @username - Add a specified user to the group members list by mentioning them. 
    /add ME - Add yourself to the group members list.
    /members - Show the list of all group members.
    /daily - Declare your daily LeetCode completion.
    /username - Check your current Telegram username.
    /status - Check your daily progress and penalties.
    /help - Display this help text.
    """
    bot.send_message(message.chat.id, help_text)




@bot.message_handler(commands=['add'])
def add_member(message):
    try:
        member_name = message.text.split()[1]  # Extract the member name after the '/add' command

        # If the user inputs "ME", use their own username
        if member_name.upper() == "ME":
            member_name = message.from_user.username

        # Check if the member is already in the list
        elif member_name in group_members:
            bot.reply_to(message, f"The user {member_name} is already in the list.")
            return
        
        # If the input doesn't start with '@' and isn't "ME", reject it
        elif not member_name.startswith('@'):
            bot.reply_to(message, "Please provide a valid member name or mention starting with '@' or use 'ME' to add yourself.")
            return
        else:
            # Remove the @ symbol
            member_name = member_name[1:]
        
        group_members.add(member_name)
        save_members()  # Save the updated list

        # Send a message mentioning the added user
        bot.send_message(message.chat.id, f"Added [{member_name}](tg://user?id={member_name}) to the group members list.", parse_mode='Markdown')
    except IndexError:
        bot.reply_to(message, "Please provide a member name after the /add command.")


    
@bot.message_handler(commands=['daily'])
def daily_declaration(message):
    user_name = message.from_user.username
    if user_name:
        daily_progress[user_name] = True  # Mark the user's progress for the day as complete
        save_data()
        bot.reply_to(message, "Your LeetCode completion for today has been recorded. Well done!")
    else:
        bot.reply_to(message, "Error: Couldn't retrieve your username. Please ensure you have a username set on Telegram.")

@bot.message_handler(commands=['members'])
def show_members(message):
    if group_members:
        members_list = []
        for member in group_members:
            penalty = penalties.get(member, 0)
            members_list.append(f"{member} - Penalty: ${penalty}")
        response = "Group members and penalties:\n" + '\n'.join(members_list)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "No members have been added yet.")


@bot.message_handler(commands=['username'])
def check_username(message):
    user_name = message.from_user.username
    if user_name:
        bot.reply_to(message, f"Your Telegram username is: @{user_name}")
    else:
        bot.reply_to(message, "Error: You don't have a username set on Telegram. Please set one in your Telegram settings.")


def check_time():
    while True:
        now = datetime.now()
        if now.hour >= 5 and now.minute >= 0:
            for user in group_members:
                if not daily_progress.get(user, False):  # If the user hasn't marked their progress
                    penalties[user] = penalties.get(user, 0) + 10  # Add $10 penalty
            daily_progress.clear()  # Reset daily progress for the next day
            save_data()
            bot.send_message(-801071288, "Checked daily LeetCode progress and penalties have been updated!")
            time.sleep(30)  # Sleep for 60 seconds to avoid multiple notifications
        else:
            time.sleep(10)  # Sleep for 10 seconds before checking again

thread = threading.Thread(target=check_time)
thread.start()

bot.infinity_polling()
