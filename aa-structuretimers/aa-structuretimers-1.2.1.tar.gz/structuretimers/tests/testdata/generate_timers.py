# flake8: noqa
"""scripts generates large amount of timers for load testing
"""

import os
import sys
from pathlib import Path

myauth_dir = Path(__file__).parent.parent.parent.parent.parent / "myauth"
sys.path.insert(0, str(myauth_dir))

import django
from django.apps import apps

# init and setup django project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings.local")
django.setup()

"""SCRIPT"""
import datetime as dt
import random
from pathlib import Path

# from django.contrib.auth.models import User
from django.utils.timezone import now
from eveuniverse.models import EveSolarSystem, EveType

from allianceauth.eveonline.models import EveCorporationInfo

from structuretimers.constants import EveCategoryId
from structuretimers.models import Timer

MAX_TIMERS = 20

structure_type_ids = EveType.objects.filter(
    eve_group__eve_category_id=EveCategoryId.STRUCTURE, published=True
).values_list("id", flat=True)
eve_solar_system_ids = EveSolarSystem.objects.values_list("id", flat=True)
owner_names = EveCorporationInfo.objects.values_list("corporation_name", flat=True)
for _ in range(MAX_TIMERS):
    Timer.objects.create(
        timer_type=random.choice([elem[0] for elem in Timer.Type.choices]),
        eve_solar_system_id=random.choice(eve_solar_system_ids),
        structure_type_id=random.choice(structure_type_ids),
        date=now()
        + dt.timedelta(days=random.randint(1, 100), hours=random.randint(0, 59)),
        structure_name=f"Generated Timer",
        objective=random.choice([elem[0] for elem in Timer.Objective.choices]),
        owner_name=random.choice(owner_names),
    )

print("DONE")
