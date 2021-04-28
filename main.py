import discord
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


class BotClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author.bot:
            return

        text = message.content

        # TODO: Add good help message
        if text.startswith('$help'):
            await message.channel.send()

        if text.startswith('$generate'):
            await generation_controller(message)

        if text.startswith('$delete'):
            await delete_controller(message)

        if text.startswith('$add'):
            await add_member_to_role(message)

        if text.startswith('$remove'):
            await remove_member_from_role(message)


async def generation_controller(message):
    if discord.utils.get(message.author.roles, name='Admin') is None:
        await message.channel.send('Only User with the role Admin use this command.')
        return
    role_name = message.content.split()[1]
    roles = await generate_roles(message.guild, role_name, message.mentions[0])

    await generate_channels(message.guild, role_name, roles)

    await message.channel.send('New roles and channels generated.')


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
        roles[1]: discord.PermissionOverwrite(read_messages=True)
    }
    category = await guild.create_category(name=channel_name, overwrites=overwrites)

    await asyncio.gather(
        guild.create_text_channel(name=channel_name + '-text', category=category, sync_permissions=True),
        guild.create_voice_channel(name=channel_name + '-voice', category=category, sync_permissions=True)
    )


async def delete_controller(message):
    if discord.utils.get(message.author.roles, name='Admin') is None:
        await message.channel.send('Only User with the role Admin use this command.')
        return
    role_name = message.content.split()[1]
    await delete_roles(message.guild, role_name)

    await delete_channels(message.guild, role_name)

    await message.channel.send('Roles and channels have been deleted.')


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


async def add_member_to_role(message):
    leader_role = message.role_mentions[0].name.split()[0] + ' Leader'
    if discord.utils.get(message.author.roles, name=leader_role):
        await message.mentions[0].add_roles(message.role_mentions[0])
        await message.channel.send('Role added to user.')
    else:
        await message.channel.send('To add this role you need to have the role ' + leader_role + '.')


async def remove_member_from_role(message):
    leader_role = message.role_mentions[0].name.split()[0] + ' Leader'
    if discord.utils.get(message.author.roles, name=leader_role):
        await message.mentions[0].remove_roles(message.role_mentions[0])
        await message.channel.send('Role removed from user.')
    else:
        await message.channel.send('To remove this role you need to have the role ' + leader_role + '.')


if __name__ == '__main__':
    client = BotClient()
    client.run(BOT_TOKEN)
