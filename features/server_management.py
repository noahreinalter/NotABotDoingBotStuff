from discord.ext import commands

from main import add_extension_function, remove_extension_function
import core.role_manager
import core.prefix_manager

extension_feature_path = 'features.'


def setup(bot):
    bot.add_cog(ServerManagement(bot))
    print('ServerManagement is being loaded!')


def teardown(bot):
    bot.remove_cog('ServerManagement')
    print('ServerManagement is being unloaded')


class ServerManagement(commands.Cog, name='Server Management'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='add_extension', help='$add_extension extension_name')
    @commands.is_owner()
    async def add_extension(self, ctx, extension_name):
        add_extension_function(extension_feature_path + extension_name)

        await ctx.send('Extension ' + extension_name + ' added to bot.')

    @add_extension.error
    async def add_extension_error(self, ctx, error):
        pass

    @commands.command(name='remove_extension', help='$remove_extension extension_name')
    @commands.is_owner()
    async def remove_extension(self, ctx, extension_name):
        remove_extension_function(extension_feature_path + extension_name)

        await ctx.send('Extension ' + extension_name + ' removed from bot.')

    @remove_extension.error
    async def remove_extension_error(self, ctx, error):
        pass

    @commands.command(name='change_prefix', help='$change_prefix new prefix')
    @core.role_manager.admin_role_check()
    @commands.guild_only()
    async def change_prefix(self, ctx, new_prefix):
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
    async def change_prefix_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command only works on a server.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Only User with the role ' + core.role_manager.admin_role(ctx) + ' can use this command.')
        else:
            await ctx.send('Something went wrong please try again.')

    @commands.command(name='change_admin_role', help='$change_admin_role @New_Admin_Role')
    @core.role_manager.admin_role_check()
    @commands.guild_only()
    async def change_admin_role(self, ctx, new_role_name):
        cur = core.globals.sql_connection.cursor()
        cur.execute("SELECT * FROM servers WHERE id=:id",
                    {"id": ctx.guild.id})

        guild = cur.fetchone()

        if guild is not None:
            cur.execute("REPLACE INTO servers values (?, ?, ?)", (guild[0], guild[1], new_role_name))
        else:
            cur.execute("INSERT INTO servers values (?, ?, ?)",
                        (ctx.guild.id, core.prefix_manager.prefix(ctx), new_role_name))

        core.globals.sql_connection.commit()
        await ctx.send('Admin role changed to ' + new_role_name)

    @change_admin_role.error
    async def change_admin_role(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command only works on a server.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Only User with the role ' + core.role_manager.admin_role(ctx) + ' can use this command.')
        else:
            await ctx.send('Something went wrong please try again.')
