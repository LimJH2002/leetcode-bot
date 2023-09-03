# LeetCode Daily Checker Bot

This Telegram bot helps groups of friends stay motivated in their LeetCode challenges. Users declare their daily LeetCode completion, and the bot keeps track of progress, applying penalties for missed days, while rewarding consistent completion with credits.

## Features:
1. **User Addition**: New users can join by sending `/start` or `/hello`. Users can also add others or themselves using `/add @username` or `/add ME`.
2. **Daily Completion**: Users declare their daily LeetCode completion using `/daily`. Completing more than 3 dailies consecutively earns them credits.
3. **Penalties & Credits**: If a user misses a day, they get a $10 penalty. However, if they have credits (from consistent completion), a credit will be used instead of applying a penalty.
4. **Status Check**: Using `/status`, users can check their daily progress, penalties, and available credits.
5. **Group Overview**: `/members` provides a list of all group members, their penalties, and credits.

## Commands:
- `/start, /hello`: Greet the bot and get added to the group members.
- `/add @username`: Add a user to the group members by mentioning them.
- `/add ME`: Add yourself to the group members list.
- `/members`: Show all group members, their penalties, and credits.
- `/daily`: Declare your daily LeetCode completion and check your credits.
- `/username`: Check your current Telegram username.
- `/status`: Check your daily progress, penalties, and credits.
- `/help`: Display the available commands.

Stay motivated and happy coding!
