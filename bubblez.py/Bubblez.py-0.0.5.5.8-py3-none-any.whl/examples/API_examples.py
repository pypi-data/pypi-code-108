from Bubblez import Bubblez

client = Bubblez("your token", verbose=True or False, use_canary=True or False)

def User():
    "Check the token and get the data!"
    client.user.check()

    "Get a user with there/your username!"
    client.user.get(username="Username")

    "Set the status online on https://bubblez.app/"
    client.user.ping()


def Post():

    """
    Sending a Post!
        message: `str` The messag in a post!
        from_: `str` The little message next to the date send!
        locked: `bool` If True, no-one can reply than!
        nsfw: `bool` If set, User without Date of Birth or nsfw set cannot see it!
    """
    client.post.send(
        message="The Best message",
        from_="This is a little message next to the post date!",
        locked=True or False,
        nsfw=True or False
    )
    
    """
    Get a Post!            
        postid: `int` The post id!
    """
    client.post.get(
        postid=123
    )

    """
    Get the latest post!
        id_only: `bool` If True, it will only return the post_id, else it will return a Post Object 
    """
    client.post.get_latest(
        id_only=True or False
    )

    """
    Lock or unlock a Post!
        postid: `int` The post id
        togglelock: `bool` True, than no-one can reply
    """
    client.post.lock()
    client.post.unlock()
    
    """
    Delete a Post!
        postid: `int` A post id!
    """
    client.post.delete()


def Reply():

    """
    Delete a Reply!
        replyid: `int` The reply id
    """
    client.reply.delete()

    """
    Edit a Reply!
        replyid: `int` The reply id
        message: `str` The messge in the reply
    """
    client.reply.edit()

    """
    Sending a Reply!
        message: `str` The message in a Reply!
        from_: `str` The little message next to the date send!
        nsfw: `bool` If set, User without Date of Birth or nsfw set cannot see it!
    """
    client.reply.send()


def Devlog():
    """ 
    Get the latest Devlog 
    """
    client.devlog.get_latest()

