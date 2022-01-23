CDN_BASE_URL = "https://cdn.discordapp.com"


def avatar_url(user):
    user_id, user_avatar = user["id"], user["avatar"]

    if user_avatar is None:
        index = int(user["discriminator"]) % 5

        return f"{CDN_BASE_URL}/embed/avatars/{index}.png"

    if user_avatar.startswith("a_"):
        return f"{CDN_BASE_URL}/avatars/{user_id}/{user_avatar}.gif"

    return f"{CDN_BASE_URL}/avatars/{user_id}/{user_avatar}.png"
