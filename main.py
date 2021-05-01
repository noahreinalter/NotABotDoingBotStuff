import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import sqlite3
from sqlite3 import Error

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
prefix = '$'
leader_string = ' Leader'
member_string = ' Member'
sql_path = 'db.sqlite'
sql_connection = None

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix=commands.when_mentioned_or(prefix))


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


@bot.command(name='invite', help='Returns a invite link for the bot.')
async def generate_invite_link(ctx):
    await ctx.send(discord.utils.oauth_url(
        client_id=bot.user.id,
        permissions=discord.Permissions(manage_channels=True, manage_roles=True,
                                        read_messages=True, send_messages=True)))


@bot.command(name='stop', hidden=True)
@commands.is_owner()
async def stop_bot(ctx):
    await bot.close()


@stop_bot.error
async def stop_bot_error(ctx, error):
    pass


@bot.command(name='add_extension', hidden=True)
@commands.is_owner()
async def add_extension(ctx, extension_name):
    bot.load_extension(extension_name)
    await ctx.send('Extension ' + extension_name + ' added to bot.')


@add_extension.error
async def add_extension_error(ctx, error):
    pass


@bot.command(name='remove_extension', hidden=True)
@commands.is_owner()
async def remove_extension(ctx, extension_name):
    bot.unload_extension(extension_name)
    await ctx.send('Extension ' + extension_name + ' removed from bot.')


@remove_extension.error
async def remove_extension_error(ctx, error):
    pass


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


def create_extensions(connection):
    execute_create_query(connection,
                         """
                            CREATE TABLE IF NOT EXISTS extensions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL 
                            );
                        """)


if __name__ == '__main__':
    sql_connection = create_connection(sql_path)
    create_servers(sql_connection)
    create_extensions(sql_connection)
    bot.run(BOT_TOKEN)
