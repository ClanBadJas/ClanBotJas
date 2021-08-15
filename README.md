# ClanBotJas.py
> Notice: This Discord bot has been written to fulfill specific functions in our community. It was never intended and prepared for multi-server environments and/or scalable deployments. It's a bot designed to run on one specific server. You are free to use and/or copy this bot, but we can not provide support.

ClanBotJas Discord Bot, based on discord.py version 1.7.3, is a simple, self-hosted, custom bot to implement automatic Voice Channel scaling, self-role TextChannel administration and some basic command functions. It has been written to combat Voice Channel management and the neverending battle of always having either too much or not enough Voice Channels available for your Discord members. It also changes the name of a Voice Channel to the activity of connected users, automatically showing the topic of the Voice Channel. The self-role funtionality allows users to add roles to themselves so they can (un)subscribe TextChannels to/from their client using a dedicated settings TextChannel.

## AutoScaler
The AutoScaler functionality of this bot keeps an eye on a specific Voice Channel Category in the Discord server and makes sure there is always an empty Voice Channel available to use. When a user joins an empty Voice Channel, the bot creates a new Voice Channel if other users want a seperate conversation. When users leave a Voice Channel, the extra Voice Channel will be removed automatically to get back to a single empty Voice Channel.
The AutoScaler functionality works on a clone Voice Channel basis, if the server is boosted and has access to higher quality bitrates make sure the first Voice Channel is configured to use the premium settings, all Voice Channels created by the AutoScaler will use these settings.

![AutoScaler](https://github.com/ClanBadJas/ClanBotJas/blob/main/docs/screenshots/AutoScaler.png)


## AutoRename
On top of the above AutoScaler functionality, the bot is also built to reflect the activity which has the majority amongst the users in the Voice Channel. For example, if three users are in a Voice Channel and two of them are playing the game Factorio, the channel name will change to "Factorio". In a 50-50 situation, a random user activity will be selected.
TBD (Not implemented yet): When all users disconnect, the Voice Channel name will automatically be reset to the default name specified in the `.env`.

![AutoRename](https://github.com/ClanBadJas/ClanBotJas/blob/main/docs/screenshots/AutoRename.png)

## TextChannel subscriptions (self-role)
Our community has created a fairly extensive list of TextChannels with specific subjects. To avoid clutter and allow users to see only what they want to see, the TextChannel subscription service has been created. When requested with the slash command `/rolebot add`, ClanBotJas creates a new TextChannel with the desired name and a corresponding Discord Server Role that is linked to the new TextChannel with `View` permissions. Please note all changes are being written to `menu.json` first and will only be visible in the Discord server after sending the slash command `/reload rolebot`.
After reloading the rolebot, the actual TextChannel and Role will be created and a new button with the TextChannel name will be added to the defined dedicated settings channel. Clicking this button will toggle grant/revoke the corresponding role and will show/hide the TextChannel for the user.

On start or reload, the rolebot will walk through `menu.json` and create any TextChannel plus Role combination that's not present in the Discord server. Existing entries will not be adjusted and are skipped to avoid destruction of manual configurations in the server. 

Slash commands to manage the rolebot:

`/rolebot add` - Add a new TextChannel and Role to the server.

`/rolebot delete` - Remove a TextChannel and Role from the server.

`/rolebot view` - View current `menu.json`, to make it active execute `/reload rolebot`.

![RoleBot](https://github.com/ClanBadJas/ClanBotJas/blob/main/docs/screenshots/RoleBot.png)

## Other Functions
The bot has a few basic commands which can be useful (functions and permissions can be set in the corresponding `<command>.js` file inside the `commands` folder).

`help` - Shows generic help or help for a specific command if specified as argument, can only be used with prefix in chat..

`say` - Makes the bot say your message and deletes the message with your command, can only be used with prefix in chat.

`/load` - Loads a newly added cog on the fly from the `cogs` folder.

`/reload` - Reloads an active cog.

`/unload` - Disable an active cog.

`/ping` - Simple ping command to see if the bot is still alive and what the latency is.

`/getid` - Retrieves the Discord UserID for people that don't have development mode turned on.

TBD (Not implemented yet): `purge <1-99>` - purges X amount of messages from the current channel, maximum 99 at a time.


## Installation

TBD
