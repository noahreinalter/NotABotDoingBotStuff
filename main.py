from discord.ext import commands
import discord
import logging
import os
from dotenv import load_dotenv
import sqlite3
from sqlite3 import Error
import glob

import core.globals
import core.prefix_manager
import core.permission_manager

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
sql_path = 'db.sqlite'

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=core.prefix_manager.prefix_function)


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    print('Logged in on {0} servers'.format(len(bot.guilds)))
    for guild in bot.guilds:
        print(' {0}, Number of members = {1}'.format(guild.name, guild.member_count))

    print('You can invite the bot using this link:',
          discord.utils.oauth_url(
              client_id=bot.user.id,
              permissions=discord.Permissions(**core.permission_manager.get_permissions())))


@bot.event
async def on_guild_join(guild):
    print('Joined', guild)


def add_extension_function(extension_name, bot_parameter):
    bot_parameter.load_extension(extension_name)


def remove_extension_function(extension_name, bot_parameter):
    bot_parameter.unload_extension(extension_name)


def reload_extension_function(extension_name, bot_parameter):
    bot_parameter.reload_extension(extension_name)


def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection


def execute_create_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
    except Error as e:
        print(f"The error '{e}' occurred")


def create_servers(connection):
    execute_create_query(connection,
                         """
                            CREATE TABLE IF NOT EXISTS servers (
                            id INTEGER PRIMARY KEY,
                            prefix TEXT NOT NULL,
                            admin_role Text
                            );
                        """)


if __name__ == '__main__':
    core.globals.initialize()
    core.globals.sql_connection = create_connection(sql_path)
    create_servers(core.globals.sql_connection)

    features = glob.glob('features/*.py')
    for feature in features:
        feature = feature.replace('.py', '')
        feature = feature.replace('\\', '.')
        add_extension_function(feature, bot)

    bot.run(BOT_TOKEN)
