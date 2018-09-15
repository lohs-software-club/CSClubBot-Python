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
        logging.debug("subscribe command recieved")

        await handle_subscription(message, True)

    elif await test_for_command(message.content, "sub"):
        logging.debug("sub command recieved")

        await handle_subscription(message, True)

    elif await test_for_command(message.content, "unsubscribe"):
        logging.debug("unsubscribe command recieved")

        await handle_subscription(message, False)

    elif await test_for_command(message.content, "unsub"):
        logging.debug("unsub command recieved")

        await handle_subscription(message, False)

    elif await test_for_command(message.content, "list"):
        logging.debug("list command recieved")
        
        await list_sub_roles(message)

    elif await test_for_command(message.content, "check"):
        logging.debug("check command recieved")

        await list_users_subbed_roles(message)

    elif await test_for_command(message.content, "help"):
        logging.debug("help command recieved")

        await handle_help(message)

    elif await test_for_command_sequence(message.content):
        logging.debug("invalid command recieved")

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


async def get_subscribeable_roles_for_server(server_name):
    roles = discord.utils.get(client.servers, name=server_name).roles
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

async def handle_subscription(message, is_subscribing):

    if await check_for_spam_channel(message):

        sub_roles = await get_subscribeable_roles_for_server(server_name)
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


async def list_sub_roles(message):
    if await check_for_spam_channel(message):
        sub_roles = await get_subscribeable_roles_for_server(server_name)
        await client.send_message(message.channel, "Here are the roles you may subscribe to:")

        for role in sub_roles:
            await client.send_message(message.channel, "***{}***".format(role.name[:-1]))


async def list_users_subbed_roles(message):
    if await check_for_spam_channel(message):
        sub_roles = await get_subscribeable_roles_for_server(server_name)
        user_roles = await get_processed_role_name_list(message.author.roles)
        is_there_something_to_show = False  # assume nothing to show

        logging.debug(user_roles)
        logging.debug(message.author)
        logging.debug(message.author.roles)

        for subrole in sub_roles:
            # author_clean_role_name = cleanup_role_name(userrole.name)
            if await cleanup_role_name(subrole.name) in user_roles:
                if not (is_there_something_to_show):
                    await client.send_message(message.channel, "Here are the roles you are subscribed to:")
                    is_there_something_to_show = True
                await client.send_message(message.channel, "***{}***".format(await cleanup_role_name(subrole.name)))

        if not(is_there_something_to_show):
            await client.send_message(message.channel, "You have not subscribed to anything. :/")

async def handle_help(message):
    if await check_for_spam_channel(message):
        await client.send_message(message.channel, "Here are the commands you can use:")
        await client.send_message(message.channel, "***.sub***,***.subscribe*** - Subscribe to a role")
        await client.send_message(message.channel, "***.unsub***,***.unsubscribe*** - Unsubscribe from a role")
        await client.send_message(message.channel, "***.sub***,***.subscribe*** - Subscribe to a role")
        await client.send_message(message.channel, "***.list*** - List the subscription roles that are available")
        await client.send_message(message.channel, "***.check*** - Check what roles you are subscribed to")
        await client.send_message(message.channel, "***.help*** - Display this list")
    else:
        await client.send_message(message.channel, "Please use the bot-spam channel to talk to me")


async def get_processed_role_name_list(roles):
    role_names = []
    logging.debug(roles)

    for role in roles:
        role_names.append(await cleanup_role_name(role.name))

    return role_names

async def cleanup_role_name(name):
    return name[:-len(subscription_role_suffix)].lower()

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

