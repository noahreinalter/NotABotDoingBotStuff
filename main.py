import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import sqlite3
from sqlite3 import Error
import glob

import core.globals
import core.role_manager
import core.prefix_manager

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
sql_path = 'db.sqlite'
extension_feature_path = 'features.'

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

    features = glob.glob('features/*.py')
    for feature in features:
        feature = feature.replace('.py', '')
        add_extension_function(feature.replace('\\', '.'))


@bot.event
async def on_guild_join(guild):
    print('Joined', guild)


@bot.command(name='invite', help='Returns a invite link for the bot.')
async def generate_invite_link(ctx):
    await ctx.send(discord.utils.oauth_url(
        client_id=bot.user.id,
        permissions=discord.Permissions(manage_channels=True, manage_roles=True,
                                        read_messages=True, send_messages=True)))


@bot.command(name='stop', help='Stops the bot.')
@commands.is_owner()
async def stop_bot(ctx):
    await bot.close()


@stop_bot.error
async def stop_bot_error(ctx, error):
    pass


def add_extension_function(extension_name):
    bot.load_extension(extension_name)


@bot.command(name='add_extension', help='$add_extension extension_name')
@commands.is_owner()
async def add_extension(ctx, extension_name):
    add_extension_function(extension_feature_path + extension_name)

    await ctx.send('Extension ' + extension_name + ' added to bot.')


@add_extension.error
async def add_extension_error(ctx, error):
    pass


def remove_extension_function(extension_name):
    bot.unload_extension(extension_name)


@bot.command(name='remove_extension', help='$remove_extension extension_name')
@commands.is_owner()
async def remove_extension(ctx, extension_name):
    remove_extension_function(extension_feature_path + extension_name)

    await ctx.send('Extension ' + extension_name + ' removed from bot.')


@remove_extension.error
async def remove_extension_error(ctx, error):
    pass


@bot.command(name='change_prefix', help='$change_prefix new prefix')
@core.role_manager.admin_role_check()
@commands.guild_only()
async def change_prefix(ctx, new_prefix):
    cur = core.globals.sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": ctx.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        cur.execute("REPLACE INTO servers values (?, ?, ?)", (guild[0], new_prefix, guild[2]))
    else:
        cur.execute("INSERT INTO servers values (?, ?, ?)",
                    (ctx.guild.id, new_prefix, core.role_manager.default_admin_role))

    core.globals.sql_connection.commit()
    await ctx.send('Prefix changed to ' + new_prefix)


@change_prefix.error
async def change_prefix_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send('This command only works on a server.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('Only User with the role ' + core.role_manager.admin_role(ctx) + ' can use this command.')
    else:
        await ctx.send('Something went wrong please try again.')


@bot.command(name='change_admin_role', help='$change_admin_role @New_Admin_Role')
@core.role_manager.admin_role_check()
@commands.guild_only()
async def change_admin_role(ctx, new_role_name):
    cur = core.globals.sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": ctx.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        cur.execute("REPLACE INTO servers values (?, ?, ?)", (guild[0], guild[1], new_role_name))
    else:
        cur.execute("INSERT INTO servers values (?, ?, ?)", (ctx.guild.id, core.prefix_manager.prefix(ctx), new_role_name))

    core.globals.sql_connection.commit()
    await ctx.send('Admin role changed to ' + new_role_name)


@change_admin_role.error
async def change_admin_role(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send('This command only works on a server.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('Only User with the role ' + core.role_manager.admin_role(ctx) + ' can use this command.')
    else:
        await ctx.send('Something went wrong please try again.')


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
    bot.run(BOT_TOKEN)
