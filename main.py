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

        if message.content.startswith('$generate'):
            await generation_controller(message)


async def generation_controller(message):
    if discord.utils.get(message.author.roles, name='Admin') is None:
        await message.channel.send('Only User with the role Admin use this command.')
        return
    role_name = message.content.split()[1]
    roles = await generate_roles(message.guild, role_name, message.mentions[0])

    await generate_channels(message.guild, role_name, roles)

    await message.channel.send('New roles and channels generated.')


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


if __name__ == '__main__':
    client = BotClient()
    client.run(BOT_TOKEN)
