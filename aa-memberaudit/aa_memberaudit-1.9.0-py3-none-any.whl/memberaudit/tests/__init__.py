from typing import Tuple

from django.contrib.auth.models import User
from esi.models import Token

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter
from allianceauth.tests.auth_utils import AuthUtils
from app_utils.testing import add_character_to_user

from ..models import Character


def create_user_from_evecharacter_with_access(
    character_id: int,
) -> Tuple[User, CharacterOwnership]:
    auth_character = EveCharacter.objects.get(character_id=character_id)
    user = AuthUtils.create_user(auth_character.character_name)
    user = AuthUtils.add_permission_to_user_by_name("memberaudit.basic_access", user)
    character_ownership = add_character_to_user(
        user, auth_character, is_main=True, scopes=Character.get_esi_scopes()
    )
    return user, character_ownership


def create_memberaudit_character(character_id: int) -> Character:
    _, character_ownership = create_user_from_evecharacter_with_access(character_id)
    return Character.objects.create(character_ownership=character_ownership)


def add_auth_character_to_user(
    user: User, character_id: int, scopes=None
) -> CharacterOwnership:
    auth_character = EveCharacter.objects.get(character_id=character_id)
    if not scopes:
        scopes = Character.get_esi_scopes()

    return add_character_to_user(user, auth_character, is_main=False, scopes=scopes)


def add_memberaudit_character_to_user(user: User, character_id: int) -> Character:
    character_ownership = add_auth_character_to_user(user, character_id)
    return Character.objects.create(character_ownership=character_ownership)


def scope_names_set(token: Token) -> set:
    return set(token.scopes.values_list("name", flat=True))
