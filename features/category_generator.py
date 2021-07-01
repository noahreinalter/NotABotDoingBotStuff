import discord
from discord.ext import commands
import asyncio

import core.role_manager
import core.prefix_manager
import core.permission_manager

leader_string = ' Leader'
member_string = ' Member'


def setup(bot):
    core.permission_manager.add_permissions(["manage_channels", "manage_roles", "read_messages", "send_messages"])
    bot.add_cog(CategoryGenerator(bot))
    print('CategoryGenerator is being loaded!')


def teardown(bot):
    core.permission_manager.remove_permissions(["manage_channels", "manage_roles", "read_messages", "send_messages"])
    bot.remove_cog('CategoryGenerator')
    print('CategoryGenerator is being unloaded')


class CategoryGenerator(commands.Cog, name='Category Generator'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='generate', help='$generate categoryname @User')
    @core.role_manager.admin_role_check()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True,
                                        read_messages=True, send_messages=True)
    @commands.guild_only()
    async def generation_controller(self, ctx, category_name, member: commands.MemberConverter):
        if discord.utils.get(ctx.guild.channels, name=category_name) is None:
            roles = await self.generate_roles(ctx.guild, category_name, member)

            await self.generate_channels(ctx.guild, category_name, roles)

            await ctx.send('New roles and channels generated.')
        else:
            await ctx.send('There are already channels in this namespace.')

    @generation_controller.error
    async def generation_controller_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command only works on a server.')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('The bot needs at least all permissions requested from the invite link generated with '
                           + core.prefix_manager.prefix(ctx) + 'invite')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Only User with the role ' + core.role_manager.admin_role(ctx) + ' can use this '
                                                                                            'command.')
        else:
            await ctx.send('Something went wrong please try again.')

    async def generate_roles(self, guild, role_name, member):
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

    async def generate_channels(self, guild, channel_name, roles):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            roles[0]: discord.PermissionOverwrite(read_messages=True),
            roles[1]: discord.PermissionOverwrite(read_messages=True),
            discord.utils.get(guild.roles, name=self.bot.user.name): discord.PermissionOverwrite(read_messages=True)
        }
        category = await guild.create_category(name=channel_name, overwrites=overwrites)

        await asyncio.gather(
            guild.create_text_channel(name=channel_name + '-text', category=category, sync_permissions=True),
            guild.create_voice_channel(name=channel_name + '-voice', category=category, sync_permissions=True)
        )

    @commands.command(name='delete', help='$delete categoryname')
    @core.role_manager.admin_role_check()
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True,
                                        read_messages=True, send_messages=True)
    @commands.guild_only()
    async def delete_controller(self, ctx, category_name):
        await self.delete_roles(ctx.guild, category_name)
        await self.delete_channels(ctx.guild, category_name)

        await ctx.send('Roles and channels have been deleted.')

    @delete_controller.error
    async def delete_controller_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command only works on a server.')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('The bot needs at least all permissions requested from the invite link generated with '
                           + core.prefix_manager.prefix(ctx) + 'invite')
        elif isinstance(error, commands.CheckFailure):
            await ctx.send('Only User with the role ' + core.role_manager.admin_role(ctx) + ' can use this '
                                                                                            'command.')
        else:
            await ctx.send('Something went wrong please try again.')

    async def delete_roles(self, guild, role_name):
        await asyncio.gather(
            discord.utils.get(guild.roles, name=role_name + leader_string).delete(),
            discord.utils.get(guild.roles, name=role_name + member_string).delete()
        )

    async def delete_channels(self, guild, role_name):
        category_channel = discord.utils.get(guild.channels, name=role_name)
        await asyncio.gather(
            category_channel.channels[0].delete(),
            category_channel.channels[1].delete()
        )
        await category_channel.delete()

    @commands.command(name='add', help='$add @User @Role')
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True,
                                        read_messages=True, send_messages=True)
    @commands.guild_only()
    async def add_member_to_role(self, ctx, member: commands.MemberConverter, role: commands.RoleConverter):
        leader_role = role.name.split()[0] + leader_string
        if discord.utils.get(ctx.author.roles, name=leader_role) is None:
            raise commands.MissingRole(leader_role)

        await member.add_roles(discord.utils.get(ctx.guild.roles, name=role.name.split()[0] + member_string))
        await ctx.send('Role added to user.')

    @add_member_to_role.error
    async def add_member_to_role_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command only works on a server.')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('The bot needs at least all permissions requested from the invite link generated with '
                           + core.prefix_manager.prefix(ctx) + 'invite')
        elif isinstance(error, commands.MissingRole):
            await ctx.send('To add this role you need to have the role ' + error.missing_role + '.')
        else:
            await ctx.send('Something went wrong please try again.')

    @commands.command(name='remove', help='$remove @User @Role')
    @commands.bot_has_guild_permissions(manage_channels=True, manage_roles=True,
                                        read_messages=True, send_messages=True)
    @commands.guild_only()
    async def remove_member_from_role(self, ctx, member: commands.MemberConverter, role: commands.RoleConverter):
        leader_role = role.name.split()[0] + leader_string
        if discord.utils.get(ctx.author.roles, name=leader_role) is None:
            raise commands.MissingRole(leader_role)

        await member.remove_roles(discord.utils.get(ctx.guild.roles, name=role.name.split()[0] + member_string))
        await ctx.send('Role removed from user.')

    @remove_member_from_role.error
    async def remove_member_from_role_error(self, ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send('This command only works on a server.')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send('The bot needs at least all permissions requested from the invite link generated with '
                           + core.prefix_manager.prefix(ctx) + 'invite')
        elif isinstance(error, commands.MissingRole):
            await ctx.send('To remove this role you need to have the role ' + error.missing_role + '.')
        else:
            await ctx.send('Something went wrong please try again.')
