import requests
import json

from typing import Tuple
from datetime import timedelta, datetime

from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.contrib.auth.models import Group

from esi.errors import TokenExpiredError, TokenInvalidError
from esi.models import Token

from allianceauth.authentication.models import CharacterOwnership
from allianceauth.eveonline.models import EveCharacter, EveCorporationInfo
from allianceauth.services.hooks import get_extension_logger
from allianceauth.authentication.models import State

from .providers import esi
from .decorators import fetch_token_for_owner

logger = get_extension_logger(__name__)


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            (
                "basic_access",
                "Can access this app and see operations based on visibility rules",
            ),
            ("create_event", "Can create and edit events"),
            ("see_signups", "Can see all signups for event"),
            ("manage_event", "Can delete and manage other signups"),
            (
                "add_ingame_calendar_owner",
                "Can add ingame calendar feeds for their corporation",
            ),
        )


class WebHook(models.Model):
    """Discord Webhook for pings"""

    name = models.CharField(
        max_length=150,
        help_text=_("Name for this webhook"),
    )
    webhook_url = models.CharField(
        max_length=500,
        help_text=_("Webhook URL"),
    )
    enabled = models.BooleanField(default=True, help_text=_("Is the webhook enabled?"))

    def send_embed(self, embed):
        custom_headers = {"Content-Type": "application/json"}
        data = '{"embeds": [%s]}' % json.dumps(embed)
        r = requests.post(self.webhook_url, headers=custom_headers, data=data)
        r.raise_for_status()

    class Meta:
        verbose_name = "Webhook"
        verbose_name_plural = "Webhooks"

    def __str__(self):
        return "{}".format(self.name)


class EventVisibility(models.Model):
    name = models.CharField(
        max_length=150, null=False, help_text="Name for the visibility filter"
    )
    restricted_to_group = models.ManyToManyField(
        Group,
        blank=True,
        related_name="eventvisibility_require_groups",
        help_text=_(
            "The group(s) that will be able to see this event visibility type ..."
        ),
    )
    restricted_to_state = models.ManyToManyField(
        State,
        blank=True,
        related_name="eventvisibility_require_states",
        help_text=_(
            "The state(s) that will be able to see this event visibility type ..."
        ),
    )
    webhook = models.ForeignKey(
        WebHook,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Webhook to send over notifications about these fleet types"),
    )
    ignore_past_fleets = models.BooleanField(
        default=True,
        help_text=_("Should we ignore fleet signals that are in the past"),
    )
    color = models.CharField(
        max_length=7,
        default="",
        blank=True,
        help_text=_("Color to be displayed on calendar"),
    )
    include_in_feed = models.BooleanField(
        default=False,
        help_text=("Whether these events should be included in the ical feed."),
    )
    is_visible = models.BooleanField(
        default=True,
        help_text=(
            "Whether this visibility filter should be displayed on the event form. Disable for internal visibilities such as the NPSI import fleet visibilities."
        ),
    )
    is_default = models.BooleanField(
        default=False,
        help_text=(
            "Whether this visibility filter is used as the default value on the event form"
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=("Whether this visibility filter is active"),
    )

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = "Event Visibility Filter"
        verbose_name_plural = "Event Visibilities Filters"

    def save(self, *args, **kwargs):
        if self.is_default:
            # select all other is_default items
            qs = type(self).objects.filter(is_default=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(is_default=False)

        super(EventVisibility, self).save(*args, **kwargs)

    @property
    def get_visibility_class(self):
        return f"{self.name.replace(' ', '-').lower()}"


class EventHost(models.Model):
    """Fleet Timer Create/Delete pings"""

    community = models.CharField(
        max_length=150, null=False, help_text="Name of the community"
    )
    logo_url = models.CharField(
        max_length=256, blank=True, help_text="Absolute URL for the community logo"
    )
    ingame_channel = models.CharField(
        max_length=150, blank=True, help_text="Ingame channel name"
    )
    ingame_mailing_list = models.CharField(
        max_length=150, blank=True, help_text="Ingame mailing list name"
    )
    fleet_comms = models.CharField(
        max_length=150,
        blank=True,
        help_text="Link or description for primary comms such as discord link",
    )
    fleet_doctrines = models.CharField(
        max_length=150, blank=True, help_text="Link or description to the doctrines"
    )
    website = models.CharField(max_length=150, blank=True, help_text="Website link URL")
    discord = models.CharField(max_length=150, blank=True, help_text="Discord link URL")
    twitch = models.CharField(max_length=150, blank=True, help_text="Twitch link URL")
    twitter = models.CharField(max_length=150, blank=True, help_text="Twitter link URL")
    youtube = models.CharField(max_length=150, blank=True, help_text="Youtube link URL")
    facebook = models.CharField(
        max_length=150, blank=True, help_text="Facebook link URL"
    )
    details = models.CharField(
        max_length=150, blank=True, help_text="Short description about the host."
    )
    is_default = models.BooleanField(
        default=False,
        help_text=("Whether this host is used as the default value on the event form"),
    )
    external = models.BooleanField(
        default=False,
        help_text=_(
            "External hosts are for NPSI API imports. Checking this box will hide the host in the manual event form."
        ),
    )

    def __str__(self):
        return str(self.community)

    class Meta:
        verbose_name = "Host"
        verbose_name_plural = "Hosts"

    def save(self, *args, **kwargs):
        if self.is_default:
            # select all other is_default items
            qs = type(self).objects.filter(is_default=True)
            # except self (if self already exists)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            # and deactive them
            qs.update(is_default=False)

        super(EventHost, self).save(*args, **kwargs)


class EventCategory(models.Model):
    name = models.CharField(
        max_length=150,
        help_text=_("Name for the category"),
    )
    ticker = models.CharField(
        max_length=10,
        help_text=_("Ticker for the category"),
    )
    color = models.CharField(
        max_length=7,
        default="",
        blank=True,
        help_text=_("Color to be displayed on calendar"),
    )
    description = models.TextField(
        blank=True,
        help_text="Prefilled description that will be added on default on the event description.",
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return str(self.name)

    @property
    def get_category_class(self):
        return f"{self.name.replace(' ', '-').lower()}"


class EventImport(models.Model):
    """NPSI IMPORT OPTIONS"""

    SPECTRE_FLEET = "SF"
    EVE_UNIVERSITY = "EU"
    FUN_INC = "FI"
    FRIDAY_YARRRR = "FY"
    REDEMPTION_ROAD = "RR"
    CAS = "CA"
    FWAMING_DWAGONS = "FD"
    FREE_RANGE_CHIKUNS = "FR"
    EVE_LINKNET = "LN"

    IMPORT_SOURCES = [
        (EVE_LINKNET, _("EVE LinkNet")),
        (SPECTRE_FLEET, _("Spectre Fleet")),
        (EVE_UNIVERSITY, _("EVE University")),
        (FUN_INC, _("Fun Inc.")),
        (FRIDAY_YARRRR, _("FRIDAY YARRRR")),
        (REDEMPTION_ROAD, _("Redemption Road")),
        (CAS, _("CAS")),
        (FWAMING_DWAGONS, _("Fwaming Dwagons")),
        (FREE_RANGE_CHIKUNS, _("FREE RANGE CHIKUNS")),
    ]

    source = models.CharField(
        max_length=32,
        choices=IMPORT_SOURCES,
        help_text="The API source where you want to pull events from",
    )

    host = models.ForeignKey(
        EventHost,
        on_delete=models.CASCADE,
        default=1,
        help_text="The AA host that will be used for the pulled events",
    )
    operation_type = models.ForeignKey(
        EventCategory,
        on_delete=models.CASCADE,
        help_text="Operation type and ticker that will be assigned for the pulled fleets",
    )
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default="1",
        help_text="User that has been used to create the fleet (most often the superuser who manages the plugin)",
    )
    eve_character = models.ForeignKey(
        EveCharacter,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Event creator main character",
    )
    event_visibility = models.ForeignKey(
        EventVisibility,
        on_delete=models.CASCADE,
        null=True,
        help_text=_("Visibility filter that dictates who is able to see this event"),
    )

    def __str__(self):
        return str(self.source)

    class Meta:
        verbose_name = "NPSI Event Import"
        verbose_name_plural = "NPSI Event Imports"


class Event(models.Model):
    DAILY = "DD"
    WEEKLY = "WE"
    MONTHLY = "MM"
    YEARLY = "YY"

    REPEAT_INTERVAL = [
        (DAILY, _("Daily")),
        (WEEKLY, _("Weekly")),
        (MONTHLY, _("Monthly")),
        (YEARLY, _("Yearly")),
    ]

    operation_type = models.ForeignKey(
        EventCategory,
        null=True,
        on_delete=models.CASCADE,
        help_text=_("Event category type"),
    )
    title = models.CharField(
        max_length=200,
        help_text=_("Title for the event"),
    )
    host = models.ForeignKey(
        EventHost,
        on_delete=models.CASCADE,
        help_text=_("Host entity for the event"),
    )
    doctrine = models.CharField(
        max_length=254,
        help_text=_("Doctrine URL or name"),
    )
    formup_system = models.CharField(
        max_length=254,
        help_text=_("Location for formup"),
    )
    description = models.TextField(
        help_text=_("Description text for the operation"),
    )
    start_time = models.DateTimeField(
        help_text=_("Event start date and time"),
    )
    end_time = models.DateTimeField(
        help_text=_("Event end date and time"),
    )
    repeat_event = models.CharField(
        max_length=32,
        default=False,
        null=True,
        blank=True,
        choices=REPEAT_INTERVAL,
        help_text="Select if you want to repeat this event in the future",
    )
    repeat_times = models.IntegerField(
        default=False,
        null=True,
        blank=True,
        help_text="How many times do you want to repeat this event?",
    )
    fc = models.CharField(
        max_length=254,
        help_text=_("Fleet commander/manager for the event"),
    )
    event_visibility = models.ForeignKey(
        EventVisibility,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Visibility filter that dictates who is able to see this event"),
    )
    external = models.BooleanField(
        default=False,
        null=True,
        help_text=_("Is the event an external event over API"),
    )
    created_date = models.DateTimeField(
        default=timezone.now,
        help_text=_("When the event was created"),
    )
    eve_character = models.ForeignKey(
        EveCharacter,
        null=True,
        on_delete=models.SET_NULL,
        help_text=_("Character used to create the event"),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text=_("User who created the event"),
    )

    def duration(self):
        return self.end_time - self.start_time

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("opcalendar:event-detail", args=(self.id,))

    @property
    def get_visibility_class(self):
        if self.event_visibility:
            return f"{self.event_visibility.name.replace(' ', '-').lower()}"

    @property
    def get_event_styling(self):
        if self.event_visibility:
            return f".{self.event_visibility.name.replace(' ', '-').lower()}:before{{border-color: transparent {self.event_visibility.color} transparent transparent;border-style: solid;}} .{self.operation_type.name.replace(' ', '-').lower()} {{border-left: 6px solid {self.operation_type.color} !important;}}"

    @property
    def get_category_class(self):
        if self.operation_type:
            return f"{self.operation_type.name.replace(' ', '-').lower()}"

    @property
    def get_date_status(self):

        if datetime.now(timezone.utc) > self.start_time:
            return "past-event"
        else:
            return "future-event"

    @property
    def get_html_url(self):
        url = reverse("opcalendar:event-detail", args=(self.id,))
        return f"{url}"

    @property
    def get_html_title(self):
        return f'<span>{self.start_time.strftime("%H:%M")} - {self.end_time.strftime("%H:%M")} <i>{self.host.community}</i></span><span><b>{self.operation_type.ticker} {self.title}</b></span>'

    def user_can_edit(self, user: user) -> bool:
        """Checks if the given user can edit this timer. Returns True or False"""
        return user.has_perm("opcalendar.manage_event") or (
            self.user == user and user.has_perm("opcalendar.create_event")
        )


class Owner(models.Model):
    """A corporation that holds the calendars"""

    ERROR_NONE = 0
    ERROR_TOKEN_INVALID = 1
    ERROR_TOKEN_EXPIRED = 2
    ERROR_INSUFFICIENT_PERMISSIONS = 3
    ERROR_NO_CHARACTER = 4
    ERROR_ESI_UNAVAILABLE = 5
    ERROR_OPERATION_MODE_MISMATCH = 6
    ERROR_UNKNOWN = 99

    ERRORS_LIST = [
        (ERROR_NONE, "No error"),
        (ERROR_TOKEN_INVALID, "Invalid token"),
        (ERROR_TOKEN_EXPIRED, "Expired token"),
        (ERROR_INSUFFICIENT_PERMISSIONS, "Insufficient permissions"),
        (ERROR_NO_CHARACTER, "No character set for fetching data from ESI"),
        (ERROR_ESI_UNAVAILABLE, "ESI API is currently unavailable"),
        (
            ERROR_OPERATION_MODE_MISMATCH,
            "Operaton mode does not match with current setting",
        ),
        (ERROR_UNKNOWN, "Unknown error"),
    ]

    corporation = models.OneToOneField(
        EveCorporationInfo,
        default=None,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text="Corporation owning the calendar",
        related_name="+",
    )
    character = models.ForeignKey(
        CharacterOwnership,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True,
        blank=True,
        help_text="Character used for syncing the calendar",
        related_name="+",
    )
    event_visibility = models.ForeignKey(
        EventVisibility,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Visibility filter that dictates who is able to see this event"),
    )
    operation_type = models.ForeignKey(
        EventCategory,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        help_text=_(
            "Event category that will be assigned for all of the events from this owner."
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=("whether this owner is currently included in the sync process"),
    )

    class Meta:
        verbose_name = "Ingame Clanedar Owner"
        verbose_name_plural = "Ingame Calendar Owners"

    @fetch_token_for_owner(["esi-calendar.read_calendar_events.v1"])
    def update_events_esi(self, token):
        if self.is_active:

            # Get all current imported fleets in database
            event_ids_to_remove = list(
                IngameEvents.objects.filter(owner=self).values_list(
                    "event_id", flat=True
                )
            )
            logger.debug(
                "Ingame events currently in database: %s" % event_ids_to_remove
            )

            events = self._fetch_events()
            for event in events:

                character_id = self.character.character.character_id

                details = (
                    esi.client.Calendar.get_characters_character_id_calendar_event_id(
                        character_id=character_id,
                        event_id=event["event_id"],
                        token=token.valid_access_token(),
                    ).results()
                )

                end_date = event["event_date"] + timedelta(minutes=details["duration"])

                original = IngameEvents.objects.filter(
                    owner=self, event_id=event["event_id"]
                ).first()

                text = strip_tags(details["text"])

                try:
                    if original is not None:

                        logger.debug("Event: %s already in database" % event["title"])
                        event_ids_to_remove.remove(original.event_id)

                    else:

                        # Check if we already have the host
                        original_host = EventHost.objects.filter(
                            community=details["owner_name"]
                        ).first()

                        logger.debug("Got original host: {}".format(original_host))

                        if original_host is not None:
                            host = original_host
                        else:
                            host = EventHost.objects.create(
                                community=details["owner_name"],
                                external=True,
                            )

                        IngameEvents.objects.create(
                            event_id=event["event_id"],
                            owner=self,
                            text=text,
                            event_owner_id=details["owner_id"],
                            owner_type=details["owner_type"],
                            owner_name=details["owner_name"],
                            host=host,
                            importance=details["importance"],
                            duration=details["duration"],
                            event_start_date=event["event_date"],
                            event_end_date=end_date,
                            title=event["title"],
                        )
                        logger.debug("New event created: %s" % event["title"])
                except Exception as e:
                    logger.debug("Error adding new event: %s" % e)

            logger.debug("Removing all events that we did not get over API")
            IngameEvents.objects.filter(pk__in=event_ids_to_remove).delete()

            logger.debug(
                "All events fetched for %s" % self.character.character.character_name
            )

    @fetch_token_for_owner(["esi-calendar.read_calendar_events.v1"])
    def _fetch_events(self, token) -> list:

        character_id = self.character.character.character_id

        events = esi.client.Calendar.get_characters_character_id_calendar(
            character_id=character_id,
            token=token.valid_access_token(),
        ).results()

        return events

    def token(self, scopes=None) -> Tuple[Token, int]:
        """returns a valid Token for the owner"""
        token = None
        error = None

        # abort if character is not configured
        if self.character is None:
            logger.error("%s: No character configured to sync", self)
            error = self.ERROR_NO_CHARACTER

        # abort if character does not have sufficient permissions
        elif self.corporation and not self.character.user.has_perm(
            "opcalendar.add_ingame_calendar_owner"
        ):
            logger.error(
                "%s: This character does not have sufficient permission to sync corporation calendars",
                self,
            )
            error = self.ERROR_INSUFFICIENT_PERMISSIONS

        # abort if character does not have sufficient permissions
        elif not self.character.user.has_perm("opcalendar.add_ingame_calendar_owner"):
            logger.error(
                "%s: This character does not have sufficient permission to sync personal calendars",
                self,
            )
            error = self.ERROR_INSUFFICIENT_PERMISSIONS

        else:
            try:
                # get token
                token = (
                    Token.objects.filter(
                        user=self.character.user,
                        character_id=self.character.character.character_id,
                    )
                    .require_scopes(scopes)
                    .require_valid()
                    .first()
                )
            except TokenInvalidError:
                logger.error("%s: Invalid token for fetching calendars", self)
                error = self.ERROR_TOKEN_INVALID
            except TokenExpiredError:
                logger.error("%s: Token expired for fetching calendars", self)
                error = self.ERROR_TOKEN_EXPIRED
            else:
                if not token:
                    logger.error("%s: No token found with sufficient scopes", self)
                    error = self.ERROR_TOKEN_INVALID

        return token, error


class IngameEvents(models.Model):

    event_id = models.PositiveBigIntegerField(
        primary_key=True, help_text="The EVE ID of the event"
    )
    owner = models.ForeignKey(
        Owner,
        on_delete=models.CASCADE,
        help_text="Event holder",
    )
    event_start_date = models.DateTimeField()
    event_end_date = models.DateTimeField(blank=True, null=True)
    title = models.CharField(max_length=128)
    text = models.TextField()
    event_owner_id = models.IntegerField(null=True)
    owner_type = models.CharField(max_length=128)
    owner_name = models.CharField(max_length=128)
    host = models.ForeignKey(
        EventHost,
        on_delete=models.CASCADE,
        default=1,
        help_text=_("Host entity for the event"),
    )
    importance = models.CharField(max_length=128)
    duration = models.CharField(max_length=128)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Ingame Event"
        verbose_name_plural = "Ingame Events"

    def get_absolute_url(self):
        return reverse("opcalendar:ingame-event-detail", args=(self.event_id,))

    @property
    def get_date_status(self):

        if datetime.now(timezone.utc) > self.event_start_date:
            return "past-event"
        else:
            return "future-event"

    @property
    def get_visibility_class(self):
        if self.owner.event_visibility:
            return f"{self.owner.event_visibility.name.replace(' ', '-').lower()}"
        else:
            return "ingame-event"

    @property
    def get_event_styling(self):
        d = ""
        if self.owner.event_visibility:
            d += f".{self.owner.event_visibility.name.replace(' ', '-').lower()}:before{{border-color: transparent {self.owner.event_visibility.color} transparent transparent;border-style: solid;}}"
        if self.owner.operation_type:
            d += f".{self.owner.operation_type.name.replace(' ', '-').lower()} {{border-left: 6px solid {self.owner.operation_type.color} !important;}}"
        return d

    @property
    def get_category_class(self):
        if self.owner.operation_type:
            return f"{self.owner.operation_type.name.replace(' ', '-').lower()}"

    @property
    def get_html_url(self):
        url = reverse("opcalendar:ingame-event-detail", args=(self.event_id,))
        return f"{url}"

    @property
    def get_html_title(self):
        return f'<span>{self.event_start_date.strftime("%H:%M")} - {self.event_end_date.strftime("%H:%M")}<i> {self.owner_name}</i></span><span><b>{self.title}</b></span>'


class EventMember(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    character = models.ForeignKey(
        EveCharacter,
        null=True,
        on_delete=models.SET_NULL,
        help_text="Event creator main character",
    )

    class Meta:
        unique_together = ["event", "character"]
