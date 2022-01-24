"""
Top level models
"""

from django.contrib.auth.models import Permission, User
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import EveEntity, EveSolarSystem, EveType

from allianceauth.eveonline.evelinks import dotlan, evewho
from allianceauth.services.hooks import get_extension_logger
from app_utils.django import users_with_permission
from app_utils.logging import LoggerAddTag

from .. import __title__
from ..managers.general import (
    EveShipTypeManger,
    EveSkillTypeManger,
    LocationManager,
    MailEntityManager,
)
from .constants import NAMES_MAX_LENGTH

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class General(models.Model):
    """Meta model for user permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            (
                "basic_access",
                "Can access this app, register, and view own characters",
            ),
            ("share_characters", "Can share his/her characters"),
            ("finder_access", "Can access character finder feature"),
            ("reports_access", "Can access reports feature"),
            ("characters_access", "Can view characters owned by others"),
            ("exports_access", "Can access data exports"),
            ("view_shared_characters", "Can view shared characters"),
            ("view_same_corporation", "Can view corporation characters"),
            ("view_same_alliance", "Can view alliance characters"),
            ("view_everything", "Can view all characters"),
        )

    @classmethod
    def basic_permission(cls):
        """return basic permission needed to use this app"""
        return Permission.objects.select_related("content_type").get(
            content_type__app_label=cls._meta.app_label, codename="basic_access"
        )

    @classmethod
    def users_with_basic_access(cls) -> models.QuerySet:
        return users_with_permission(cls.basic_permission())

    @classmethod
    def accessible_users(cls, user: User) -> models.QuerySet:
        """users that the given user can access"""
        if user.has_perm("memberaudit.view_everything"):
            return cls.users_with_basic_access()
        elif (
            user.has_perm("memberaudit.view_same_alliance")
            and user.profile.main_character.alliance_id
        ):
            return cls.users_with_basic_access().filter(
                profile__main_character__alliance_id=user.profile.main_character.alliance_id
            )
        elif user.has_perm("memberaudit.view_same_corporation"):
            return cls.users_with_basic_access().filter(
                profile__main_character__corporation_id=user.profile.main_character.corporation_id
            )
        return User.objects.filter(pk=user.pk)


class Location(models.Model):
    """An Eve Online location: Station or Upwell Structure or Solar System"""

    _SOLAR_SYSTEM_ID_START = 30_000_000
    _SOLAR_SYSTEM_ID_END = 33_000_000
    _STATION_ID_START = 60_000_000
    _STATION_ID_END = 64_000_000
    _STRUCTURE_ID_START = 1_000_000_000_000

    id = models.PositiveBigIntegerField(
        primary_key=True,
        help_text=(
            "Eve Online location ID, "
            "either item ID for stations or structure ID for structures"
        ),
    )
    name = models.CharField(
        max_length=NAMES_MAX_LENGTH,
        help_text="In-game name of this station or structure",
    )
    eve_solar_system = models.ForeignKey(
        EveSolarSystem,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
    )
    eve_type = models.ForeignKey(
        EveType,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
    )
    owner = models.ForeignKey(
        EveEntity,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
        help_text="corporation this station or structure belongs to",
    )
    updated_at = models.DateTimeField(auto_now=True)

    objects = LocationManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return "{}(id={}, name='{}')".format(
            self.__class__.__name__, self.id, self.name
        )

    @property
    def name_plus(self) -> str:
        """return the actual name or 'Unknown location' for empty locations"""
        if self.is_empty:
            return f"Unknown location #{self.id}"

        return self.name

    @property
    def is_empty(self) -> bool:
        return not self.eve_solar_system and not self.eve_type

    @property
    def solar_system_url(self) -> str:
        """returns dotlan URL for this solar system"""
        try:
            return dotlan.solar_system_url(self.eve_solar_system.name)
        except AttributeError:
            return ""

    @property
    def is_solar_system(self) -> bool:
        return self.is_solar_system_id(self.id)

    @property
    def is_station(self) -> bool:
        return self.is_station_id(self.id)

    @property
    def is_structure(self) -> bool:
        return self.is_structure_id(self.id)

    @classmethod
    def is_solar_system_id(cls, location_id: int) -> bool:
        return cls._SOLAR_SYSTEM_ID_START <= location_id <= cls._SOLAR_SYSTEM_ID_END

    @classmethod
    def is_station_id(cls, location_id: int) -> bool:
        return cls._STATION_ID_START <= location_id <= cls._STATION_ID_END

    @classmethod
    def is_structure_id(cls, location_id: int) -> bool:
        return location_id >= cls._STRUCTURE_ID_START


class EveShipType(EveType):
    """Subset of EveType for all ship types"""

    class Meta:
        proxy = True

    objects = EveShipTypeManger()


class EveSkillType(EveType):
    """Subset of EveType for all skill types"""

    class Meta:
        proxy = True

    objects = EveSkillTypeManger()


class SkillSetGroup(models.Model):
    """A group of SkillSets, e.g. for defining a doctrine"""

    name = models.CharField(max_length=NAMES_MAX_LENGTH, unique=True)
    description = models.TextField(blank=True)
    skill_sets = models.ManyToManyField("SkillSet", related_name="groups")
    is_doctrine = models.BooleanField(
        default=False,
        db_index=True,
        help_text=(
            "This enables a skill set group to show up correctly in doctrine reports"
        ),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this skill set group is in active use",
    )

    def __str__(self) -> str:
        return str(self.name)

    @property
    def name_plus(self) -> str:
        return "{}{}".format(_("Doctrine: ") if self.is_doctrine else "", self.name)


class SkillSet(models.Model):
    """A set of required and recommended skills needed to perform
    a particular task like flying a doctrine ships
    """

    name = models.CharField(max_length=NAMES_MAX_LENGTH, unique=True)
    description = models.TextField(blank=True)
    ship_type = models.ForeignKey(
        EveShipType,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
        help_text=(
            "Ship type is used for visual presentation only. "
            "All skill requirements must be explicitly defined."
        ),
    )
    is_visible = models.BooleanField(
        default=True,
        db_index=True,
        help_text=(
            "Non visible skill sets are not shown to users "
            "on their character sheet and used for audit purposes only."
        ),
    )

    def __str__(self) -> str:
        return str(self.name)


class SkillSetSkill(models.Model):
    # A specific skill within a skill set

    skill_set = models.ForeignKey(
        SkillSet, on_delete=models.CASCADE, related_name="skills"
    )
    eve_type = models.ForeignKey(
        EveSkillType, on_delete=models.CASCADE, verbose_name="skill", related_name="+"
    )

    required_level = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    recommended_level = models.PositiveIntegerField(
        default=None,
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["skill_set", "eve_type"],
                name="functional_pk_skillsetskill",
            )
        ]

    def __str__(self) -> str:
        return f"{self.skill_set}-{self.eve_type}"


class MailEntity(models.Model):
    """A sender or recipient in a mail"""

    class Category(models.TextChoices):
        ALLIANCE = "AL", _("Alliance")
        CHARACTER = "CH", _("Character")
        CORPORATION = "CO", _("Corporation")
        MAILING_LIST = "ML", _("Mailing List")
        UNKNOWN = "UN", _("Unknown")

        @classmethod
        def eve_entity_compatible(cls) -> set:
            return {cls.ALLIANCE, cls.CHARACTER, cls.CORPORATION}

    id = models.PositiveIntegerField(primary_key=True)
    category = models.CharField(
        max_length=2, choices=Category.choices, db_index=True
    )  # mandatory
    name = models.CharField(max_length=255, db_index=True)  # optional

    objects = MailEntityManager()

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(id={self.id}, category={self.category}, "
            f"name='{self.name}')"
        )

    @property
    def name_plus(self) -> str:
        """returns the name if defined or a generatic name based on category and ID"""
        return self.name if self.name else f"{self.get_category_display()} #{self.id}"

    @property
    def eve_entity_categories(self) -> set:
        """categories which also exist for EveEntity"""
        return {
            self.Category.ALLIANCE,
            self.Category.CHARACTER,
            self.Category.CORPORATION,
        }

    def save(self, *args, **kwargs):
        if not self.category:
            raise ValidationError("You must specify a category")

        super().save(*args, **kwargs)

    def external_url(self) -> str:
        """returns URL for to show details of this entity on external website"""
        if self.category == self.Category.ALLIANCE and self.name:
            return dotlan.alliance_url(self.name)

        elif self.category == self.Category.CHARACTER:
            return evewho.character_url(self.id)

        elif self.category == self.Category.CORPORATION and self.name:
            return dotlan.corporation_url(self.name)

        else:
            return ""
