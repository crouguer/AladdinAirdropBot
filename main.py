import discord
import os
import re
import gspread
import json
import neversleep

client = discord.Client()
keyfile_dict = json.loads(os.getenv('SVC_ACCT_KEY'))
gc = gspread.service_account_from_dict(keyfile_dict)
sheet = gc.open("Airdrop Addresses").sheet1


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def parse_address(message):
    match = re.match("^0x[a-fA-F0-9]{40}$", message)
    if (match):
        return match.group(0)
    else:
        raise Exception("Bad address format")


def store_to_sheets(uid, name, address):
    # Check to see if there is an entry for this user id
    cell = sheet.find(str(uid), in_column=1)
    updated = False

    #Update existing entry for this user id
    if cell is not None:
        sheet.update_cell(cell.row, 1, str(uid))
        sheet.update_cell(cell.row, 2, name)
        sheet.update_cell(cell.row, 3, address)
        updated = True

    # This is a new user id
    else:
        sheet.insert_row([str(uid), name, address], 2)

    return updated


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!rub'):
        displayname = message.author.name
        id = message.author.id

        if len(message.content[4:].strip()) == 0:
            await message.channel.send(
                "You must tell me your Ethereum address, {}!".format(
                    displayname),
                reference=message)
            return

        try:
            address = parse_address(message.content[4:].strip())
        except:
            await message.channel.send(
                "I FROWN upon on your malformed Ethereum address, {}".format(
                    displayname),
                reference=message)
            return

        try:
            updated = store_to_sheets(id, displayname, address)
            print("Airdrop: {} ({}): {}".format(displayname, id, address))
        except:
            # Notify user that it's failed... maybe also notify admin
            print("Failed to register recipient in sheets {} ({}), {}".format(displayname, id, address))
            await message.channel.send("I have failed you.", reference=message)

        if updated:
            await message.channel.send(
                "Your wish will be granted, replacing your previous wish, {}!".
                format(displayname),
                reference=message)
        else:
            await message.channel.send(
                "Your wish will be granted.  Magical airdrop awaits you, {}!".
                format(displayname),
                reference=message)


neversleep.awake("https://AladdinAirdropBot.crouguer.repl.co", False)
client.run(os.getenv('TOKEN'))
