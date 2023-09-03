# LeetCode Daily Progress Telegram Bot

This bot helps groups track their daily LeetCode progress. Users can declare their daily completion, check their status, and incur penalties for missing their daily target.

## Features

1. **User Registration**: Users can be added to the tracking list either by interacting with the bot or by being added by another user using the `/add` command.
2. **Daily Progress Tracking**: Users can declare their daily LeetCode completion using the `/daily` command.
3. **Penalties**: At a specified time each day (currently set to 5am), the bot checks the progress of all registered users. Those who have not declared their daily completion incur a penalty.
4. **Status Checking**: Users can check their daily progress and total penalties using the `/status` command.

## Commands

- `/start`, `/hello`: Start the bot and add your username to the group members.
- `/add [username]` or `/add [@username]`: Add a specified username or mention to the group members list.
- `/members`: Show the list of all group members along with their penalties.
- `/daily`: Declare your daily LeetCode completion.
- `/username`: Check your current Telegram username.
- `/status`: Check your daily progress and penalties.
- `/help`: Display the list of available commands.

## Installation and Setup

1. Clone the repository.
2. Ensure you have all the required packages installed.
3. Set the `BOT_TOKEN` environment variable to your Telegram bot token.
4. Run the bot script.

