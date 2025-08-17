import os
import re
import shlex
import asyncio
import traceback
from typing import Tuple
from telethon import events
from llyod import app, logger
from llyod.config import SAUCE_KEY
from telethon.tl.custom.button import Button
from telethon.tl.custom.message import Message
from pysaucenao import SauceNao

saucenao = SauceNao(api_key=SAUCE_KEY, min_similarity=60, results_limit=2)
media_types = (".jpeg", ".jpg", ".png", ".gif", ".webp", ".mp4")


@app.on(
    events.NewMessage(pattern=r"^[/!][Ss][Aa][Uu][Cc][Ee](@LlyodFronteraBot)?(\s.*)?")
)
async def get_sauce(event: Message):
    args = event.raw_text.split(" ", 1)
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply.media:
            try:
                media = await reply.download_media()
                if media.endswith(".mp4"):
                    new_media = media.replace("mp4", "gif")
                    await runcmd(f"ffmpeg -y -i {media} {new_media}")
                    os.remove(media)
                    media = new_media
            except:
                await event.reply("Reply to an image or send an url with it. eg. `/sauce <image url>`")
                return
        else:
            await event.reply("Reply to an image or send an url with it. eg. `/sauce <image url>`")
            return

    elif len(args) == 2:
        if args[1].endswith(media_types):
            media = args[1]
        else:
            await event.reply("Reply to an image or send an url with it. eg. `/sauce <image url>`")
            return
    else:
        await event.reply("Reply to an image or send an url with it. eg. `/sauce <image url>`")
        return

    tm = await event.reply("`Searching for sauce...🍝`")
    msg = ""
    btns = []

    try:
        if os.path.isfile(media):
            results = await saucenao.from_file(media)
        else:
            results = await saucenao.from_url(media)

        if results:
            result = results[0]  # take the top result
            msg += f"**Title:** {result.title or 'Unknown'}\n"
            msg += f"**Similarity:** `{result.similarity}%`\n"

            if result.author_name:
                msg += f"**Author/Artist:** `{result.author_name}`\n"

            if hasattr(result, "episode") and result.episode:
                msg += f"**Episode:** {result.episode}\n"
            if hasattr(result, "year") and result.year:
                msg += f"**Year:** {result.year}\n"
            if hasattr(result, "timestamp") and result.timestamp:
                msg += f"**Timestamp:** {result.timestamp}\n"

            if result.urls:
                for url in result.urls:
                    url_name = re.search(r"https://(.*?)/", url)
                    names = url_name.group(1).split(".")
                    name = (
                        names[1] if len(names) > 2 and names[0] == "www" else names[0]
                    )
                    btns.append(Button.url(name.replace("yande", "yandere").capitalize(), url))

            # optional: check for second best match
            if len(results) > 1:
                second = results[1]
                if second.similarity >= 80 and second.urls:
                    msg += f"\n**Alt match:** {second.title or 'Unknown'} ({second.similarity}%)"
                    for url in second.urls:
                        url_name = re.search(r"https://(.*?)/", url)
                        names = url_name.group(1).split(".")
                        name = (
                            names[1] if len(names) > 2 and names[0] == "www" else names[0]
                        )
                        btns.append(Button.url(name.capitalize(), url))
        else:
            msg += "**No results found.**"

    except Exception:
        logger.error(traceback.format_exc())
        msg += "**Error:** `API ERROR TRY AGAIN LATER`"

    if btns:
        await tm.edit(msg, buttons=btns)
    else:
        await tm.edit(msg)

    try:
        if os.path.isfile(media):
            os.remove(media)
    except:
        pass


async def runcmd(cmd: str) -> Tuple[str, str, int, int]:
    """run command in terminal"""
    args = shlex.split(cmd)
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        stdout.decode("utf-8", "replace").strip(),
        stderr.decode("utf-8", "replace").strip(),
        process.returncode,
        process.pid,
    )
