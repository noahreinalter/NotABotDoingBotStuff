import discord
from discord.ext import commands

import core.globals

default_admin_role = 'Admin'


def admin_role_check():
    def predicate(ctx):
        cur = core.globals.sql_connection.cursor()
        cur.execute("SELECT * FROM servers WHERE id=:id",
                    {"id": ctx.guild.id})

        guild = cur.fetchone()

        if guild is not None:
            role = discord.utils.get(ctx.author.roles, name=guild[2])
        else:
            role = discord.utils.get(ctx.author.roles, name=default_admin_role)

        if role is None:
            if guild is not None:
                raise commands.errors.MissingRole(guild[2])
            else:
                raise commands.errors.MissingRole(default_admin_role)
        else:
            return True

    return commands.check(predicate)


def admin_role(ctx):
    cur = core.globals.sql_connection.cursor()
    cur.execute("SELECT * FROM servers WHERE id=:id",
                {"id": ctx.guild.id})

    guild = cur.fetchone()

    if guild is not None:
        return guild[2]
    else:
        return default_admin_role
