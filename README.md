# LeetCode Progress Bot

This bot is designed to keep track of a group's daily progress on LeetCode problems. Members of the group can declare their completion, and the bot will monitor this. Penalties are applied for missed days unless credits are available.

## Commands:

- **/start, /hello**: Start the bot and add your username to the group members.
- **/add @username**: Add a specified user to the group members list by mentioning them.
- **/add ME**: Add yourself to the group members list.
- **/members**: Show the list of all group members.
- **/daily**: Declare your daily LeetCode completion and see your current credits.
- **/username**: Check your current Telegram username.
- **/status**: Check your daily progress, penalties, and credits.
- **/clearCredits**: Clear your saved credits.
- **/help**: Display the list of commands.

## Credit System:

Members can earn up to three credits by declaring their LeetCode completion for three days consecutively. If a member misses a day, a credit will be used up instead of applying a penalty. If the member doesn't have any credits left, a $10 penalty will be applied.

Remember, consistency is key! Keep solving and keep learning.
