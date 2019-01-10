#!/usr/bin/python3
import discord
import asyncio
import sys

import logging
#https://discordpy.readthedocs.io/en/latest/logging.html

logging.basicConfig(filename="csclubbot.log", filemode="w", level=logging.DEBUG)
# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical error message')

EMBEDCOLOR_ERROR = 0xFF0000
EMBEDCOLOR_SUCCESS = 0x00FF00
EMBEDCOLOR_DEFAULT = 0x00006F


client = discord.Client()

command_sequence = "."
subscription_role_suffix = "*" #can only be one character/will only check first character
discord_bot_token = str(sys.argv[1])
server_name = "LOHS Computer Science Club"
bot_channel_name = "bot-spam"

@client.event
async def on_ready():
    #easter egg credit: https://github.com/nbd9/PastaBot/blob/0caeca8bdab8f9828f348024d4f4908696b166a0/src/main/java/utils/InterfaceListener.java#L15
    logging.info('Yo!')
    logging.info('His palms are sweaty, knees weak, arms are heavy!')
    logging.info("There's vomit on his sweater already, mom's spaghetti.")
    logging.info('Bot Ready.\n\n')
    logging.info("Name: " + client.user.name)
    logging.info("ID " + client.user.id)
    logging.info('------')
    logging.debug('Bot initialized with token: ' + discord_bot_token)






@client.event
async def on_message(message):

   if message.content.startswith(command_sequence):
        command = message.content.split(' ', 1 )[0]
        logging.debug("Command {} recieved".format(command))
        if command == command_sequence + "manage":

            await show_subscription_info(message)

        elif command == command_sequence + "list":

            await show_subscription_info(message)

        elif command == command_sequence + "toggle":

            await toggle_subscription(message)
        
        elif command == command_sequence + "help":

            await handle_help(message)
        else: 
            logging.info("Invalid Command Entered")


async def get_subscribeable_roles_for_server(server):
    roles = server.roles
    subscription_roles = []
    for role in roles:
        if role.name[-1] == subscription_role_suffix:
            # if should_lowercase:
            #     role.name = role.name.lower()#lowercase the name for detection later
            subscription_roles.append(role)

    return subscription_roles

async def check_for_spam_channel(message):
    if message.channel == discord.utils.get(client.get_all_channels(), name=bot_channel_name):
        return True
    else:
        return False


async def toggle_subscription(message):
    if await check_for_spam_channel(message):
        sub_roles = await get_subscribeable_roles_for_server(message.server)
        message_as_list = message.content.split(' ')

        if len(message_as_list) > 2:
            await send_error_message(message.channel, "You cannot toggle more than one subscription at once")
            return
        
        if not represents_int(message_as_list[1]):
            await send_error_message(message.channel, "Only integer subscription ID's are allowed.\nYou can find the ID by using **.list** or **.manage**")
            return

        selected_role_index = int(message_as_list[1])
        selected_role = sub_roles[selected_role_index]

        try:
                
            if selected_role in message.author.roles:
                #message author is already subscribed to role
                await client.remove_roles(message.author, selected_role)
                await send_success_message(message.channel, "You are now unsubscribed from **{}**".format(selected_role.name))

            else:
                await client.add_roles(message.author, selected_role)
                await send_success_message(message.channel, "You are now subscribed to **{}**".format(selected_role.name))
        except discord.errors.Forbidden:
            await send_error_message(message.channel, "Whoops. I cannot update your roles. Please make sure that I have the correct permissions and have a rank that is higher than the users you need me to serve.")



#https://stackoverflow.com/a/1267145
def represents_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


async def show_subscription_info(message):
    if await check_for_spam_channel(message):
        sub_roles = await get_subscribeable_roles_for_server(message.server)

        response_content = ""
        index = 0

        for role in sub_roles:
            if role in message.author.roles:
                response_content += "{}. **{}**".format(index, await cleanup_role_name(role.name))
            else:
                response_content += "{}. {}".format(index, await cleanup_role_name(role.name))

            response_content += "\n"
            index += 1

        response_content += "\n\n You are already subscribed to roles listed in **bold**"
        response_content += "\n To change a subscription, please use **.toggle** followed by"


        await send_embed_message(message.channel,
                "Subscription Status for {}".format(message.author.display_name),
                response_content)


async def handle_help(message):
    if await check_for_spam_channel(message):
        help_msg = '''
        Here are the commands you can use:
        **.manage**, **.list** - Show a summary of your subscription options 
        **.toggle [subscription number]** - Toggle your subscription status on or off for subscription number given
        **.help** - Display this help menu
        '''
        await send_embed_message(message.channel, "Help", help_msg)
    # else:
    #     await client.send_message(message.channel, "Please use the bot-spam channel to talk to me")


async def send_embed_message(msg_channel, msg_title, message, color=EMBEDCOLOR_DEFAULT):
    em = discord.Embed(title=msg_title, description=message, colour=color)
    # em.set_author(name='Someone', icon_url=client.user.default_avatar_url)
    await client.send_message(msg_channel, embed=em)

async def send_error_message(msg_channel, message):
    await send_embed_message(msg_channel, "Error:", message, EMBEDCOLOR_ERROR)

async def send_success_message(msg_channel, message):
    await send_embed_message(msg_channel, "Success!", message, EMBEDCOLOR_SUCCESS)

async def cleanup_role_name(name):
    return name[:-len(subscription_role_suffix)]#.lower()

# discord.on_member_join(member)
# discord.on_member_remove(member)

#client.run(discord_bot_token)

#network blip resilience https://stackoverflow.com/a/49082260
def run_client(client, *args, **kwargs):
    loop = asyncio.get_event_loop()
    while True:
        try:
            loop.run_until_complete(client.start(*args, **kwargs))
        except Exception as e:
            logging.error("Error", e)  # or use proper logging
        logging.info("Waiting until restart")
        time.sleep(600)

run_client(client, discord_bot_token)

