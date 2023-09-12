from telegram.ext import Updater, CommandHandler
import os
import telebot
import threading
import time
from datetime import datetime
import pytz

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Initialize empty dictionaries for members and data
group_members = {}
daily_progress = {}
penalties = {}
credits = {}
daily_refresh_checked = {}

reminded = False

def ensure_directory_exists(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

# Functions to save and load chat IDs
def save_chat_id(chat_id):
    """Save new chat ID to chat_id.txt."""
    with open("chat_id.txt", "a") as f:
        f.write(f"{chat_id}\n")

def load_chat_ids():
    """Load all chat IDs from chat_id.txt."""
    try:
        with open("chat_id.txt", "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()
    
# Functions to save and load reminded chat IDs
def save_reminded_chat_id(chat_id):
    """Save chat ID to remind.txt after sending a reminder."""
    with open("remind.txt", "a") as f:
        f.write(f"{chat_id}\n")

def load_reminded_chat_ids():
    """Load all reminded chat IDs from remind.txt."""
    try:
        with open("remind.txt", "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()
    
def clear_reminded_chat_ids():
    """Clear all chat IDs from remind.txt."""
    with open("remind.txt", "w") as f:
        f.write("")

# Functions to handle saving and loading data
def save_members(chat_id, members):
    ensure_directory_exists(str(chat_id))
    with open(f"{chat_id}/members.txt", "w") as f:
        for member in members:
            f.write(f"{member}\n")

def load_members(chat_id):
    ensure_directory_exists(str(chat_id))
    try:
        with open(f"{chat_id}/members.txt", "r") as f:
            return set(line.strip() for line in f)
    except FileNotFoundError:
        return set()

def save_data(chat_id, daily_progress, penalties, credits):
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


def save_check_status(chat_id, status):
    with open(f"{chat_id}/check_status.txt", "w") as f:
        f.write(status)

def load_check_status(chat_id):
    try:
        with open(f"{chat_id}/check_status.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return "not_checked"


# Telebot command handlers
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id not in load_chat_ids():
        save_chat_id(chat_id)
    group_members = load_members(chat_id)
    
    user_name = message.from_user.username
    if user_name:
        group_members.add(user_name)
        save_members(chat_id)
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(commands=['status'])
def check_status(message):
    chat_id = message.chat.id
    if chat_id not in load_chat_ids():
        save_chat_id(chat_id)
    daily_progress, penalties, credits = load_data(chat_id)
    
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
    chat_id = message.chat.id
    if chat_id not in load_chat_ids():
        save_chat_id(chat_id)
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
    chat_id = message.chat.id
    if chat_id not in load_chat_ids():
        save_chat_id(chat_id)
    group_members[chat_id] = load_members(chat_id)
    try:
        member_name = message.text.split()[1]
        if member_name.upper() == "ME":
            member_name = message.from_user.username
        elif member_name in group_members[chat_id]:
            bot.reply_to(message, f"The user {member_name} is already in the list.")
            return
        elif not member_name.startswith('@'):
            bot.reply_to(message, "Please provide a valid member's Telegram username or mention starting with '@' or use 'ME' to add yourself.")
            return
        else:
            member_name = member_name[1:]
        group_members[chat_id].add(member_name)
        save_members(chat_id, group_members[chat_id])
        bot.send_message(message.chat.id, f"Added [{member_name}](tg://user?id={member_name}) to the group members list.", parse_mode='Markdown')
    except IndexError:
        bot.reply_to(message, "Please provide a member's Telegram username after the /add command.")
        

@bot.message_handler(commands=['daily'])
def daily_declaration(message):
    chat_id = message.chat.id
    if chat_id not in load_chat_ids():
        save_chat_id(chat_id)
    daily_progress[chat_id], penalties[chat_id], credits[chat_id] = load_data(chat_id)
    
    user_name = message.from_user.username
    if user_name:
        # If the user has already declared their daily completion
        if daily_progress[chat_id].get(user_name, False):
            credits[chat_id][user_name] = min(3, credits[chat_id].get(user_name, 0) + 1)
            if credits[chat_id][user_name] == 3:
                bot.reply_to(message, "You've already completed your daily LeetCode! You've also maxed out your credits at 3.")
            else:
                save_data(chat_id, daily_progress[chat_id], penalties[chat_id], credits[chat_id])
                bot.reply_to(message, f"You've already completed your daily LeetCode! You now have {credits[chat_id][user_name]} credits.")
            return
        
        # Mark the user's progress for the day as complete
        daily_progress[chat_id][user_name] = True
        save_data(chat_id, daily_progress[chat_id], penalties[chat_id], credits[chat_id])
        bot.reply_to(message, f"Your LeetCode completion for today has been recorded. Well done!")
    else:
        bot.reply_to(message, "Error: Couldn't retrieve your username. Please ensure you have a username set on Telegram.")

@bot.message_handler(commands=['members'])
def show_members(message):
    chat_id = message.chat.id
    if str(chat_id) not in load_chat_ids():
        save_chat_id(chat_id)
    group_members[chat_id] = load_members(chat_id)
    print(group_members[chat_id])
    daily_progress[chat_id], penalties[chat_id], credits[chat_id] = load_data(chat_id)
    
    if group_members[chat_id]:
        members_list = []
        for member in group_members[chat_id]:
            penalty = penalties[chat_id].get(member, 0)
            credit = credits[chat_id].get(member, 0)
            daily_status = "Completed" if daily_progress[chat_id].get(member, False) else "Not Completed"
            members_list.append(f"{member} - Daily: {daily_status} - Penalty: ${penalty} - Credits: {credit}")
        response = "Group members, daily status, penalties, and credits:\n" + '\n'.join(members_list)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "No members have been added yet.")


@bot.message_handler(commands=['username'])
def check_username(message):
    chat_id = message.chat.id
    if chat_id not in load_chat_ids():
        save_chat_id(chat_id)
    user_name = message.from_user.username
    if user_name:
        bot.reply_to(message, f"Your Telegram username is: @{user_name}")
    else:
        bot.reply_to(message, "Error: You don't have a username set on Telegram. Please set one in your Telegram settings.")

@bot.message_handler(commands=['clearCredits'])
def clear_credits(message):
    chat_id = message.chat.id
    if chat_id not in load_chat_ids():
        save_chat_id(chat_id)
    _, penalties[chat_id], credits[chat_id] = load_data(chat_id)

    user_name = message.from_user.username
    if user_name:
        if credits[chat_id].get(user_name, 0) == 0:
            bot.reply_to(message, "You have no credits to clear.")
        else:
            credits[chat_id][user_name] = 0
            save_data(chat_id, daily_progress[chat_id], penalties[chat_id], credits[chat_id])
            bot.reply_to(message, "Your credits have been cleared.")
    else:
        bot.reply_to(message, "Error: Couldn't retrieve your username. Please ensure you have a username set on Telegram.")

def check_time():
    while True:
        # Get the current time in GMT+8 timezone
        tz = pytz.timezone('Asia/Singapore')
        now = datetime.now(tz)
        reminded_chat_ids = load_reminded_chat_ids()

        #For Russell
        if (now.hour == 12 or now.hour == 15 or now.hour == 18 or now.hour == 21) and not reminded:
            reminded = True
            bot.send_message(1758860067, "Don’t overthink, lower your expectations")
            time.sleep(3660)
        
        if (now.hour == 13 or now.hour == 16 or now.hour == 19 or now.hour == 22) and reminded:
            reminded = False
            time.sleep(3660)

        for chat_id in load_chat_ids():
            people = ""
            group_members = load_members(chat_id)
            if now.hour == 23 and chat_id not in reminded_chat_ids:
                daily_progress[chat_id], _, _ = load_data(chat_id)
                for user in group_members:
                  if not daily_progress[chat_id].get(user, False):
                      people += f"@{user} "
                if (people != ""):
                  bot.send_message(chat_id, f"@{people}, remember to complete your daily LeetCode challenge!")
                save_reminded_chat_id(chat_id)
                time.sleep(60)  # Sleep for 60 seconds to avoid multiple reminders
        
            # At 5 AM GMT+8, check daily progress and update penalties or deduct credits
            elif now.hour >= 5 and now.minute >= 0 and load_check_status(chat_id) == "not_checked":
                daily_progress[chat_id], penalties[chat_id], credits[chat_id] = load_data(chat_id)
                for user in group_members:
                    if not daily_progress[chat_id].get(user, False):  # If the user hasn't marked their progress
                        if credits[chat_id].get(user, 0) > 0:  # If user has credits
                            credits[chat_id][user] -= 1  # Deduct a credit
                        else:
                            penalties[chat_id][user] = penalties[chat_id].get(user, 0) + 10  # Add $10 penalty
                daily_progress[chat_id].clear()  # Reset daily progress for the next day
                save_data(chat_id, daily_progress[chat_id], penalties[chat_id], credits[chat_id])

                # Prepare the list of members and their penalties
                members_list = []
                for member in group_members:
                    penalty = penalties[chat_id].get(member, 0)
                    members_list.append(f"{member} - Penalty: ${penalty}")
                response = "Checked daily LeetCode progress. Penalties have been updated or credits have been deducted!\n\nGroup members and penalties:\n" + '\n'.join(members_list)
            
                bot.send_message(chat_id, response)
                save_check_status(chat_id, "checked")  # Mark that we've checked progress for today.
                time.sleep(60)  # Sleep for 60 seconds to avoid multiple notifications
        
            # At 0 AM GMT+8, reset the flag for daily progress check
            elif now.hour == 4 and now.minute >= 30:
                print(now, "Resetting check status")
                save_check_status(chat_id, "not_checked")
                clear_reminded_chat_ids()
                time.sleep(60)
        
        time.sleep(60)  # Sleep for 10 seconds before checking again


if __name__ == "__main__":
    keep_alive()
    thread = threading.Thread(target=check_time)
    thread.start()
    bot.infinity_polling()