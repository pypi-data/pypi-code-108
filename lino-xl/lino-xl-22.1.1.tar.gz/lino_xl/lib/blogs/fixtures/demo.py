# -*- coding: UTF-8 -*-
# Copyright 2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import datetime as dt
from pathlib import Path

from django.conf import settings

from lino.api import rt, dd, _
from lino.core.gfks import gfk2lookup
from lino.modlib.uploads.mixins import make_uploaded_file

imgpath = Path(__file__).parent / "images"

def objects():
    Entry = rt.models.blogs.Entry

    robin = rt.models.users.User.objects.get(username='robin')
    demo_date = settings.SITE.the_demo_date

    title = "At the fork of the cross roads"
    body = """<div><p>Let's choose one or the other of the either roads (or NOT)!</p><p><br/></p><p>And the hasitation, does it comes rarely(?), Nooo!, we are very frequently and suddenly put to situations where we must choose between roads.</p><p><br/></p><p>Of course, how to choose and what to choose are the questions. But did we ever ask 'why?' But of course it depends on the context, let's not give it a context, let's talk abstract. 'Why?' is the question. Maybe to be like a stoic or something, not sure!</p><p><br/></p><p>The advice from a stoic would be to not choose but just hang around at the fork and not think about it at all, just try to be at peace, the hesitations aside.</p><p><br/></p><p>But no we have to make a choice, why? because, the world isn't going to wait for us! We have to make a choice and move along with the world, fast forward. We can deal with whatever comes.</p><p><br/></p><p>OTOH! sometimes it's not worth moving along, sometimes we can just sit at the fork and think through things, cars, engines, birds, rocket ships or the stars, really, anything at all, because it doesn't matter what about, anything will do, why not! thinking is fun, just living the fantasy that we forgot to live, the fantasies that engulped us when we were children, make a peace out of the fork, build a house on the fork, a house of fantasies, a house of the colors from the river on the night sky, a house of wind and the smell of dirt or grass, a house on no where, wouldn't that be fun!</p><p><br/></p><p>Here again comes the 'but', the other 'but', that is, you start to hear a calling from one of the roads, it's a call for you to continue along and at this point even though you are sure of the choice you need to make, it's not really a choice anymore, it has become the destiny, this is the path of your life, but you cannot make the choice, you cannot leave the fork, the house of no where! You have already fallen in love with the fork and the house, so why bother!</p><p><br/></p><p>This clinging nature to things is going to be the end of you. You wanted to be free, to live a life of a free spirit, and you always forget to be free, you always forget to think, you always forget to keep the fantasy alive, you always forget that wherever you are you can wrap yourself around with the house, because the house is of nowhere and you are always at the nowhere unless you make it a somewhere. Remember the difference between a nowhere and a somewhere, only then you will be able to not forget.</p><p><br/></p><p>On the path of becoming a stoic.</p></div>"""

    cross_roads = Entry(title=title, body=body, user=robin, pub_date=demo_date)
    yield cross_roads

    title = "Melancholy House"
    body = """<div><p>It was cursed and the occupant knew about the unholy nature of it. They wanted to get away from it but it never did allow them to do so until they were consumed by the unholy spirit of it. When they got out, all that remained of them was an empty shell. Sometimes you can here it screaming as it devours of the occupant, i think it wants to become the occupant, it's a jeolous beast, and the scream comes from the fact that - as the beast grows from the occupant it also grows in melancholy rediated from the occupant.</p></div>"""

    melancholy_house = Entry(title=title, body=body, user=robin, pub_date=demo_date - dt.timedelta(days=1))
    yield melancholy_house

    title = "A little too much to talk"
    body = """<div><p>We want to be quiet. Say to mine-self, let's be quiet and try to be quiet. But does that ever stops us from talking. It seems there's a little too many ways of talking. So, the talking never stops. Now a days everybody's talking and everybody's listening. Now we ask mine-self, what does that has to do with us(?)! in wonder!!!! So what everybody's talking! Let them talk but let us be quiet! But the thought, it just a thought, like so many other thoughts, one thought among unimaginably many thoughts, so it remains a thought, and we never really stop from being talking. Because this thought of being quiet has no significance at all among all those uncountably many thoughts. So, the world is living inside of us it seems, the whole universe is living inside of us. We cannot ignore the resemblence that this living universe has with the universe outside. They are both the same. Yogic or Stoic, where are the happinesses has gone where have the peace gone. It's all just empty words, empty thoughts, non of it has any significance. There's no peace on the inside nor on the outside to have the courage to give any weight to these thoughts or the words. We don't buy words anymore, we only buy junks because we all have become junkies. We have it all and at the same time nothing at all.</p><p><br/></p><p>What are you spreading, happiness or sadness? Why do you ask? Why should it matter what I am spreading? You might say for the betterment of the human race. Oh okay! Then what happened to the junkies(?), is my question.</p><p><br/></p><p>Yes, the peace, it has come only to disappear again. Now the eyes are shining bright only to become dry again. It a terbulant universe, the one on the inside, and the bandwidth of the spectras seems infinite, so many colors and the terbulance, every instance is a new color, only there's the lack of a single color that you might stare into in admire.</p><p><br/></p><p>Also, they never end.</p></div>"""

    bleeding_words = Entry(title=title, body=body, user=robin, pub_date=demo_date - dt.timedelta(days=2))
    yield bleeding_words

    if dd.is_installed('albums'):

        def insert_memo_command(obj, cmd):
            body = obj.body.split('<div>')[1]
            obj.body = "<div><p>" + cmd + "</p>" + body
            return obj

        File = rt.models.albums.File
        FileUsage = rt.models.albums.FileUsage

        def make_file_and_usage(name, description, copyright, blog):
            file_made = make_uploaded_file(name, imgpath / name, blog.pub_date)
            file = File(file=file_made, description=description, copyright=copyright)
            yield file
            yield FileUsage(
                file=file, **gfk2lookup(FileUsage.owner, blog), primary_image=True)

            # cmd = file.get_memo_command()
            #
            # yield insert_memo_command(blog, cmd)

        yield make_file_and_usage("crossroads.jpg", "A House beside crossroads",
            "Copyright 2010-2017 rarestohanean (pixabay.com user)", cross_roads)
        # source: https://pixabay.com/photos/crossroads-little-house-park-1951949/
        yield make_file_and_usage("melancholy_house.jpg", "The House",
            "Copyright - Bob Hickman (pinterest.com user@warhick1981)", melancholy_house)
        # source: https://www.pinterest.com/pin/526147168960097319/
        yield make_file_and_usage("bleeding_words.jpg", "Bleeding Words",
            "Copyright 2017 Gerd Altmann (pixabay.com user@geralt)", bleeding_words)
        # source: https://pixabay.com/illustrations/feedback-report-back-business-people-2990424/
