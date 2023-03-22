import discord
from discord.ext import commands

from main import add_extension_function, remove_extension_function, reload_extension_function
import core.permission_manager
import core.permission_enum

extension_feature_path = 'features.'
permissions = [core.permission_enum.PermissionEnum.read_messages.name,
               core.permission_enum.PermissionEnum.send_messages.name,
               core.permission_enum.PermissionEnum.use_application_commands.name]

def setup(bot):
    core.permission_manager.add_permissions(permissions)
    bot.add_cog(BotManagement(bot))
    print('BotManagement is being loaded!')


def teardown(bot):
    core.permission_manager.remove_permissions(permissions)
    bot.remove_cog('BotManagement')
    print('BotManagement is being unloaded')


class BotManagement(commands.Cog, name='Bot Management'):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='add_extension', description='$add_extension extension_name')
    @commands.is_owner()
    async def add_extension(self, ctx, extension_name):
        add_extension_function(extension_feature_path + extension_name, self.bot)
        await ctx.send('Extension ' + extension_name + ' added to bot.')

    @add_extension.error
    async def add_extension_error(self, ctx, error):
        pass

    @commands.slash_command(name='remove_extension', description='$remove_extension extension_name')
    @commands.is_owner()
    async def remove_extension(self, ctx, extension_name):
        remove_extension_function(extension_feature_path + extension_name, self.bot)
        await ctx.send('Extension ' + extension_name + ' removed from bot.')

    @remove_extension.error
    async def remove_extension_error(self, ctx, error):
        pass

    @commands.slash_command(name='reload_extension', description='$reload_extension extension_name')
    @commands.is_owner()
    async def reload_extension(self, ctx, extension_name):
        reload_extension_function(extension_feature_path + extension_name, self.bot)
        await ctx.send('Extension ' + extension_name + ' reloaded.')

    @reload_extension.error
    async def reload_extension_error(self, ctx, error):
        pass

    @commands.slash_command(name='invite', description='Returns a invite link for the bot.')
    async def generate_invite_link(self, ctx):
        await ctx.send(discord.utils.oauth_url(
            client_id=self.bot.user.id,
            permissions=discord.Permissions(**core.permission_manager.get_permissions())))

    @generate_invite_link.error
    async def generate_invite_link_error(self, ctx, error):
        pass

    @commands.slash_command(name='stop', description='Stops the bot.')
    @commands.is_owner()
    async def stop_bot(self, ctx):
        await self.bot.close()

    @stop_bot.error
    async def stop_bot_error(self, ctx, error):
        pass
