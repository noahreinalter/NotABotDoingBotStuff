from discord.ext import commands

import core.role_manager
import core.prefix_manager
import core.permission_manager
import core.permission_enum

permissions = [core.permission_enum.PermissionEnum.read_messages.name,
               core.permission_enum.PermissionEnum.send_messages.name,
               core.permission_enum.PermissionEnum.use_application_commands.name]


def setup(bot):
    core.permission_manager.add_permissions(permissions)
    bot.add_cog(ServerManagement(bot))
    print('ServerManagement is being loaded!')


def teardown(bot):
    core.permission_manager.remove_permissions(permissions)
    bot.remove_cog('ServerManagement')
    print('ServerManagement is being unloaded')


class ServerManagement(commands.Cog, name='Server Management'):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='change_prefix', description='$change_prefix new prefix')
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

    @commands.slash_command(name='change_admin_role', description='$change_admin_role @New_Admin_Role')
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
    async def change_admin_role_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command only works on a server.')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Only User with the role ' + core.role_manager.admin_role(ctx) + ' can use this command.')
        else:
            await ctx.send('Something went wrong please try again.')
