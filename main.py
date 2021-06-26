import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import sqlite3
from sqlite3 import Error

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
default_prefix = '$'
default_admin_role = 'Admin'
leader_string = ' Leader'
member_string = ' Member'
sql_path = 'db.sqlite'
sql_connection = None
extension_feature_path = 'extensions.features.'

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)


def prefix(ctx):
    cur = sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": ctx.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        return guild[1]
    else:
        return default_prefix


def prefix_function(bot, message):
    cur = sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": message.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        return commands.when_mentioned_or(guild[1])(bot, message)
    else:
        return commands.when_mentioned_or(default_prefix)(bot, message)


bot = commands.Bot(command_prefix=prefix_function)


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    print('Logged in on {0} servers'.format(len(bot.guilds)))
    for guild in bot.guilds:
        print(' {0}, Number of members = {1}'.format(guild.name, guild.member_count))


@bot.event
async def on_guild_join(guild):
    print('Joined', guild)


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


def add_extension_function(extension_name):
    bot.load_extension(extension_name)


@bot.command(name='add_extension', hidden=True)
@commands.is_owner()
async def add_extension(ctx, extension_name):
    add_extension_function(extension_feature_path + extension_name)

    await ctx.send('Extension ' + extension_name + ' added to bot.')


@add_extension.error
async def add_extension_error(ctx, error):
    pass


def remove_extension_function(extension_name):
    bot.unload_extension(extension_name)


@bot.command(name='remove_extension', hidden=True)
@commands.is_owner()
async def remove_extension(ctx, extension_name):
    remove_extension_function(extension_feature_path + extension_name)

    await ctx.send('Extension ' + extension_name + ' removed from bot.')


@remove_extension.error
async def remove_extension_error(ctx, error):
    pass


@bot.command(name='change_prefix')
@commands.has_role(default_admin_role)
async def change_prefix(ctx, new_prefix):
    cur = sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": ctx.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        cur.execute("REPLACE INTO servers values (?, ?, ?)", (guild[0], new_prefix, guild[2]))
    else:
        cur.execute("INSERT INTO servers values (?, ?, ?)", (ctx.guild.id, new_prefix, default_admin_role))

    sql_connection.commit()
    await ctx.send('Prefix changed to ' + new_prefix)


@bot.command(name='change_admin_role', help='Work in progress does not work!!', hidden=True)
@commands.has_role(default_admin_role)
async def change_admin_role(ctx, new_role_name):
    cur = sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": ctx.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        cur.execute("REPLACE INTO servers values (?, ?, ?)", (guild[0], guild[1], new_role_name))
    else:
        cur.execute("INSERT INTO servers values (?, ?, ?)", (ctx.guild.id, prefix(ctx), new_role_name))

    sql_connection.commit()
    await ctx.send('Admin role changed to ' + new_role_name)


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
    sql_connection = create_connection(sql_path)
    create_servers(sql_connection)
    bot.run(BOT_TOKEN)
