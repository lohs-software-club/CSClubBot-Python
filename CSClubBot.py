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

    if await test_for_command(message.content, "test"):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1

        await client.edit_message(tmp, 'You have {} messages.'.format(counter))

    elif await test_for_command(message.content, "sleep"):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

    elif await test_for_command(message.content, "ispm"):
        await client.send_message(message.channel, str(message.channel.is_private))

    elif await test_for_command(message.content, "subscribe"):
        logging.info("subscribe command recieved")

        await handle_subscription(message, True)

    elif await test_for_command(message.content, "sub"):
        logging.info("sub command recieved")

        await handle_subscription(message, True)

    elif await test_for_command(message.content, "unsubscribe"):
        logging.info("unsubscribe command recieved")

        await handle_subscription(message, False)

    elif await test_for_command(message.content, "unsub"):
        logging.info("unsub command recieved")

        await handle_subscription(message, False)

    elif await test_for_command(message.content, "list"):
        logging.info("list command recieved")
        
        await list_sub_roles(message)

    elif await test_for_command(message.content, "check"):
        logging.info("check command recieved")

        await list_users_subbed_roles(message)

    elif await test_for_command(message.content, "help"):
        logging.info("help command recieved")

        await handle_help(message)

    elif await test_for_command_sequence(message.content):
        logging.info("invalid command recieved")

        await handle_help(message)


"""
This method takes the input from discord and a string representing the command being tested for
and checks if it begins with the commandCharacter plus the requested command
"""
async def test_for_command(input, string_to_test):
    return await test_string_beginnings(input, command_sequence + string_to_test)

async def test_for_command_sequence(input):
    return await test_string_beginnings(input, command_sequence)

"""
this function tests the first characters of an input string for the beginning string.
Returns true if the entire beginning string was found in the unput string, false otherwise
"""
async def test_string_beginnings(string, beginning):
    for index in range(0, len(string)):
        # if there is no match at any point, return false
        if string[index] != beginning[index]:
            return False

        # if there is a match and the next index is not in the command sequence, return true
        elif string[index] == beginning[index] and index + 1 >= len(beginning):
            return True


async def get_subscribeable_roles_for_server(server):
    roles = server.roles
    subscription_roles = []
    for role in roles:
        if role.name[-1] == subscription_role_suffix:
            # if should_lowercase:
            #     role.name = role.name.lower()#lowercase the name for detection later
            subscription_roles.append(role)

    return subscription_roles

async def get_subscribeable_role_names_for_server(server):
    roles = get_subscribeable_roles_for_server(server)
    subscription_role_names = []
    for role in roles:
        subscription_role_names.append(role.name.lower())

    return subscription_role_names


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
            await send_error_message(message.channel, "Only integer subscription ID's are allowed.\nYou can find the ID by using ***.list*** or ***.manage***")
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

async def handle_subscription(message, is_subscribing):

    if await check_for_spam_channel(message):

        sub_roles = await get_subscribeable_roles_for_server(message.server)
        to_act_roles = message.content.lower().split()  # get the space separated parameters
        to_act_roles.pop(0)  # remove the first one, which is the command

        # print("TSR: " + str(to_act_roles))

        # remove authors existing roles from subscription list
        for userrole in message.author.roles:

            # remove the role suffix if it is a subscription role and lowercase it
            author_clean_role_name = cleanup_role_name(userrole.name)

            # If a role in the user's list of roles matches one of those that was requested for action send a message
            # and remove it.
            if author_clean_role_name in to_act_roles:
                if is_subscribing:
                    await client.send_message(message.channel,
                                              "You are already subscribed to ***{}***.".format(author_clean_role_name))
                    to_act_roles.remove(author_clean_role_name)
            # othewise, if the role is at least in the list of subscription roles
            elif author_clean_role_name in sub_roles:
                if not(is_subscribing):
                    await client.send_message(message.channel,
                                              "You are not currently subscribed to ***{}***.".format(author_clean_role_name))

        # go through each subscribe-able role and check if the user wants to act on it, if so, act and remove it.
        for subrole in sub_roles:

            if subrole.name[:-len(subscription_role_suffix)].lower() in to_act_roles:
                if is_subscribing:
                    await client.add_roles(message.author, subrole)
                    await client.send_message(message.channel,
                                              "Successfully subscribed to ***{}***.".format(subrole.name))
                else:
                    await client.remove_roles(message.author, subrole)
                    await client.send_message(message.channel,
                                              "Successfully unsubscribed from ***{}***.".format(subrole.name))

                to_act_roles.remove(cleanup_role_name(subrole.name))

        # go through remaining roles and tell the user that they dont exist
        for invalidrole in to_act_roles:
            logging.info(invalidrole)
            await client.send_message(message.channel,
                                      "No action was taken for ***{}*** because it doesn't exist.".format(invalidrole))



async def show_subscription_info(message):
    if await check_for_spam_channel(message):
        sub_roles = await get_subscribeable_roles_for_server(message.server)

        response_content = ""
        index = 0

        for role in sub_roles:
            if role in message.author.roles:
                response_content += "{}. ***{}***".format(index, await cleanup_role_name(role.name))
            else:
                response_content += "{}. {}".format(index, await cleanup_role_name(role.name))

            response_content += "\n"
            index += 1

        response_content += "\n\n You are already subscribed to roles listed in ***bold***"
        response_content += "\n To change a subscription, please use ***.toggle*** followed by"


        await send_embed_message(message.channel,
                "Subscription Status for {}".format(message.author.display_name),
                response_content)





async def list_sub_roles(message):
    if await check_for_spam_channel(message):
        sub_roles = await get_subscribeable_roles_for_server(message.server)
        message_content = ""
        
        for role in sub_roles:
            message_content += await cleanup_role_name(role.name) + "\n"
        
        await send_embed_message(message.channel, "Here are the roles you may subscribe to:", message_content)


async def list_users_subbed_roles(message):
    if await check_for_spam_channel(message):
        sub_roles = await get_subscribeable_roles_for_server(message.server)
        user_roles = await get_processed_role_name_list(message.author.roles)
        is_there_something_to_show = False  # assume nothing to show
        subbed_roles = []

        logging.debug(user_roles)
        logging.debug(message.author)
        logging.debug(message.author.roles)

        for subrole in sub_roles:
            # author_clean_role_name = cleanup_role_name(userrole.name)
            if await cleanup_role_name(subrole.name) in user_roles:
                if not (is_there_something_to_show):
                    is_there_something_to_show = True
                subbed_roles.append("***{}***".format(await cleanup_role_name(subrole.name)))

        if not(is_there_something_to_show):
            await send_embed_message(message.channel, "Your Subscriptions:", "You have not subscribed to anything. ***:frowning:***")
            return

        await send_list_message(message.channel, "Your Subscriptions:", subbed_roles)

async def handle_help(message):
    if await check_for_spam_channel(message):
        help_msg = '''
        Here are the commands you can use:
        ***.manage***, ***.list*** - Show a summary of your subscription options 
        ***.toggle [subscription number]*** - Toggle your subscription status on or off for subscription number given
        ***.help*** - Display this help menu
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

async def send_list_message(msg_channel, title, response_list, intro_message="", end_message=""):
    
    if intro_message != "":
        bot_response_content = intro_message
    else:
        bot_response_content = ""

    for item in response_list:
        bot_response_content += str(item) + "\n"

    if end_message != "":
        bot_response_content += "\n\n" + end_message

    await send_embed_message(msg_channel, title, bot_response_content)


async def make_string_list(item_list, intro_message="", end_message=""):
    
    if intro_message != "":
        str_list = intro_message
    else:
        str_list = ""

    for item in response_list:
        str_list += str(item) + "\n"

    if end_message != "":
        str_list += "\n\n" + end_message

    return str_list

async def get_processed_role_name_list(roles):
    role_names = []
    logging.debug(roles)

    for role in roles:
        role_names.append(await cleanup_role_name(role.name))

    return role_names

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

