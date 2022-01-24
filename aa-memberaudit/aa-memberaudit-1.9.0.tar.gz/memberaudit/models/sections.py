"""
Character sections models
"""

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from eveuniverse.models import (
    EveAncestry,
    EveBloodline,
    EveEntity,
    EveFaction,
    EveRace,
    EveSolarSystem,
    EveType,
)

from allianceauth.services.hooks import get_extension_logger
from app_utils.logging import LoggerAddTag

from .. import __title__
from ..core.xml_converter import eve_xml_to_html
from ..managers.sections import (
    CharacterAssetManager,
    CharacterAttributesManager,
    CharacterContactLabelManager,
    CharacterContactManager,
    CharacterContractBidManager,
    CharacterContractItemManager,
    CharacterContractManager,
    CharacterCorporationHistoryManager,
    CharacterDetailsManager,
    CharacterImplantManager,
    CharacterJumpCloneManager,
    CharacterLocationManager,
    CharacterLoyaltyEntryManager,
    CharacterMailLabelManager,
    CharacterMailManager,
    CharacterShipManager,
    CharacterSkillManager,
    CharacterSkillqueueEntryManager,
    CharacterSkillSetCheckManager,
    CharacterWalletJournalEntryManager,
    CharacterWalletTransactionManager,
)
from .character import Character
from .constants import CURRENCY_MAX_DECIMALS, CURRENCY_MAX_DIGITS, NAMES_MAX_LENGTH
from .general import Location

logger = LoggerAddTag(get_extension_logger(__name__), __title__)


class CharacterAsset(models.Model):
    """An Eve Online asset belonging to a Character"""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="assets"
    )
    item_id = models.PositiveBigIntegerField()

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, default=None, null=True
    )
    parent = models.ForeignKey(
        "CharacterAsset",
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="children",
    )

    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")
    is_blueprint_copy = models.BooleanField(default=None, null=True, db_index=True)
    is_singleton = models.BooleanField()
    location_flag = models.CharField(max_length=NAMES_MAX_LENGTH)
    name = models.CharField(max_length=NAMES_MAX_LENGTH, default="")
    quantity = models.PositiveIntegerField()

    objects = CharacterAssetManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "item_id"],
                name="functional_pk_characterasset",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.item_id}-{self.name_display}"

    @property
    def name_display(self) -> str:
        """name of this asset to be displayed to user"""
        name = self.name if self.name else self.eve_type.name
        if self.is_blueprint_copy:
            name += " [BPC]"
        return name

    @property
    def icon_url(self) -> str:
        variant = self.eve_type.IconVariant.BPC if self.is_blueprint_copy else None
        return self.eve_type.icon_url(variant=variant)

    @property
    def group_display(self) -> str:
        """group of this asset to be displayed to user"""
        return self.eve_type.name if self.name else self.eve_type.eve_group.name


class CharacterContactLabel(models.Model):
    """An Eve Online contact label belonging to a Character"""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="contact_labels"
    )
    label_id = models.PositiveBigIntegerField()
    name = models.CharField(max_length=NAMES_MAX_LENGTH)

    objects = CharacterContactLabelManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "label_id"],
                name="functional_pk_characterlabel",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.name}"


class CharacterContact(models.Model):
    """An Eve Online contact belonging to a Character"""

    STANDING_EXCELLENT = _("excellent standing")
    STANDING_GOOD = _("good standing")
    STANDING_NEUTRAL = _("neutral standing")
    STANDING_BAD = _("bad standing")
    STANDING_TERRIBLE = _("terrible standing")

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="contacts"
    )
    eve_entity = models.ForeignKey(
        EveEntity, on_delete=models.CASCADE, related_name="+"
    )

    is_blocked = models.BooleanField(default=None, null=True)
    is_watched = models.BooleanField(default=None, null=True)
    standing = models.FloatField()
    labels = models.ManyToManyField(CharacterContactLabel, related_name="contacts")

    objects = CharacterContactManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "eve_entity"],
                name="functional_pk_charactercontact",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.eve_entity.name}"

    @property
    def standing_level(self) -> int:
        if self.standing > 5:
            return self.STANDING_EXCELLENT

        if 5 >= self.standing > 0:
            return self.STANDING_GOOD

        if self.standing == 0:
            return self.STANDING_NEUTRAL

        if 0 > self.standing >= -5:
            return self.STANDING_BAD

        if self.standing < -5:
            return self.STANDING_TERRIBLE


class CharacterContract(models.Model):
    """An Eve Online contract belonging to a Character"""

    AVAILABILITY_ALLIANCE = "AL"
    AVAILABILITY_CORPORATION = "CO"
    AVAILABILITY_PERSONAL = "PR"
    AVAILABILITY_PUBLIC = "PU"
    AVAILABILITY_CHOICES = (
        (AVAILABILITY_ALLIANCE, _("alliance")),
        (AVAILABILITY_CORPORATION, _("corporation")),
        (AVAILABILITY_PERSONAL, _("private")),
        (AVAILABILITY_PUBLIC, _("public")),
    )
    ESI_AVAILABILITY_MAP = {
        "alliance": AVAILABILITY_ALLIANCE,
        "corporation": AVAILABILITY_CORPORATION,
        "personal": AVAILABILITY_PERSONAL,
        "public": AVAILABILITY_PUBLIC,
    }

    STATUS_OUTSTANDING = "OS"
    STATUS_IN_PROGRESS = "IP"
    STATUS_FINISHED_ISSUER = "FI"
    STATUS_FINISHED_CONTRACTOR = "FC"
    STATUS_FINISHED = "FS"
    STATUS_CANCELED = "CA"
    STATUS_REJECTED = "RJ"
    STATUS_FAILED = "FL"
    STATUS_DELETED = "DL"
    STATUS_REVERSED = "RV"
    STATUS_CHOICES = (
        (STATUS_CANCELED, _("canceled")),
        (STATUS_DELETED, _("deleted")),
        (STATUS_FAILED, _("failed")),
        (STATUS_FINISHED, _("finished")),
        (STATUS_FINISHED_CONTRACTOR, _("finished contractor")),
        (STATUS_FINISHED_ISSUER, _("finished issuer")),
        (STATUS_IN_PROGRESS, _("in progress")),
        (STATUS_OUTSTANDING, _("outstanding")),
        (STATUS_REJECTED, _("rejected")),
        (STATUS_REVERSED, _("reversed")),
    )
    ESI_STATUS_MAP = {
        "canceled": STATUS_CANCELED,
        "deleted": STATUS_DELETED,
        "failed": STATUS_FAILED,
        "finished": STATUS_FINISHED,
        "finished_contractor": STATUS_FINISHED_CONTRACTOR,
        "finished_issuer": STATUS_FINISHED_ISSUER,
        "in_progress": STATUS_IN_PROGRESS,
        "outstanding": STATUS_OUTSTANDING,
        "rejected": STATUS_REJECTED,
        "reversed": STATUS_REVERSED,
    }

    TYPE_AUCTION = "AT"
    TYPE_COURIER = "CR"
    TYPE_ITEM_EXCHANGE = "IE"
    TYPE_LOAN = "LN"
    TYPE_UNKNOWN = "UK"
    TYPE_CHOICES = (
        (TYPE_AUCTION, _("auction")),
        (TYPE_COURIER, _("courier")),
        (TYPE_ITEM_EXCHANGE, _("item exchange")),
        (TYPE_LOAN, _("loan")),
        (TYPE_UNKNOWN, _("unknown")),
    )
    ESI_TYPE_MAP = {
        "auction": TYPE_AUCTION,
        "courier": TYPE_COURIER,
        "item_exchange": TYPE_ITEM_EXCHANGE,
        "loan": TYPE_LOAN,
        "unknown": TYPE_UNKNOWN,
    }

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="contracts",
    )
    contract_id = models.IntegerField()

    acceptor = models.ForeignKey(
        EveEntity,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="+",
        help_text="Who will accept the contract if character",
    )
    acceptor_corporation = models.ForeignKey(
        EveEntity,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="+",
        help_text="corporation of acceptor",
    )  # This field is currently unused
    assignee = models.ForeignKey(
        EveEntity,
        on_delete=models.CASCADE,
        default=None,
        null=True,
        related_name="+",
        help_text="To whom the contract is assigned, can be a corporation or a character",
    )
    availability = models.CharField(
        max_length=2,
        choices=AVAILABILITY_CHOICES,
        help_text="To whom the contract is available",
    )
    buyout = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS,
        decimal_places=CURRENCY_MAX_DECIMALS,
        default=None,
        null=True,
    )
    collateral = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS,
        decimal_places=CURRENCY_MAX_DECIMALS,
        default=None,
        null=True,
    )
    contract_type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    date_accepted = models.DateTimeField(default=None, null=True)
    date_completed = models.DateTimeField(default=None, null=True)
    date_expired = models.DateTimeField()
    date_issued = models.DateTimeField()
    days_to_complete = models.IntegerField(default=None, null=True)
    end_location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="contract_end_location",
        default=None,
        null=True,
    )
    for_corporation = models.BooleanField()
    issuer_corporation = models.ForeignKey(
        EveEntity, on_delete=models.CASCADE, related_name="+"
    )
    issuer = models.ForeignKey(EveEntity, on_delete=models.CASCADE, related_name="+")
    price = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS,
        decimal_places=CURRENCY_MAX_DECIMALS,
        default=None,
        null=True,
    )
    reward = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS,
        decimal_places=CURRENCY_MAX_DECIMALS,
        default=None,
        null=True,
    )
    start_location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name="contract_start_location",
        default=None,
        null=True,
    )
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    title = models.CharField(max_length=NAMES_MAX_LENGTH, default="")
    volume = models.FloatField(default=None, null=True)

    objects = CharacterContractManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "contract_id"],
                name="functional_pk_charactercontract",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.contract_id}"

    @property
    def is_completed(self) -> bool:
        """whether this contract is completed or active"""
        return self.status in [
            self.STATUS_FINISHED_ISSUER,
            self.STATUS_FINISHED_CONTRACTOR,
            self.STATUS_FINISHED_ISSUER,
            self.STATUS_CANCELED,
            self.STATUS_REJECTED,
            self.STATUS_DELETED,
            self.STATUS_FINISHED,
            self.STATUS_FAILED,
        ]

    @property
    def is_in_progress(self) -> bool:
        return self.status == self.STATUS_IN_PROGRESS

    @property
    def is_failed(self) -> bool:
        return self.status == self.STATUS_FAILED

    @property
    def has_expired(self) -> bool:
        """returns true if this contract is expired"""
        return self.date_expired < now()

    @property
    def hours_issued_2_completed(self) -> float:
        if self.date_completed:
            td = self.date_completed - self.date_issued
            return td.days * 24 + (td.seconds / 3600)
        else:
            return None

    def summary(self) -> str:
        """return summary text for this contract"""
        if self.contract_type == CharacterContract.TYPE_COURIER:
            summary = (
                f"{self.start_location.eve_solar_system} >> "
                f"{self.end_location.eve_solar_system} "
                f"({self.volume:.0f} m3)"
            )
        else:
            if self.items.filter(is_included=True).count() > 1:
                summary = _("[Multiple Items]")
            else:
                first_item = self.items.first()
                summary = first_item.eve_type.name if first_item else "(no items)"

        return summary


class CharacterContractBid(models.Model):
    contract = models.ForeignKey(
        CharacterContract, on_delete=models.CASCADE, related_name="bids"
    )
    bid_id = models.PositiveIntegerField(db_index=True)

    amount = models.FloatField()
    bidder = models.ForeignKey(EveEntity, on_delete=models.CASCADE, related_name="+")
    date_bid = models.DateTimeField()

    objects = CharacterContractBidManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return f"{self.contract}-{self.bid_id}"


class CharacterContractItem(models.Model):
    contract = models.ForeignKey(
        CharacterContract, on_delete=models.CASCADE, related_name="items"
    )
    record_id = models.PositiveIntegerField(db_index=True)

    is_included = models.BooleanField(db_index=True)
    is_singleton = models.BooleanField()
    quantity = models.PositiveIntegerField()
    raw_quantity = models.IntegerField(default=None, null=True)
    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")

    objects = CharacterContractItemManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return f"{self.contract}-{self.record_id}"

    @property
    def is_blueprint_original(self) -> bool:
        return self.raw_quantity == -1

    @property
    def is_blueprint_copy(self) -> bool:
        return self.raw_quantity == -2

    @property
    def is_blueprint(self) -> bool:
        return self.raw_quantity in [-1, -2]

    @property
    def name_display(self) -> str:
        """name to be displayed to user"""
        name = self.eve_type.name
        if self.is_blueprint_copy:
            name += " [BPC]"
        return name


class CharacterCorporationHistory(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="corporation_history"
    )
    record_id = models.PositiveIntegerField(db_index=True)

    corporation = models.ForeignKey(
        EveEntity, on_delete=models.CASCADE, related_name="+"
    )
    is_deleted = models.BooleanField(null=True, default=None, db_index=True)
    start_date = models.DateTimeField(db_index=True)

    objects = CharacterCorporationHistoryManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "record_id"],
                name="functional_pk_charactercorporationhistory",
            )
        ]

    def __str__(self) -> str:
        return str(f"{self.character}-{self.record_id}")


class CharacterDetails(models.Model):
    """Details for a character"""

    GENDER_MALE = "m"
    GENDER_FEMALE = "f"
    GENDER_CHOICES = (
        (GENDER_MALE, _("male")),
        (GENDER_FEMALE, _("female")),
    )
    character = models.OneToOneField(
        Character,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="details",
        help_text="character this details belongs to",
    )

    # character public info
    alliance = models.ForeignKey(
        EveEntity,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
    )
    birthday = models.DateTimeField()
    corporation = models.ForeignKey(
        EveEntity, on_delete=models.CASCADE, related_name="+"
    )
    description = models.TextField()
    eve_ancestry = models.ForeignKey(
        EveAncestry,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        related_name="+",
    )
    eve_bloodline = models.ForeignKey(
        EveBloodline, on_delete=models.CASCADE, related_name="+"
    )
    eve_faction = models.ForeignKey(
        EveFaction,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        related_name="+",
    )
    eve_race = models.ForeignKey(EveRace, on_delete=models.CASCADE, related_name="+")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    name = models.CharField(max_length=NAMES_MAX_LENGTH)
    security_status = models.FloatField(default=None, null=True)
    title = models.TextField()

    objects = CharacterDetailsManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return str(self.character)

    @property
    def description_plain(self) -> str:
        """returns the description without tags"""
        return eve_xml_to_html(self.description)


class CharacterImplant(models.Model):
    """Implant of a character"""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="implants"
    )
    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")

    objects = CharacterImplantManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "eve_type"],
                name="functional_pk_characterimplant",
            )
        ]

    def __str__(self) -> str:
        return str(f"{self.character}-{self.eve_type}")


class CharacterLocation(models.Model):
    """Location of a character"""

    character = models.OneToOneField(
        Character, on_delete=models.CASCADE, primary_key=True, related_name="location"
    )

    eve_solar_system = models.ForeignKey(
        EveSolarSystem, on_delete=models.CASCADE, related_name="+"
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_DEFAULT, default=None, null=True
    )

    objects = CharacterLocationManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return str(f"{self.character}-{self.eve_solar_system}")


class CharacterLoyaltyEntry(models.Model):
    """Loyalty entry for a character"""

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="loyalty_entries",
    )
    corporation = models.ForeignKey(
        EveEntity, on_delete=models.CASCADE, related_name="+"
    )

    loyalty_points = models.PositiveIntegerField()

    objects = CharacterLoyaltyEntryManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "corporation"],
                name="functional_pk_characterloyaltyentry",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.corporation}"


class CharacterJumpClone(models.Model):
    """Jump clone of a character"""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="jump_clones"
    )
    jump_clone_id = models.PositiveIntegerField(db_index=True)

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    name = models.CharField(max_length=NAMES_MAX_LENGTH, default="")

    objects = CharacterJumpCloneManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "jump_clone_id"],
                name="functional_pk_characterjumpclone",
            )
        ]

    def __str__(self) -> str:
        return str(f"{self.character}-{self.jump_clone_id}")


class CharacterJumpCloneImplant(models.Model):
    """Implant of a character jump clone"""

    jump_clone = models.ForeignKey(
        CharacterJumpClone, on_delete=models.CASCADE, related_name="implants"
    )
    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return str(f"{self.jump_clone}-{self.eve_type}")


class CharacterMail(models.Model):
    """Mail of a character"""

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="mails",
        help_text="character this mail belongs to",
    )
    mail_id = models.PositiveIntegerField(db_index=True)

    body = models.TextField()
    is_read = models.BooleanField(null=True, default=None, db_index=True)
    labels = models.ManyToManyField("CharacterMailLabel", related_name="mails")
    recipients = models.ManyToManyField("MailEntity", related_name="recipient_mails")
    # TODO: When migrations are reset remove default for sender
    sender = models.ForeignKey(
        "MailEntity",
        on_delete=models.CASCADE,
        null=True,
        default=None,
        related_name="sender_mails",
    )
    subject = models.CharField(max_length=255, default="")
    timestamp = models.DateTimeField(null=True, default=None)

    objects = CharacterMailManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "mail_id"], name="functional_pk_charactermail"
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.mail_id}"

    @property
    def body_html(self) -> str:
        """returns the body as html"""
        return eve_xml_to_html(self.body)


class CharacterMailLabel(models.Model):
    """Mail labels of a character"""

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="mail_labels"
    )
    label_id = models.PositiveIntegerField(db_index=True)

    name = models.CharField(max_length=40, db_index=True)
    color = models.CharField(max_length=16, default="")
    unread_count = models.PositiveIntegerField(default=None, null=True)

    objects = CharacterMailLabelManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "label_id"],
                name="functional_pk_charactermaillabel",
            )
        ]

    def __str__(self) -> str:
        return self.name


class CharacterMailUnreadCount(models.Model):
    """Wallet balance of a character"""

    character = models.OneToOneField(
        Character,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="unread_mail_count",
    )
    total = models.PositiveIntegerField()

    class Meta:
        default_permissions = ()


class CharacterOnlineStatus(models.Model):
    """Online Status of a character"""

    character = models.OneToOneField(
        Character,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="online_status",
    )

    last_login = models.DateTimeField(default=None, null=True)
    last_logout = models.DateTimeField(default=None, null=True)
    logins = models.PositiveIntegerField(default=None, null=True)

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return str(self.character)


class CharacterShip(models.Model):
    """Current ship of a character"""

    character = models.OneToOneField(
        Character, on_delete=models.CASCADE, related_name="ship"
    )
    name = models.CharField(max_length=255)
    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")

    objects = CharacterShipManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return str(f"{self.character}-{self.eve_type.name}")


class CharacterSkill(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="skills"
    )
    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")

    active_skill_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    skillpoints_in_skill = models.PositiveBigIntegerField()
    trained_skill_level = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    objects = CharacterSkillManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "eve_type"], name="functional_pk_characterskill"
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.eve_type.name}"


class CharacterSkillpoints(models.Model):
    """Skillpoints of a character"""

    character = models.OneToOneField(
        Character,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="skillpoints",
    )
    total = models.PositiveBigIntegerField()
    unallocated = models.PositiveIntegerField(default=None, null=True)

    class Meta:
        default_permissions = ()


class CharacterSkillqueueEntry(models.Model):
    """Entry in the skillqueue of a character"""

    character = models.ForeignKey(
        Character,
        on_delete=models.CASCADE,
        related_name="skillqueue",
    )
    queue_position = models.PositiveIntegerField(db_index=True)

    finish_date = models.DateTimeField(default=None, null=True)
    finished_level = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    level_end_sp = models.PositiveIntegerField(default=None, null=True)
    level_start_sp = models.PositiveIntegerField(default=None, null=True)
    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE, related_name="+")
    start_date = models.DateTimeField(default=None, null=True)
    training_start_sp = models.PositiveIntegerField(default=None, null=True)

    objects = CharacterSkillqueueEntryManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "queue_position"],
                name="functional_pk_characterskillqueueentry",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.queue_position}"

    @property
    def is_active(self) -> bool:
        """Returns true when this skill is currently being trained"""
        return self.finish_date and self.queue_position == 0


class CharacterSkillSetCheck(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="skill_set_checks"
    )
    skill_set = models.ForeignKey("SkillSet", on_delete=models.CASCADE)

    failed_required_skills = models.ManyToManyField(
        "SkillSetSkill", related_name="failed_required_skill_set_checks"
    )
    failed_recommended_skills = models.ManyToManyField(
        "SkillSetSkill", related_name="failed_recommended_skill_set_checks"
    )

    objects = CharacterSkillSetCheckManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "skill_set"],
                name="functional_pk_characterskillsetcheck",
            )
        ]

    def __str__(self) -> str:
        return f"{self.character}-{self.skill_set}"

    @property
    def can_fly(self) -> bool:
        return self.failed_required_skills.count() == 0


class CharacterWalletBalance(models.Model):
    """Wallet balance of a character"""

    character = models.OneToOneField(
        Character,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="wallet_balance",
    )
    total = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS, decimal_places=CURRENCY_MAX_DECIMALS
    )

    class Meta:
        default_permissions = ()


class CharacterWalletJournalEntry(models.Model):
    CONTEXT_ID_TYPE_UNDEFINED = "NON"
    CONTEXT_ID_TYPE_STRUCTURE_ID = "STR"
    CONTEXT_ID_TYPE_STATION_ID = "STA"
    CONTEXT_ID_TYPE_MARKET_TRANSACTION_ID = "MTR"
    CONTEXT_ID_TYPE_CHARACTER_ID = "CHR"
    CONTEXT_ID_TYPE_CORPORATION_ID = "COR"
    CONTEXT_ID_TYPE_ALLIANCE_ID = "ALL"
    CONTEXT_ID_TYPE_EVE_SYSTEM = "EVE"
    CONTEXT_ID_TYPE_INDUSTRY_JOB_ID = "INJ"
    CONTEXT_ID_TYPE_CONTRACT_ID = "CNT"
    CONTEXT_ID_TYPE_PLANET_ID = "PLN"
    CONTEXT_ID_TYPE_SYSTEM_ID = "SYS"
    CONTEXT_ID_TYPE_TYPE_ID = "TYP"
    CONTEXT_ID_CHOICES = (
        (CONTEXT_ID_TYPE_UNDEFINED, _("undefined")),
        (CONTEXT_ID_TYPE_STATION_ID, _("station ID")),
        (CONTEXT_ID_TYPE_MARKET_TRANSACTION_ID, _("market transaction ID")),
        (CONTEXT_ID_TYPE_CHARACTER_ID, _("character ID")),
        (CONTEXT_ID_TYPE_CORPORATION_ID, _("corporation ID")),
        (CONTEXT_ID_TYPE_ALLIANCE_ID, _("alliance ID")),
        (CONTEXT_ID_TYPE_EVE_SYSTEM, _("eve system")),
        (CONTEXT_ID_TYPE_INDUSTRY_JOB_ID, _("industry job ID")),
        (CONTEXT_ID_TYPE_CONTRACT_ID, _("contract ID")),
        (CONTEXT_ID_TYPE_PLANET_ID, _("planet ID")),
        (CONTEXT_ID_TYPE_SYSTEM_ID, _("system ID")),
        (CONTEXT_ID_TYPE_TYPE_ID, _("type ID")),
    )
    CONTEXT_ID_MAPS = {
        "undefined": CONTEXT_ID_TYPE_UNDEFINED,
        "station_id": CONTEXT_ID_TYPE_STATION_ID,
        "market_transaction_id": CONTEXT_ID_TYPE_MARKET_TRANSACTION_ID,
        "character_id": CONTEXT_ID_TYPE_CHARACTER_ID,
        "corporation_id": CONTEXT_ID_TYPE_CORPORATION_ID,
        "alliance_id": CONTEXT_ID_TYPE_ALLIANCE_ID,
        "eve_system": CONTEXT_ID_TYPE_EVE_SYSTEM,
        "industry_job_id": CONTEXT_ID_TYPE_INDUSTRY_JOB_ID,
        "contract_id": CONTEXT_ID_TYPE_CONTRACT_ID,
        "planet_id": CONTEXT_ID_TYPE_PLANET_ID,
        "system_id": CONTEXT_ID_TYPE_SYSTEM_ID,
        "type_id": CONTEXT_ID_TYPE_TYPE_ID,
    }

    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="wallet_journal"
    )
    entry_id = models.PositiveBigIntegerField(db_index=True)

    amount = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS,
        decimal_places=CURRENCY_MAX_DECIMALS,
        default=None,
        null=True,
        blank=True,
    )
    balance = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS,
        decimal_places=CURRENCY_MAX_DECIMALS,
        default=None,
        null=True,
        blank=True,
    )
    context_id = models.PositiveBigIntegerField(default=None, null=True)
    context_id_type = models.CharField(max_length=3, choices=CONTEXT_ID_CHOICES)
    date = models.DateTimeField()
    description = models.TextField()
    first_party = models.ForeignKey(
        EveEntity,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
    )
    reason = models.TextField()
    ref_type = models.CharField(max_length=64)
    second_party = models.ForeignKey(
        EveEntity,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
    )
    tax = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS,
        decimal_places=CURRENCY_MAX_DECIMALS,
        default=None,
        null=True,
        blank=True,
    )
    tax_receiver = models.ForeignKey(
        EveEntity,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        related_name="+",
    )

    objects = CharacterWalletJournalEntryManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "entry_id"],
                name="functional_pk_characterwalletjournalentry",
            )
        ]

    def __str__(self) -> str:
        return str(self.character) + " " + str(self.entry_id)

    @classmethod
    def match_context_type_id(cls, query: str) -> str:
        result = cls.CONTEXT_ID_MAPS.get(query)
        if result:
            return result

        return cls.CONTEXT_ID_TYPE_UNDEFINED


class CharacterWalletTransaction(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="wallet_transactions"
    )
    transaction_id = models.PositiveBigIntegerField(db_index=True)

    client = models.ForeignKey(EveEntity, on_delete=models.CASCADE, related_name="+")
    date = models.DateTimeField()
    is_buy = models.BooleanField()
    is_personal = models.BooleanField()
    journal_ref = models.OneToOneField(
        CharacterWalletJournalEntry,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        related_name="wallet_transaction",
    )
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    eve_type = models.ForeignKey(EveType, on_delete=models.CASCADE)
    unit_price = models.DecimalField(
        max_digits=CURRENCY_MAX_DIGITS, decimal_places=CURRENCY_MAX_DECIMALS
    )

    objects = CharacterWalletTransactionManager()

    class Meta:
        default_permissions = ()
        constraints = [
            models.UniqueConstraint(
                fields=["character", "transaction_id"],
                name="functional_pk_characterwallettransactions",
            )
        ]

    def __str__(self) -> str:
        return str(self.character) + " " + str(self.transaction_id)


class CharacterAttributes(models.Model):
    """The training attributes of the character"""

    character = models.OneToOneField(
        Character,
        primary_key=True,
        on_delete=models.CASCADE,
        related_name="attributes",
        help_text="character these attributes belongs to",
    )

    accrued_remap_cooldown_date = models.DateTimeField(default=None, null=True)
    last_remap_date = models.DateTimeField(default=None, null=True)
    bonus_remaps = models.PositiveIntegerField()
    charisma = models.PositiveIntegerField()
    intelligence = models.PositiveIntegerField()
    memory = models.PositiveIntegerField()
    perception = models.PositiveIntegerField()
    willpower = models.PositiveIntegerField()
    objects = CharacterAttributesManager()

    class Meta:
        default_permissions = ()

    def __str__(self) -> str:
        return str(self.character)
