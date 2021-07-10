import discord
from discord.ext import commands

import asyncio

import time
from timeloop import Timeloop
from datetime import timedelta

from pyzbar.pyzbar import decode
from PIL import Image
import requests

import base45
import zlib
import cbor2
import json
from cose.messages import CoseMessage
from datetime import datetime

import main
import core.globals
import core.role_manager
import core.prefix_manager
import core.permission_manager
import core.permission_enum

permissions = [core.permission_enum.PermissionEnum.read_messages.name,
               core.permission_enum.PermissionEnum.send_messages.name]

tl = Timeloop()


def setup(bot):
    core.permission_manager.add_permissions(permissions)
    bot.add_cog(Covid19(bot))
    create_table(core.globals.sql_connection)
    tl.start()
    print('Covid-19 is being loaded!')


def teardown(bot):
    core.permission_manager.remove_permissions(permissions)
    bot.remove_cog('Covid-19')
    tl.stop()
    print('Covid-19 is being unloaded')


# @tl.job(interval=timedelta(seconds=30))
def update_loop():
    connection = main.create_connection(main.sql_path)
    cur = connection.cursor()
    cur.execute("SELECT * FROM entry_test WHERE expiration_date<:expiration_date",
                {"expiration_date": int(time.time())})

    expired = cur.fetchall()
    asyncio.run(remove_expired_async(expired, cur, connection))
    connection.close()


async def remove_expired_async(expired, cur, connection):
    for row in expired:
        guild = discord.utils.get(main.bot.guilds, id=row[0])
        member = discord.utils.get(guild.members, id=row[1])
        if row[3] < 1:
            role_name = "Tested"
        else:
            role_name = "Vaccinated"

        await member.remove_roles(discord.utils.get(guild.roles, name=role_name))
        cur.execute("DELETE FROM entry_test WHERE  expiration_date<:expiration_date",
                    {"expiration_date": int(time.time())})
        connection.commit()


def qr_code_url_to_json(url):
    if url.endswith(".png") or url.endswith(".jpg"):
        image = Image.open(requests.get(url, stream=True).raw)
        qr_codes_data = decode(image)

        if qr_codes_data:
            return_json = []

            for qr_code_data_raw in qr_codes_data:
                qr_code_data = qr_code_data_raw.data.decode("utf-8")

                if qr_code_data[:4] == 'HC1:':
                    qr_code_data = qr_code_data[4:]

                base45_decoded_data = base45.b45decode(qr_code_data)
                zlib_decompressed_data = zlib.decompress(base45_decoded_data)
                cose_decoded_data = CoseMessage.decode(zlib_decompressed_data)
                raw_json_data = cbor2.loads(cose_decoded_data.payload)
                json_data = json.loads(json.dumps(raw_json_data))

                # convert unix time of expiration date to normal date time + rename
                json_data['4'] = datetime.utcfromtimestamp(int(json_data['4'])).strftime('%Y-%m-%d %H:%M:%S')
                json_data['expiration date'] = json_data.pop('4')

                # convert unix time of test date  to normal date time + rename
                json_data['6'] = datetime.utcfromtimestamp(int(json_data['6'])).strftime('%Y-%m-%d %H:%M:%S')
                json_data['issue date'] = json_data.pop('6')

                json_data['issuer country'] = json_data.pop('1')
                return_json.append(json_data)

            return return_json
        else:
            raise Exception('No QR-Code')
    else:
        raise Exception('Not right type')


def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
                            CREATE TABLE IF NOT EXISTS entry_test (
                            server INTEGER NOT NULL,
                            user INTEGER NOT NULL,
                            expiration_date INTEGER NOT NULL,
                            vaccinated INTEGER NOT NULL
                            );
                        """)
    connection.commit()


async def add_roll_to_member(guild, role_name, member):
    all_roles = await guild.fetch_roles()
    role = discord.utils.get(all_roles, name=role_name)

    if role is not None:
        await member.add_roles(role)
    else:
        await guild.create_role(name=role_name)
        all_roles = await guild.fetch_roles()
        await member.add_roles(discord.utils.get(all_roles, name=role_name))


class Covid19(commands.Cog, name='Covid-19'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='covid19_decoder', help='Attach picture of 3G-QR-Code in png or jpg format.')
    async def covid19_decoder(self, ctx):
        json_data = qr_code_url_to_json(ctx.message.attachments[0].url)

        for i in json_data:
            json_formatted = json.dumps(i, indent=2)
            await ctx.send('QR-Code Data:\n' + json_formatted)

    @covid19_decoder.error
    async def covid19_decoder_error(self, ctx, error):
        await ctx.send('The attached document needs to be a png or jpg and there must be 3G-QR-Code in the picture')

    @commands.command(name='covid19_entry_test', help='Attach picture of 3G-QR-Code in png or jpg format.')
    async def covid19_entry_test(self, ctx):
        json_data = qr_code_url_to_json(ctx.message.attachments[0].url)

        for i in json_data:
            if datetime.strptime(i["expiration date"], '%Y-%m-%d %H:%M:%S') > datetime.now():
                vaccinated = False
                if "-260" in i:
                    if "1" in i["-260"]:
                        if "v" in i["-260"]["1"]:
                            vaccinated = True

                connection = core.globals.sql_connection

                cur = connection.cursor()
                cur.execute("INSERT INTO entry_test (server,user,expiration_date,vaccinated) VALUES (?, ?, ?, ?)",
                            (ctx.guild.id, ctx.author.id,
                             datetime.strptime(i["expiration date"], '%Y-%m-%d %H:%M:%S').timestamp(), vaccinated))
                connection.commit()
                if vaccinated:
                    await add_roll_to_member(ctx.guild, "Vaccinated", ctx.author)
                    await ctx.send('Successfully added to the group of vaccinated.')
                else:
                    await add_roll_to_member(ctx.guild, "Tested", ctx.author)
                    await ctx.send('Successfully added to the group of tested.')
            else:
                await ctx.send('The 3G-QR-Code is not valid.')
