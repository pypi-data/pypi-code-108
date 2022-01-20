import operator
from calendar import HTMLCalendar
from datetime import date
from itertools import chain
from datetime import datetime
from django.db.models import Q, F
from django.utils import timezone
from allianceauth.services.hooks import get_extension_logger

from .models import Event, IngameEvents
from .app_settings import (
    OPCALENDAR_DISPLAY_STRUCTURETIMERS,
    OPCALENDAR_DISPLAY_MOONMINING,
)

from .app_settings import structuretimers_active, moonmining_active

if structuretimers_active():
    from structuretimers.models import Timer

if moonmining_active():
    from moonmining.models import Extraction

logger = get_extension_logger(__name__)


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, user=None):
        self.year = year
        self.month = month
        self.user = user
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(
        self, day, events, ingame_events, structuretimer_events, moonmining_events
    ):

        structuretimers_per_day = []

        moonmining_per_day = []

        events_per_day = events.filter(start_time__day=day)

        ingame_events_per_day = ingame_events.filter(event_start_date__day=day)

        if structuretimers_active() and OPCALENDAR_DISPLAY_STRUCTURETIMERS:
            structuretimers_per_day = structuretimer_events.filter(start_time__day=day)

        if moonmining_active() and OPCALENDAR_DISPLAY_MOONMINING:
            moonmining_per_day = moonmining_events.filter(chunk_arrival_at__day=day)

        all_events_per_day = sorted(
            chain(
                events_per_day,
                ingame_events_per_day,
                structuretimers_per_day,
                moonmining_per_day,
            ),
            key=operator.attrgetter("start_time"),
        )

        d = ""

        # Only events for current month
        if day != 0:
            # Parse events
            for event in all_events_per_day:

                if type(event).__name__ == "Timer":
                    OBJECTIVE_UNDEFINED = "UN"
                    OBJECTIVE_HOSTILE = "HO"
                    OBJECTIVE_FRIENDLY = "FR"
                    OBJECTIVE_NEUTRAL = "NE"

                    if event.objective == OBJECTIVE_HOSTILE:
                        objective_verbosed = "Hostile"
                    if event.objective == OBJECTIVE_FRIENDLY:
                        objective_verbosed = "Friendly"
                    if event.objective == OBJECTIVE_NEUTRAL:
                        objective_verbosed = "Neutral"
                    if event.objective == OBJECTIVE_UNDEFINED:
                        objective_verbosed = "Undefined"

                    d += (
                        f'<div class="event {"past-event" if datetime.now(timezone.utc) > event.date else "future-event"} event-structuretimer">'
                        f'<span>{event.date.strftime("%H:%M")}<i> {objective_verbosed} structure timer</i></span>'
                        f"<span>{event.eve_solar_system.name} - {event.structure_type.name}</span>"
                        f"</div>"
                    )

                    logger.debug("Typer type is: %s " % event.get_objective_display())

                if type(event).__name__ == "Extraction":
                    # WIP currently only required view permission
                    if self.user.has_perm(
                        "moonmining.extractions_access"
                    ) and self.user.has_perm("moonmining.extractions_access"):
                        refinery = event.refinery.name
                        system = (
                            event.refinery.moon.eve_moon.eve_planet.eve_solar_system.name
                        )

                        structure = refinery.replace(system, "")

                        d += (
                            f'<a class="nostyling" href="/moonmining/extraction/{event.id}?new_page=yes">'
                            f'<div class="event {"past-event" if datetime.now(timezone.utc) > event.chunk_arrival_at else "future-event"} event-moonmining">'
                            f'<span>{event.chunk_arrival_at.strftime("%H:%M")} <i> Moon chunk arrival {event.refinery.moon.eve_moon.name}</i></span>'
                            f"<span>{structure[3:]}</span>"
                            f"</div>"
                            f"</a>"
                        )
                if (
                    type(event).__name__ == "Event"
                    or type(event).__name__ == "IngameEvents"
                ):
                    d += (
                        f"<style>{event.get_event_styling}</style>"
                        f'<a class="nostyling" href="{event.get_html_url}">'
                        f'<div class="event {event.get_date_status} {event.get_visibility_class} {event.get_category_class}">'
                        f"{event.get_html_title}"
                        f"</div>"
                        f"</a>"
                    )
            if date.today() == date(self.year, self.month, day):
                return f"<td class='today'><div class='date'>{day}</div> {d}</td>"
            return f"<td><div class='date'>{day}</div> {d}</td>"
        return "<td></td>"

    # formats a week as a tr
    def formatweek(
        self, theweek, events, ingame_events, structuretimer_events, moonmining_events
    ):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(
                d, events, ingame_events, structuretimer_events, moonmining_events
            )
        return f"<tr> {week} </tr>"

    # formats a month as a table
    # filter events by year and month

    def formatmonth(self, withyear=True):
        # Get normal events
        # Filter by groups and states
        events = (
            Event.objects.filter(
                start_time__year=self.year,
                start_time__month=self.month,
            )
            .filter(
                Q(event_visibility__restricted_to_group__in=self.user.groups.all())
                | Q(event_visibility__restricted_to_group__isnull=True),
            )
            .filter(
                Q(event_visibility__restricted_to_state=self.user.profile.state)
                | Q(event_visibility__restricted_to_state__isnull=True),
            )
        )
        # Get ingame events
        # Filter by groups and states
        ingame_events = (
            IngameEvents.objects.filter(
                event_start_date__year=self.year, event_start_date__month=self.month
            )
            .annotate(start_time=F("event_start_date"), end_time=F("event_end_date"))
            .filter(
                Q(
                    owner__event_visibility__restricted_to_group__in=self.user.groups.all()
                )
                | Q(owner__event_visibility__restricted_to_group__isnull=True),
            )
            .filter(
                Q(owner__event_visibility__restricted_to_state=self.user.profile.state)
                | Q(owner__event_visibility__restricted_to_state__isnull=True),
            )
        )

        # Check if structuretimers is active
        # Should we fetch timers

        if structuretimers_active() and OPCALENDAR_DISPLAY_STRUCTURETIMERS:
            structuretimer_events = (
                Timer.objects.all()
                .visible_to_user(self.user)
                .annotate(start_time=F("date"))
                .filter(date__year=self.year, date__month=self.month)
            )
        else:
            structuretimer_events = Event.objects.none()

        # Check if moonmining is active
        # Should we fetch extractions
        if moonmining_active() and OPCALENDAR_DISPLAY_MOONMINING:
            moonmining_events = (
                Extraction.objects.all()
                .annotate(start_time=F("chunk_arrival_at"))
                .filter(
                    chunk_arrival_at__year=self.year, chunk_arrival_at__month=self.month
                )
                .exclude(status="CN")
            )
        else:
            moonmining_events = Event.objects.none()

        logger.debug(
            "Returning %s extractions, display setting is %s. List is: %s"
            % (
                moonmining_events.count(),
                OPCALENDAR_DISPLAY_MOONMINING,
                moonmining_events,
            )
        )

        logger.debug("Returning %s ingame events" % ingame_events.count())

        cal = '<table class="calendar">\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        cal += f"{self.formatweekheader()}\n"

        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, events, ingame_events, structuretimer_events, moonmining_events)}\n"

        cal += "</table>"

        return cal
