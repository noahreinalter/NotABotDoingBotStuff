import discord
from discord.ext import commands


def setup(bot):
    bot.add_cog(BotManagement(bot))
    print('BotManagement is being loaded!')


def teardown(bot):
    bot.remove_cog('BotManagement')
    print('BotManagement is being unloaded')


class BotManagement(commands.Cog, name='Bot Management'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='invite', help='Returns a invite link for the bot.')
    async def generate_invite_link(self, ctx):
        await ctx.send(discord.utils.oauth_url(
            client_id=self.bot.user.id,
            permissions=discord.Permissions(manage_channels=True, manage_roles=True,
                                            read_messages=True, send_messages=True)))

    @generate_invite_link.error
    async def generate_invite_link_error(self, ctx, error):
        pass

    @commands.command(name='stop', help='Stops the bot.')
    @commands.is_owner()
    async def stop_bot(self, ctx):
        await self.bot.close()

    @stop_bot.error
    async def stop_bot_error(self, ctx, error):
        pass
