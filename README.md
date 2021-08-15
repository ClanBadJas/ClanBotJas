# ClanBotJas.py
> Notice: This Discord bot has been written to fulfill specific functions in our community. It was never intended and prepared for multi-server environments and/or scalable deployments. It's a bot designed to run on one specific server. You are free to use and/or copy this bot, but we can not provide support.

ClanBotJas Discord Bot, based on discord.py version 1.7.3, is a simple, self-hosted, custom bot to implement automatic Voice Channel scaling, self-role TextChannel administration and some basic command functions. It has been written to combat Voice Channel management and the neverending battle of always having either too much or not enough Voice Channels available for your Discord members. It also changes the name of a Voice Channel to the activity of connected users, automatically showing the topic of the Voice Channel. The self-role funtionality allows users to add roles to themselves so they can (un)subscribe TextChannels to/from their client using a dedicated settings TextChannel.

## AutoScaler
The AutoScaler functionality of this bot keeps an eye on a specific Voice Channel Category in the Discord server and makes sure there is always an empty Voice Channel available to use. When a user joins an empty Voice Channel, the bot creates a new Voice Channel if other users want a seperate conversation. When users leave a Voice Channel, the extra Voice Channel will be removed automatically to get back to a single empty Voice Channel.
The AutoScaler functionality works on a clone Voice Channel basis, if the server is boosted and has access to higher quality bitrates make sure the first Voice Channel is configured to use the premium settings, all Voice Channels created by the AutoScaler will use these settings.

![AutoScaler](https://github.com/ClanBadJas/ClanBotJas/blob/master/docs/screenshots/AutoScaler.png)


## AutoRename
On top of the above AutoScaler functionality, the bot is also built to reflect the activity which has the majority amongst the users in the Voice Channel. For example, if three users are in a Voice Channel and two of them are playing the game Factorio, the channel name will change to "Factorio". In a 50-50 situation, a random user activity will be selected.
TBD (Not implemented yet): When all users disconnect, the Voice Channel name will automatically be reset to the default name specified in the `.env`.

![AutoRename](https://github.com/ClanBadJas/ClanBotJas/blob/master/docs/screenshots/AutoRename.png)

## TextChannel subscriptions (self-role)
Our community has created a fairly extensive list of TextChannels with specific subjects. To avoid clutter and allow users to see only what they want to see, the TextChannel subscription service has been created. When requested with the slash command `/rolebot add`, ClanBotJas creates a new TextChannel with the desired name and a corresponding Discord Server Role that is linked to the new TextChannel with `View` permissions. Please note all changes are being written to `menu.json` first and will only be visible in the Discord server after sending the slash command `/reload rolebot`.
After reloading the rolebot, the actual TextChannel and Role will be created and a new button with the TextChannel name will be added to the defined dedicated settings channel. Clicking this button will toggle grant/revoke the corresponding role and will show/hide the TextChannel for the user.

On start or reload, the rolebot will walk through `menu.json` and create any TextChannel plus Role combination that's not present in the Discord server. Existing entries will not be adjusted and are skipped to avoid destruction of manual configurations in the server. 

Slash commands to manage the rolebot:

`/rolebot add` - Add a new TextChannel and Role to the server.

`/rolebot delete` - Remove a TextChannel and Role from the server.

`/rolebot view` - View current `menu.json`, to make it active execute `/reload rolebot`.

![RoleBot](https://github.com/ClanBadJas/ClanBotJas/blob/master/docs/screenshots/RoleBot.png)

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


## Installation and configuration
ClanBotJas can be run as standalone Python application, as a pre-built container or as a container built from source.
Please follow the guide by Discord to create your Discord Bot on the developer pages before following the steps below.
Make sure the bot has `Privileged Gateway Intents` enabled in the Discord developer environment.
Make sure the bot has the `Manage Channels` and `Manage Roles` permissions in the Discord server for the rolebot to function (don't forget the top level category permissions).
This bot uses two different channels as handlers, one: create a dedicated TextChannel for the bot to deploy the Role buttons, two: create a dedicated TextChannel for the bot to send logs to. The logs TextChannel can be hidden to people on the server, just make sure the bot has access.

### Run as standalone Python application
Make sure you have Python 3.9 or later installed on your system.
First `git clone` to the location you want to run the bot from.
cd into the `clanbotjas` folder and `pip install -r requirements.txt` to install the dependencies.
Configure the bot settings in `clanbotjas/settings/.env`, you can copy the `.env.example` to `.env` to make it easy, fill all the options with ID's from the Discord server.
If you already know what TextChannels and Roles you like to have, do the same for `menu.json` as what was just done for `.env` and edit it to fit the Discord server.
Now start the bot using `python cogmanager.py`

### Run as container
Running a container is quite easy, all that's required is a capable Docker host (including docker-compose) and a few files.
Get the `docker-compose.yml`, `.env.example` and the `menu.json.example` and save them somewhere.
Rename the `menu.json.example` to `menu.json`, edit the values and save it somewhere accessible.
Rename the `.env.example` to `.env` and edit the values to reflect the ID's of the Discord server.
Edit the `docker-compose.yml` to mount the folder with the `menu.json` to `clanbotjas/settings` for persistent storage.
Run `docker-compose up -d`

### Build the container from source
First `git clone` to the location you want to run the bot from.
Make sure to be in the root of the project.
Run `docker build -t <username>/<repository>:[version]` to build the container.
Now edit `docker-compose.yml` to reflect the built container image.
Follow the steps described above (Run as container)