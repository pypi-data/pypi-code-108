import discord
import json
from datetime import datetime


def jsonToEmbed(filePath):
    with open(filePath, "r") as f:
        data = json.load(f)

    def checkEntryExists(name, data):
        if name in data:
            return len(data[name]) > 0
        return False

    embeds = []
    for i, embed in enumerate(data["embeds"]):
        embeds.append(
            discord.Embed(
                title=str(embed["title"]) if checkEntryExists("title", embed) else "",
                description=str(embed["description"])
                if checkEntryExists("title", embed)
                else "",
                color=int(embed["color"])
                if checkEntryExists("color", embed)
                else 2895667,
                url=str(embed["url"]) if checkEntryExists("color", embed) else "",
            )
        )

        if checkEntryExists("fields", embed):
            for field in embed["fields"]:
                embeds[i].add_field(
                    name=str(field["name"]) if checkEntryExists("name", field) else "",
                    value=str(field["value"])
                    if checkEntryExists("value", field)
                    else "",
                    inline=bool(field["value"])
                    if checkEntryExists("value", field)
                    else False,
                )
        if checkEntryExists("author", embed):
            embeds[i].set_author(
                name=str(embed["author"]["name"])
                if checkEntryExists("name", embed["author"])
                else "",
                url=str(embed["author"]["url"])
                if checkEntryExists("url", embed["author"])
                else "",
                icon_url=str(embed["author"]["icon_url"])
                if checkEntryExists("icon_url", embed["author"])
                else "",
            )

        if checkEntryExists("thumbnail", embed):
            embeds[i].set_thumbnail(
                url=str(embed["thumbnail"]["url"])
                if checkEntryExists("url", embed["thumbnail"])
                else "",
            )

        if checkEntryExists("timestamp", embed):
            embeds[i].timestamp = (
                datetime.fromisoformat(str(embed["timestamp"])[:-1])
                if checkEntryExists("timestamp", embed)
                else ""
            )

        if checkEntryExists("image", embed):
            embeds[i].set_image(
                url=str(embed["image"]["url"])
                if checkEntryExists("url", embed["image"])
                else "",
            )
    return embeds
