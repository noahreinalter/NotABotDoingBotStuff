import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

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
async def generation_controller(ctx):
    if discord.utils.get(ctx.author.roles, name='Admin') is None:
        await ctx.send('Only User with the role Admin use this command.')
        return
    role_name = ctx.message.content.split()[1]
    roles = await generate_roles(ctx.guild, role_name, ctx.message.mentions[0])

    await generate_channels(ctx.guild, role_name, roles)

    await ctx.send('New roles and channels generated.')


async def generate_roles(guild, role_name, member):
    await asyncio.gather(
        guild.create_role(name=role_name + ' Leader'),
        guild.create_role(name=role_name + ' Member')
    )

    all_roles = await guild.fetch_roles()
    roles = [discord.utils.get(all_roles, name=role_name + ' Leader'),
             discord.utils.get(all_roles, name=role_name + ' Member')]

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
async def delete_controller(ctx):
    if discord.utils.get(ctx.author.roles, name='Admin') is None:
        await ctx.send('Only User with the role Admin use this command.')
        return
    role_name = ctx.message.content.split()[1]
    await delete_roles(ctx.guild, role_name)

    await delete_channels(ctx.guild, role_name)

    await ctx.send('Roles and channels have been deleted.')


async def delete_roles(guild, role_name):
    await asyncio.gather(
        discord.utils.get(guild.roles, name=role_name + ' Leader').delete(),
        discord.utils.get(guild.roles, name=role_name + ' Member').delete()
    )


async def delete_channels(guild, role_name):
    category_channel = discord.utils.get(guild.channels, name=role_name)
    await asyncio.gather(
        category_channel.channels[0].delete(),
        category_channel.channels[1].delete()
    )
    await category_channel.delete()


@bot.command(name='add', help='$add @User @Role')
async def add_member_to_role(ctx):
    leader_role = ctx.message.role_mentions[0].name.split()[0] + ' Leader'
    if discord.utils.get(ctx.author.roles, name=leader_role):
        await ctx.message.mentions[0].add_roles(ctx.message.role_mentions[0])
        await ctx.send('Role added to user.')
    else:
        await ctx.send('To add this role you need to have the role ' + leader_role + '.')


@bot.command(name='remove', help='$remove @User @Role')
async def remove_member_from_role(ctx):
    leader_role = ctx.message.role_mentions[0].name.split()[0] + ' Leader'
    if discord.utils.get(ctx.author.roles, name=leader_role):
        await ctx.message.mentions[0].remove_roles(ctx.message.role_mentions[0])
        await ctx.send('Role removed from user.')
    else:
        await ctx.send('To remove this role you need to have the role ' + leader_role + '.')


if __name__ == '__main__':
    bot.run(BOT_TOKEN)
