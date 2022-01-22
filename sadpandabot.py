import datetime
import os

import aiohttp
import asyncio
import simplematrixbotlib as botlib
from bs4 import BeautifulSoup

import ehapi

config = botlib.Config()
config.join_on_invite = True
creds = botlib.Creds(
    os.environ["HOMESERVER"], os.environ["USERNAME"], os.environ["PASSWORD"]
)
bot = botlib.Bot(creds, config=config)
bot._need_allow_homeserver_users = True
PREFIX = "!"
BASE = "https://cdn.discordapp.com/attachments/306823976615936002/"
G_CATEGORY = {
    "Doujinshi": BASE + "471642768180117524/doujinshi.png",
    "Manga": BASE + "471642771862716446/manga.png",
    "Artist CG": BASE + "471642764623478804/artistcg.png",
    "Game CG": BASE + "471642769169842176/gamecg.png",
    "Western": BASE + "471642775964745729/western.png",
    "Non-H": BASE + "471642774350069771/non-h.png",
    "Image Set": BASE + "471642770331926558/imageset.png",
    "Cosplay": BASE + "471642766993260544/cosplay.png",
    "Asian Porn": BASE + "471642765781106689/asianporn.png",
    "Misc": BASE + "471642773087322112/misc.png",
}


async def fetch_img(session, url):
    filename = "/tmp/" + url.split("/")[-1]
    timeout = aiohttp.ClientTimeout(total=60)
    async with session.get(url, timeout=timeout) as response:
        assert response.status == 200
        img = await response.read()
    with open(filename, "wb") as img_io:
        img_io.write(img)
    return filename


@bot.listener.on_startup
async def on_ready(room_id):
    print("------")
    print(f"Successfully logged in and booted in {room_id}...!")


@bot.listener.on_message_event
async def on_message(room, message):
    match = botlib.MessageMatch(room, message, bot, PREFIX)
    if match.is_not_from_this_bot() and not message.flattened().get(
        "content.m.relates_to.m.in_reply_to.event_id", False
    ):
        await parse_exlinks(message, room)


# search for EH links and post their metadata
async def parse_exlinks(message, room):
    galleries = ehapi.get_galleries(message.body)
    if galleries:
        logger(message, ", ".join([gallery["token"] for gallery in galleries]))
        if len(galleries) > 5:  # don't spam chat too much if user spams links
            await bot.api.send_text_message(room.room_id, embed_titles(galleries))
        else:
            for gallery in galleries:
                loop = asyncio.get_event_loop()
                async with aiohttp.ClientSession(loop=loop) as session:
                    img_fn = await fetch_img(session, gallery["thumb"])
                await bot.api.send_image_message(room.room_id, img_fn)
                os.remove(img_fn)
                await bot.api.send_markdown_message(room.room_id, embed_full(gallery))


# string of titles for lots of links
def embed_titles(exmetas):
    link_list = [
        create_markdown_url(
            exmeta["title"], create_ex_url(exmeta["gid"], exmeta["token"])
        )
        for exmeta in exmetas
    ]
    msg = "\n".join(link_list)
    return msg


# pretty discord embeds for small amount of links
def embed_full(exmeta):
    title = BeautifulSoup(exmeta["title"], "html.parser").string
    url = create_ex_url(exmeta["gid"], exmeta["token"])
    timestamp = datetime.datetime.utcfromtimestamp(int(exmeta["posted"]))
    description = BeautifulSoup(exmeta["title_jpn"], "html.parser").string
    # em.set_image(url=exmeta["thumb"]) # TODO find a way to send those images
    # em.set_thumbnail(url=G_CATEGORY[exmeta["category"]])
    # em.set_footer(text=exmeta["filecount"] + " pages")
    # em.add_field(name="rating", value=exmeta["rating"])
    # em = process_tags(em, exmeta["tags"])
    formatted_str = (
        f"__**[{title}]({url})**__\n*{timestamp}*\n{description if description else ''}"
    )
    formatted_str = process_tags(formatted_str, exmeta["tags"])
    return formatted_str


# put our tags from the EH JSON response into the discord embed
def process_tags(formatted_str, tags):
    tag_dict = {"male": [], "female": [], "parody": [], "character": [], "misc": []}
    for tag in tags:
        if ":" in tag:
            splitted = tag.split(":")
            if splitted[0] in tag_dict:
                tag_dict[splitted[0]].append(
                    BeautifulSoup(splitted[1], "html.parser").string
                )
        else:
            tag_dict["misc"].append(tag)

    for ex_tag in tag_dict:
        if tag_dict[ex_tag]:
            tags = f'\n**{ex_tag}**\n{", ".join(tag_dict[ex_tag])}'
            formatted_str += tags

    return formatted_str


# make a markdown hyperlink
def create_markdown_url(message, url):
    return "[" + BeautifulSoup(message, "html.parser").string + "](" + url + ")"


# make a EH url from it's gid and token
def create_ex_url(gid, g_token):
    return "https://exhentai.org/g/" + str(gid) + "/" + g_token + "/"


# crude, but using Docker so ¯\_(ツ)_/¯
def logger(message, contents):
    print(contents)


def main():
    print("Logging in...")
    bot.run()


if __name__ == "__main__":
    main()
