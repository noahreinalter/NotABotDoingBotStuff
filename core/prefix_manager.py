from discord.ext import commands

import core.globals

default_prefix = '$'


def prefix_function(bot, message):
    cur = core.globals.sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": message.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        return commands.when_mentioned_or(guild[1])(bot, message)
    else:
        return commands.when_mentioned_or(default_prefix)(bot, message)


def prefix(ctx):
    cur = core.globals.sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": ctx.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        return guild[1]
    else:
        return default_prefix
