import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
leader_string = ' Leader'
member_string = ' Member'

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix='$')


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))


@bot.command(name='generate', help='$generate categoryname @User')
@commands.has_role('Admin')
@commands.guild_only()
async def generation_controller(ctx, category_name, member: commands.MemberConverter):
    if discord.utils.get(ctx.guild.channels, name=category_name) is None:
        roles = await generate_roles(ctx.guild, category_name, member)

        await generate_channels(ctx.guild, category_name, roles)

        await ctx.send('New roles and channels generated.')
    else:
        await ctx.send('There are already channels in this namespace.')


@generation_controller.error
async def generation_controller_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send('This command only works on a server.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('Only User with the role Admin use this command.')


async def generate_roles(guild, role_name, member):
    await asyncio.gather(
        guild.create_role(name=role_name + leader_string),
        guild.create_role(name=role_name + member_string)
    )

    all_roles = await guild.fetch_roles()
    roles = [discord.utils.get(all_roles, name=role_name + leader_string),
             discord.utils.get(all_roles, name=role_name + member_string)]

    await asyncio.gather(
        member.add_roles(roles[0]),
        member.add_roles(roles[1])
    )

    return roles


async def generate_channels(guild, channel_name, roles):
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        roles[0]: discord.PermissionOverwrite(read_messages=True),
        roles[1]: discord.PermissionOverwrite(read_messages=True),
    }
    category = await guild.create_category(name=channel_name, overwrites=overwrites)

    await asyncio.gather(
        guild.create_text_channel(name=channel_name + '-text', category=category, sync_permissions=True),
        guild.create_voice_channel(name=channel_name + '-voice', category=category, sync_permissions=True)
    )


@bot.command(name='delete', help='$delete categoryname')
@commands.has_role('Admin')
@commands.guild_only()
async def delete_controller(ctx, category_name):
    await delete_roles(ctx.guild, category_name)
    await delete_channels(ctx.guild, category_name)

    await ctx.send('Roles and channels have been deleted.')


@delete_controller.error
async def delete_controller_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send('This command only works on a server.')
    elif isinstance(error, commands.CheckFailure):
        await ctx.send('Only User with the role Admin use this command.')


async def delete_roles(guild, role_name):
    await asyncio.gather(
        discord.utils.get(guild.roles, name=role_name + leader_string).delete(),
        discord.utils.get(guild.roles, name=role_name + member_string).delete()
    )


async def delete_channels(guild, role_name):
    category_channel = discord.utils.get(guild.channels, name=role_name)
    await asyncio.gather(
        category_channel.channels[0].delete(),
        category_channel.channels[1].delete()
    )
    await category_channel.delete()


@bot.command(name='add', help='$add @User @Role')
@commands.guild_only()
async def add_member_to_role(ctx, member: commands.MemberConverter, role: commands.RoleConverter):
    leader_role = role.name.split()[0] + leader_string
    if discord.utils.get(ctx.author.roles, name=leader_role) is None:
        raise commands.MissingRole(leader_role)

    await member.add_roles(role.name.split()[0] + member_string)
    await ctx.send('Role added to user.')


@add_member_to_role.error
async def add_member_to_role_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send('This command only works on a server.')
    elif isinstance(error, commands.MissingRole):
        await ctx.send('To add this role you need to have the role ' + error.missing_role + '.')


@bot.command(name='remove', help='$remove @User @Role')
@commands.guild_only()
async def remove_member_from_role(ctx, member: commands.MemberConverter, role: commands.RoleConverter):
    leader_role = role.name.split()[0] + leader_string
    if discord.utils.get(ctx.author.roles, name=leader_role) is None:
        raise commands.MissingRole(leader_role)

    await member.remove_roles(role.name.split()[0] + member_string)
    await ctx.send('Role removed from user.')


@remove_member_from_role.error
async def remove_member_from_role_error(ctx, error):
    if isinstance(error, commands.NoPrivateMessage):
        await ctx.send('This command only works on a server.')
    elif isinstance(error, commands.MissingRole):
        await ctx.send('To remove this role you need to have the role ' + error.missing_role + '.')


if __name__ == '__main__':
    bot.run(BOT_TOKEN)
