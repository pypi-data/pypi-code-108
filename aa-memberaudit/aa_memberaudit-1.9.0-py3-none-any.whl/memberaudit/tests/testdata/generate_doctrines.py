# flake8: noqa
"""
This is a standalone scripts that generates test doctrines complete with ships and skills
"""

import inspect
import os
import sys

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
myauth_dir = (
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(currentdir))))
    + "/myauth"
)
sys.path.insert(0, myauth_dir)


import django
from django.apps import apps

# init and setup django project
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myauth.settings.local")
django.setup()

if not apps.is_installed("memberaudit"):
    raise RuntimeError("The app memberaudit is not installed")

from eveuniverse.models import EveType

from memberaudit.models import SkillSet, SkillSetGroup, SkillSetSkill


def get_or_create_esi_or_none(EveModel, id) -> object:
    obj, _ = EveModel.objects.get_or_create_esi(id=id)
    return obj


print("Generating test doctrines...")


doctrine, _ = SkillSetGroup.objects.update_or_create(
    name="Test SkillSetGroup Subcaps",
    is_doctrine=True,
    defaults={"description": "Generated doctrine for testing"},
)
doctrine.skill_sets.clear()
machariel, _ = SkillSet.objects.update_or_create(
    name="Machariel", defaults={"ship_type": get_or_create_esi_or_none(EveType, 17738)}
)
doctrine.skill_sets.add(machariel)
SkillSetSkill.objects.update_or_create(
    skill_set=machariel,
    eve_type=get_or_create_esi_or_none(EveType, 3336),  # Gallente Battleship
    defaults={"required_level": 3, "recommended_level": 4},
)
SkillSetSkill.objects.update_or_create(
    skill_set=machariel,
    eve_type=get_or_create_esi_or_none(EveType, 3337),  # Minmatar Battleship
    defaults={"required_level": 3, "recommended_level": 4},
)
SkillSetSkill.objects.update_or_create(
    skill_set=machariel,
    eve_type=get_or_create_esi_or_none(
        EveType, 12209
    ),  # Large Autocannon Specialization
    defaults={"required_level": 3, "recommended_level": 5},
)
guardian, _ = SkillSet.objects.update_or_create(
    name="Guardian", defaults={"ship_type": get_or_create_esi_or_none(EveType, 11987)}
)
doctrine.skill_sets.add(guardian)
SkillSetSkill.objects.update_or_create(
    skill_set=guardian,
    eve_type=get_or_create_esi_or_none(EveType, 12096),  # Logistics Cruisers
    defaults={"required_level": 5},
)
SkillSetSkill.objects.update_or_create(
    skill_set=guardian,
    eve_type=get_or_create_esi_or_none(EveType, 3335),  # Amarr Cruiser
    defaults={"required_level": 5},
)
SkillSetSkill.objects.update_or_create(
    skill_set=guardian,
    eve_type=get_or_create_esi_or_none(EveType, 16069),  # Remote Armor Repair Systems
    defaults={"required_level": 3, "recommended_level": 5},
)
SkillSetSkill.objects.update_or_create(
    skill_set=guardian,
    eve_type=get_or_create_esi_or_none(EveType, 16069),  # Capacitor Emission Systems
    defaults={"required_level": 3, "recommended_level": 5},
)

doctrine, _ = SkillSetGroup.objects.update_or_create(
    name="Test SkillSetGroup Caps",
    is_doctrine=True,
    defaults={"description": "Generated doctrine for testing"},
)
doctrine.skill_sets.clear()
archon, _ = SkillSet.objects.update_or_create(
    name="Archon", defaults={"ship_type": get_or_create_esi_or_none(EveType, 23757)}
)
doctrine.skill_sets.add(archon)
SkillSetSkill.objects.update_or_create(
    skill_set=archon,
    eve_type=get_or_create_esi_or_none(EveType, 24311),  # Amarr Carrier
    defaults={"required_level": 3},
)
SkillSetSkill.objects.update_or_create(
    skill_set=archon,
    eve_type=get_or_create_esi_or_none(EveType, 20533),  # Capital Ships
    defaults={"required_level": 3},
)
SkillSetSkill.objects.update_or_create(
    skill_set=archon,
    eve_type=get_or_create_esi_or_none(EveType, 21611),  # Jump Drive Calibration
    defaults={"required_level": 4, "recommended_level": 5},
)

print("Completed.")
