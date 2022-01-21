from datetime import timedelta

from django.utils import formats, timezone

import requests
from cache_memoize import cache_memoize
from ics import Calendar


def get_current_events(calendar: Calendar, limit: int = 5) -> list:
    """Get upcoming events from a calendar (ICS) object.

    :param calendar: The calendar object
    :param limit: Count of events
    :return: List of upcoming events
    """
    i: int = 0
    events: list = []
    for event in calendar.timeline.start_after(timezone.now()):
        # Check for limit
        if i >= limit:
            break
        i += 1

        if event.all_day:
            # The last day in all day events is excluded
            event.end -= timedelta(days=1)

        # Create formatted dates and times for begin and end
        begin_date_formatted = formats.date_format(event.begin)
        end_date_formatted = formats.date_format(event.end)
        begin_time_formatted = formats.time_format(event.begin.time())
        end_time_formatted = formats.time_format(event.end.time())

        if event.begin.date() == event.end.date():
            # Event is only on one day
            formatted = begin_date_formatted

            if not event.all_day:
                # No all day event
                formatted += f" {begin_time_formatted}"

                if event.begin.time != event.end.time():
                    # Event has an end time
                    formatted += f" – {end_time_formatted}"

        else:
            # Event is on multiple days
            if event.all_day:
                # Event is all day
                formatted = f"{begin_date_formatted} – {end_date_formatted}"
            else:
                # Event has begin and end times
                formatted = (
                    f"{begin_date_formatted} {begin_time_formatted}"
                    f" – {end_date_formatted} {end_time_formatted}"
                )

        events.append(
            {
                "name": event.name,
                "begin_timestamp": event.begin.timestamp,
                "end_timestamp": event.end.timestamp,
                "date_formatted": formatted,
            }
        )

    return events


@cache_memoize(3600)
def get_current_events_with_cal(calendar_url: str, limit: int = 5) -> list:
    """Get current events.

    Download an iCalendar file from an URL, parse using the ICS library
    and return a limited number of events.
    """
    content = requests.get(calendar_url, timeout=3)
    calendar: Calendar = Calendar(content.text)
    return get_current_events(calendar, limit)
