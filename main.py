# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)


@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\n\n I Am A Bot For Download Links From Your **.TXT** File And Then Upload That File On Telegram. Use /upload Command.</b>")


@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):
    await m.reply_text("**Stopped**🚦", True)
    os.execl(sys.executable, sys.executable, *sys.argv)



@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('𝕤ᴇɴᴅ ᴛxᴛ ғɪʟᴇ ⚡️')
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)

    try:
        with open(x, "r") as f:
            content = f.read()
        content = content.split("\n")
        links = []
        for line in content:
            if "://" in line:
                parts = line.split(":", 1)
                name_part = parts[0].strip()
                url_part = "https:" + parts[1].strip() if not parts[1].strip().startswith("http") else parts[1].strip()
                links.append((name_part, url_part))
        os.remove(x)
    except Exception as e:
        await m.reply_text(f"**Invalid file format.**\nError: {e}")
        return
    
    await editable.edit(f"**Total links found: {len(links)}**\nSend starting number (e.g. 1)")
    input0: Message = await bot.listen(editable.chat.id)
    raw_text = input0.text
    await input0.delete(True)

    await editable.edit("**Send Batch Name**")
    input1: Message = await bot.listen(editable.chat.id)
    raw_text0 = input1.text
    await input1.delete(True)

    await editable.edit("**Enter Resolution** (144, 360, 720, etc.)")
    input2: Message = await bot.listen(editable.chat.id)
    raw_text2 = input2.text
    await input2.delete(True)
    
    await editable.edit("**Enter Caption** (or send 'no')")
    input3: Message = await bot.listen(editable.chat.id)
    raw_text3 = input3.text
    await input3.delete(True)
    MR = "" if raw_text3.lower() == 'no' else raw_text3
   
    await editable.edit("**Send Thumbnail URL** (or send 'no')")
    input6 = await bot.listen(editable.chat.id)
    thumb_url = input6.text
    await input6.delete(True)
    await editable.delete()

    thumb = "no"
    if thumb_url.startswith("http"):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"

    count = int(raw_text)

    for i in range(count - 1, len(links)):
        try:
            name1 = re.sub(r'[^\w\s]', '', links[i][0].strip())
            name = f'{str(count).zfill(3)}) {name1[:50]}'.strip()
            url = links[i][1]

            # YouTube handling to avoid bot detection
            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            # Adding --no-check-certificate and user-agent to bypass some blocks
            cmd = f'yt-dlp --no-check-certificate --user-agent "Mozilla/5.0" -f "{ytf}" "{url}" -o "{name}.mp4"'

            cc = f'**[📽️] Vid_ID:** {str(count).zfill(3)}. {name1} {MR}\n**Batch:** {raw_text0}'
            
            if ".pdf" in url:
                os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc)
                os.remove(f'{name}.pdf')
            else:
                prog = await m.reply_text(f"**Downloading:** {name}")
                res_file = await helper.download_video(url, cmd, name)
                await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                await prog.delete()
            
            count += 1
            time.sleep(2)

        except Exception as e:
            await m.reply_text(f"**Error on ID {count}:**\n`{e}`\n**Link:** {url}")
            count += 1
            continue

    await m.reply_text("**Done Boss!**")

bot.run()
