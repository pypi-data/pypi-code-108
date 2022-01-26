# flake8: noqa
"""scripts generates large amount of fat links for load testing

This script can be executed directly from shell.
"""

# Standard Library
import os
import sys
from pathlib import Path

myauth_dir = Path(__file__).parent.parent.parent.parent.parent / "myauth"
sys.path.insert(0, str(myauth_dir))

# Django
import django

# init and setup django project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings.local")
django.setup()

# Standard Library
import datetime as dt
import random

# Django
from django.contrib.auth.models import User
from django.utils.timezone import now

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth (External Libs)
from app_utils.helpers import random_string

# Alliance Auth AFAT
from afat.models import AFat, AFatLink, AFatLinkType, AFatLogEvent
from afat.tests.fixtures.utils import RequestStub
from afat.utils import write_log

LINKS_NUMBER = 1000


characters = list(EveCharacter.objects.all())
print(
    f"Adding {LINKS_NUMBER:,} FAT links "
    f"with up to {len(characters)} characters each"
)
user = User.objects.first()
creator = user.profile.main_character
link_type, _ = AFatLinkType.objects.get_or_create(name="Generated Fleet")
for _ in range(LINKS_NUMBER):
    fat_link = AFatLink.objects.create(
        fleet=f"Generated Fleet #{random.randint(1, 1000000000)}",
        hash=random_string(20),
        creator=user,
        character=creator,
        link_type=link_type,
        afattime=now() - dt.timedelta(days=random.randint(0, 180)),
    )
    write_log(
        request=RequestStub(user),
        log_event=AFatLogEvent.CREATE_FATLINK,
        log_text=(
            f'ESI FAT link with name "{fat_link.fleet}"'
            f"{link_type} was created by {user}"
        ),
        fatlink_hash=fat_link.hash,
    )
    for character in random.sample(characters, k=random.randint(1, len(characters))):
        AFat.objects.create(
            character_id=character.id,
            afatlink=fat_link,
            system="Jita",
            shiptype="Ibis",
        )
    print(".", end="", flush=True)


print("")
print("DONE")
