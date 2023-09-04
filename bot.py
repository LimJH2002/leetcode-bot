import os
import telebot
import threading
import time
from datetime import datetime
import pytz
from keep_alive import keep_alive

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

def ensure_directory_exists(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

# Functions to handle saving and loading data
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

def save_data(chat_id):
    ensure_directory_exists(str(chat_id))
    with open(f"{chat_id}/daily_progress.txt", "w") as dp_file:
        for user, progress in daily_progress.items():
            dp_file.write(f"{user},{progress}\n")

    with open(f"{chat_id}/penalties.txt", "w") as pen_file:
        for user, penalty in penalties.items():
            pen_file.write(f"{user},{penalty}\n")
    
    with open(f"{chat_id}/credits.txt", "w") as cred_file:
        for user, credit in credits.items():
            cred_file.write(f"{user},{credit}\n")


def load_data(chat_id):
    ensure_directory_exists(str(chat_id))
    daily_progress = {}
    penalties = {}
    credits = {}

    try:
        with open(f"{chat_id}/daily_progress.txt", "r") as dp_file:
            for line in dp_file:
                user, progress = line.strip().split(',')
                daily_progress[user] = progress == 'True'
    except FileNotFoundError:
        pass

    try:
        with open(f"{chat_id}/penalties.txt", "r") as pen_file:
            for line in pen_file:
                user, penalty = line.strip().split(',')
                penalties[user] = int(penalty)
    except FileNotFoundError:
        pass

    try:
        with open(f"{chat_id}/credits.txt", "r") as cred_file:
            for line in cred_file:
                user, credit = line.strip().split(',')
                credits[user] = int(credit)
    except FileNotFoundError:
        pass

    return daily_progress, penalties, credits

# Load members and data on startup
group_members = load_members()
daily_progress, penalties, credits = load_data()

def save_check_status(status):
    with open("check_status.txt", "w") as f:
        f.write(status)

def load_check_status():
    try:
        with open("check_status.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "not_checked"


# Telebot command handlers
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
        credit = credits.get(user_name, 0)
        
        progress_status = "completed" if progress else "not completed"
        bot.reply_to(message, f"Your daily LeetCode progress: {progress_status}\nYour total penalties: ${penalty}\nYour available credits: {credit}")
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
    /daily - Declare your daily LeetCode completion and see your current credits.
    /username - Check your current Telegram username.
    /status - Check your daily progress, penalties, and credits.
    /clearCredits - Clear your saved credits.
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
            bot.reply_to(message, "Please provide a valid member's Telegram username or mention starting with '@' or use 'ME' to add yourself.")
            return
        else:
            # Remove the @ symbol
            member_name = member_name[1:]
        
        group_members.add(member_name)
        save_members()  # Save the updated list

        # Send a message mentioning the added user
        bot.send_message(message.chat.id, f"Added [{member_name}](tg://user?id={member_name}) to the group members list.", parse_mode='Markdown')
    except IndexError:
        bot.reply_to(message, "Please provide a member's Telegram username after the /add command.")

@bot.message_handler(commands=['daily'])
def daily_declaration(message):
    user_name = message.from_user.username
    if user_name:
        # If the user has already declared their daily completion
        if daily_progress.get(user_name, False):
            credits[user_name] = min(3, credits.get(user_name, 0) + 1)
            if credits[user_name] == 3:
                bot.reply_to(message, "You've already completed your daily LeetCode! You've also maxed out your credits at 3.")
                return
            else:
                save_data()
                bot.reply_to(message, f"You've already completed your daily LeetCode! You now have {credits[user_name]} credits.")
                return
        
        # Mark the user's progress for the day as complete
        daily_progress[user_name] = True
        current_credits = credits.get(user_name, 0)
        save_data()
        bot.reply_to(message, f"Your LeetCode completion for today has been recorded. Well done! You have {current_credits} credits.")
    else:
        bot.reply_to(message, "Error: Couldn't retrieve your username. Please ensure you have a username set on Telegram.")


@bot.message_handler(commands=['members'])
def show_members(message):
    if group_members:
        members_list = []
        for member in group_members:
            penalty = penalties.get(member, 0)
            credit = credits.get(member, 0)
            daily_status = "Completed" if daily_progress.get(member, False) else "Not Completed"
            members_list.append(f"{member} - Daily: {daily_status} - Penalty: ${penalty} - Credits: {credit}")
        response = "Group members, daily status, penalties, and credits:\n" + '\n'.join(members_list)
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

@bot.message_handler(commands=['clearCredits'])
def clear_credits(message):
    user_name = message.from_user.username
    if user_name:
        if credits.get(user_name, 0) == 0:
            bot.reply_to(message, "You have no credits to clear.")
        else:
            credits[user_name] = 0
            save_data()
            bot.reply_to(message, "Your credits have been cleared.")
    else:
        bot.reply_to(message, "Error: Couldn't retrieve your username. Please ensure you have a username set on Telegram.")


def check_time():
    daily_progress_checked = False  # This flag will help us ensure the daily progress is checked only once per day.
    while True:
        # Get the current time in GMT+8 timezone
        tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(tz)
        print(now)

        # At 1 PM GMT+8, remind users who haven't done their dailies
        if now.hour == 13 and now.minute <= 20:
            for user in group_members:
                if not daily_progress.get(user, False):
                    bot.send_message(-801071288, f"@{user}, remember to complete your daily LeetCode challenge!")
            time.sleep(3601)  # Sleep for 3600 seconds to avoid multiple reminders
        
        # At 5 AM GMT+8, check daily progress and update penalties, but only if it hasn't been checked for the day
        elif now.hour == 5 and now.minute == 0 and not daily_progress_checked:
            daily_progress_checked = True  # Mark that we've checked progress for today.
            for user in group_members:
                if not daily_progress.get(user, False):  # If the user hasn't marked their progress
                    penalties[user] = penalties.get(user, 0) + 10  # Add $10 penalty
            daily_progress.clear()  # Reset daily progress for the next day
            save_data()

            # Prepare the list of members and their penalties
            members_list = []
            for member in group_members:
                penalty = penalties.get(member, 0)
                members_list.append(f"{member} - Penalty: ${penalty}")
            response = "Checked daily LeetCode progress and penalties have been updated!\n\nGroup members and penalties:\n" + '\n'.join(members_list)
            
            bot.send_message(-801071288, response)
            time.sleep(60)  # Sleep for 60 seconds to avoid multiple notifications
        
        # At 0 AM GMT+8, reset the flag for daily progress check
        elif now.hour == 0 and now.minute == 0:
            daily_progress_checked = False
            time.sleep(60)
        
        else:
            time.sleep(60)  # Sleep for 10 seconds before checking again


keep_alive()
thread = threading.Thread(target=check_time)
thread.start()

bot.infinity_polling()
