# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ

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

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\nSend /upload to start.</b>")

@bot.on_message(filters.command(["upload"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('𝕤ᴇɴᴅ ᴛxᴛ ғɪʟᴇ ⚡️')
    input_msg = await bot.listen(editable.chat.id)
    x = await input_msg.download()
    await input_msg.delete(True)

    try:
        with open(x, "r") as f:
            content = f.read().splitlines()
        links = []
        for line in content:
            if "://" in line:
                # নাম এবং লিঙ্ক আলাদা করার সঠিক পদ্ধতি
                parts = line.split(":", 1)
                name_part = parts[0].strip()
                url_part = parts[1].strip()
                if url_part.startswith("//"):
                    url_part = "https:" + url_part
                links.append((name_part, url_part))
        os.remove(x)
    except Exception as e:
        await m.reply_text(f"Invalid File: {e}")
        return

    await editable.edit(f"**Total links:** {len(links)}\nSend start index (1, 2...)")
    start_input = await bot.listen(editable.chat.id)
    count = int(start_input.text)

    await editable.edit("**Batch Name:**")
    batch_input = await bot.listen(editable.chat.id)
    batch_name = batch_input.text

    await editable.edit("**Resolution:** (144, 360, 720)")
    res_input = await bot.listen(editable.chat.id)
    raw_res = res_input.text

    await editable.edit("**Thumb URL or 'no'**")
    thumb_input = await bot.listen(editable.chat.id)
    thumb_url = thumb_input.text
    thumb = "no"
    if thumb_url.startswith("http"):
        getstatusoutput(f"wget '{thumb_url}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"

    await editable.delete()

    for i in range(count - 1, len(links)):
        try:
            name1 = re.sub(r'[^\w\s]', '', links[i][0].strip())
            name = f'{str(count).zfill(3)}) {name1[:50]}'.strip()
            url = links[i][1]

            # YouTube-এর জন্য স্পেশাল হ্যান্ডলিং যাতে এরর না আসে
            if "youtu" in url:
                ytf = f"b[height<={raw_res}][ext=mp4]/bv[height<={raw_res}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_res}]/bv+ba/b"

            # কমান্ডে --no-warnings যোগ করা হয়েছে স্ট্রিং এরর এড়াতে
            cmd = f'yt-dlp --no-check-certificate --no-warnings --user-agent "Mozilla/5.0" -f "{ytf}" "{url}" -o "{name}.mp4"'

            cc = f'**[📽️] Vid_ID:** {str(count).zfill(3)}. {name1}\n**Batch:** {batch_name}'

            if ".pdf" in url:
                os.system(f'yt-dlp -o "{name}.pdf" "{url}"')
                await bot.send_document(m.chat.id, f'{name}.pdf', caption=cc)
                os.remove(f'{name}.pdf')
            else:
                prog = await m.reply_text(f"**Downloading:** {name}")
                # helper.download_video তে এরর হ্যান্ডলিং যোগ করা হয়েছে
                try:
                    res_file = await helper.download_video(url, cmd, name)
                    await helper.send_vid(bot, m, cc, res_file, thumb, name, prog)
                except Exception as e:
                    await m.reply_text(f"**Error Downloading {name}:**\nYouTube blocked the request or file not found.")
                await prog.delete()

            count += 1
            time.sleep(2)
        except Exception as e:
            await m.reply_text(f"**Skipped ID {count} due to error.**")
            count += 1
            continue

    await m.reply_text("✅ Done!")

bot.run()
