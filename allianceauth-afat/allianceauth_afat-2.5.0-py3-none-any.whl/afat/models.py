"""
The models
"""

# Django
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _

# Alliance Auth
from allianceauth.eveonline.models import EveCharacter

# Alliance Auth AFAT
from afat.managers import AFatLinkManager, AFatManager


def get_sentinel_user() -> User:
    """
    Get user or create one
    :return:
    """

    return User.objects.get_or_create(username="deleted")[0]


def get_hash_on_save() -> str:
    """
    Get the slug
    :return:
    """

    fatlink_hash = get_random_string(length=30)

    while AFatLink.objects.filter(hash=fatlink_hash).exists():
        fatlink_hash = get_random_string(length=30)

    return fatlink_hash


class AFatLogEvent(models.TextChoices):
    """
    Choices for SRP Status
    """

    CREATE_FATLINK = "CR_FAT_LINK", _("FAT Link Created")
    CHANGE_FATLINK = "CH_FAT_LINK", _("FAT Link Changed")
    DELETE_FATLINK = "RM_FAT_LINK", _("FAT Link Removed")
    REOPEN_FATLINK = "RO_FAT_LINK", _("FAT Link Re-Opened")
    # CREATE_FAT = "CR_FAT", _("FAT Registered")
    DELETE_FAT = "RM_FAT", _("FAT Removed")
    MANUAL_FAT = "CR_FAT_MAN", _("Manual FAT Added")


class AaAfat(models.Model):
    """
    Meta model for app permissions
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AaAfat :: Meta
        """

        managed = False
        default_permissions = ()
        permissions = (
            # can access and register his own participation to a FAT link
            ("basic_access", "Can access the AFAT module"),
            # Can manage the FAT module
            # Has:
            #   » add_fatlink
            #   » change_fatlink
            #   » delete_fatlink
            #   » add_fat
            #   » delete_fat
            ("manage_afat", "Can manage the AFAT module"),
            # Can add a new FAT link
            ("add_fatlink", "Can create FAT Links"),
            # Can see own corp stats
            ("stats_corporation_own", "Can see own corporation statistics"),
            # Can see the stats of all corps
            ("stats_corporation_other", "Can see statistics of other corporations"),
            # Can view the modules log
            ("log_view", "Can view the modules log"),
        )
        verbose_name = "Alliance Auth AFAT"


# AFatLinkType Model (StratOp, ADM, HD etc)
class AFatLinkType(models.Model):
    """
    AFatLinkType
    """

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=254, help_text="Descriptive name of your fleet type"
    )

    is_enabled = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this fleet type is active or not",
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AFatLinkType :: Meta
        """

        default_permissions = ()
        verbose_name = "FAT Link Fleet Type"
        verbose_name_plural = "FAT Link Fleet Types"

    def __str__(self) -> str:
        return str(self.name)


# AFatLink Model
class AFatLink(models.Model):
    """
    AFatLink
    """

    afattime = models.DateTimeField(
        default=timezone.now, db_index=True, help_text="When was this FAT link created"
    )

    fleet = models.CharField(
        max_length=254,
        blank=False,
        default=None,
        help_text="The FAT link fleet name",
    )

    hash = models.CharField(
        max_length=254, db_index=True, unique=True, help_text="The FAT link hash"
    )

    creator = models.ForeignKey(
        User,
        related_name="+",
        on_delete=models.SET(get_sentinel_user),
        help_text="Who created the FAT link?",
    )

    character = models.ForeignKey(
        EveCharacter,
        related_name="+",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        help_text="Character this FAT link has been created with",
    )

    link_type = models.ForeignKey(
        AFatLinkType,
        related_name="+",
        on_delete=models.CASCADE,
        null=True,
        help_text="The FAT link fleet type, if it's set",
    )

    is_esilink = models.BooleanField(
        default=False,
        help_text="Whether this FAT link was created via ESI or not",
    )

    is_registered_on_esi = models.BooleanField(
        default=False,
        help_text="Whether this is an ESI fat link is registered on ESI or not",
    )

    esi_fleet_id = models.BigIntegerField(blank=True, null=True)

    reopened = models.BooleanField(
        default=False,
        help_text="Has this FAT link being re-opened?",
    )

    objects = AFatLinkManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AFatLink :: Meta
        """

        default_permissions = ()
        ordering = ("-afattime",)
        verbose_name = "FAT Link"
        verbose_name_plural = "FAT Links"

    def __str__(self) -> str:
        return f"{self.fleet} - {self.hash}"

    @transaction.atomic()
    def save(self, *args, **kwargs):
        """
        Add the hash on save
        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        """

        try:
            self.hash
        except ObjectDoesNotExist:
            self.hash = get_hash_on_save()
        super().save(*args, **kwargs)

    @property
    def number_of_fats(self):
        """
        Returns the number of registered FATs
        :return:
        :rtype:
        """

        return AFat.objects.filter(afatlink=self).count()


# ClickAFatDuration Model
class ClickAFatDuration(models.Model):
    """
    ClickAFatDuration
    """

    duration = models.PositiveIntegerField()
    fleet = models.ForeignKey(AFatLink, on_delete=models.CASCADE)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        ClickAFatDuration :: Meta
        """

        default_permissions = ()
        verbose_name = "FAT Duration"
        verbose_name_plural = "FAT Durations"


# AFat Model
class AFat(models.Model):
    """
    AFat
    """

    character = models.ForeignKey(
        EveCharacter,
        related_name="afats",
        on_delete=models.CASCADE,
        help_text="Character who registered this FAT",
    )

    afatlink = models.ForeignKey(
        AFatLink,
        related_name="afats",
        on_delete=models.CASCADE,
        help_text="The FAT link the character registered at",
    )

    system = models.CharField(
        max_length=100, null=True, help_text="The system the character is in"
    )

    shiptype = models.CharField(
        max_length=100,
        null=True,
        db_index=True,
        help_text="The ship the character was flying",
    )

    objects = AFatManager()

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AFat :: Meta
        """

        default_permissions = ()
        unique_together = (("character", "afatlink"),)
        verbose_name = "FAT"
        verbose_name_plural = "FATs"

    def __str__(self) -> str:
        return f"{self.afatlink} - {self.character}"


# ManualAFat Model
class ManualAFat(models.Model):
    """
    ManualAFat
    """

    creator = models.ForeignKey(
        User, related_name="+", on_delete=models.SET(get_sentinel_user)
    )
    afatlink = models.ForeignKey(AFatLink, related_name="+", on_delete=models.CASCADE)
    character = models.ForeignKey(
        EveCharacter, related_name="+", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        blank=True, null=True, help_text="Time this FAT has been added manually"
    )

    class Meta:  # pylint: disable=too-few-public-methods
        """
        ManualAFat :: Meta
        """

        default_permissions = ()
        verbose_name = "Manual FAT"
        verbose_name_plural = "Manual FATs"

    # Add property for getting the user for a character.
    def __str__(self) -> str:
        return f"{self.afatlink} - {self.character} ({self.creator})"


# AFat Log Model
class AFatLog(models.Model):
    """
    AFatLog
    """

    log_time = models.DateTimeField(default=timezone.now, db_index=True)
    user = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True,
        default=None,
        on_delete=models.SET(get_sentinel_user),
    )
    log_event = models.CharField(
        max_length=11,
        blank=False,
        choices=AFatLogEvent.choices,
        default=AFatLogEvent.CREATE_FATLINK,
    )
    log_text = models.TextField()
    fatlink_hash = models.CharField(max_length=254)

    class Meta:  # pylint: disable=too-few-public-methods
        """
        AFatLog :: Meta
        """

        default_permissions = ()
        verbose_name = "AFAT Log"
        verbose_name_plural = "AFAT Logs"
