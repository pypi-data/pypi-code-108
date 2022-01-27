from datetime import datetime, timedelta

week = ["Sunday", "Monday", "Tuesday",
        "Wednesday", "Thursday", "Friday", "Saturday"]
day_name_map = {
    "Sunday": "Sun",
    "Monday": "Mon",
    "Tuesday": "Tue",
    "Wednesday": "Wed",
    "Thursday": "Thur",
    "Friday": "Fri",
    "Saturday": "Sat"
}
keys = [
    "frequency", "interval", "time",
    "weekDays", "monthDays",
    "hours", "minutes"
]
start_date = datetime(datetime.utcnow().year, 1, 1, 0, 0)
start_time_fmt = "%Y-%m-%dT%H:%M:%SZ"


def create_schedule_id(config_obj):
    entries = {k: config_obj.get(k) for k in keys}

    if entries["weekDays"]:
        entries["weekDays"] = \
            tuple([w for w in week if w in entries["weekDays"]])
    elif entries["monthDays"]:
        entries["monthDays"] = tuple(sorted(entries["monthDays"]))
    elif entries["frequency"] is None:
        entries["frequency"] = "Day"

    if entries["frequency"] is None:
        if entries["hours"] is None:
            entries["hours"] = [0]
        if entries["minutes"] is None:
            entries["minutes"] = [0]
    elif entries["minutes"] is None and entries["hours"] is not None:
        entries["minutes"] = [0]

    if entries["hours"] is not None:
        entries["hours"] = tuple(sorted(entries["hours"]))
    if entries["minutes"] is not None:
        entries["minutes"] = tuple(sorted(entries["minutes"]))

    return tuple(entries[k] for k in keys)


def trigger_name(frequency, interval, time,
                 weekDays, monthDays,
                 hours, minutes):

    def create_times_list():
        return " ".join([
            str(h).zfill(2) + str(m).zfill(2)
            for h in hours
            for m in minutes
        ])

    if frequency and interval:
        trigger_name = f"Every {interval} {frequency}"
        if interval > 1:
            trigger_name += "s"
        return trigger_name
    elif weekDays:
        return " - ".join([
            "Each Week",
            " ".join([day_name_map[day] for day in weekDays]),
            create_times_list()
        ])
    elif monthDays:
        return " - ".join([
            "Each Month",
            "Days " + " ".join([str(d) for d in sorted(monthDays)]),
            create_times_list()
        ])
    elif time:
        return "Daily - " + time.replace(":", "")
    else:
        return "Daily - " + create_times_list()


def create_recurrence_object(frequency, interval, time,
                             weekDays, monthDays,
                             hours, minutes):

    recurr_obj = {
        "interval": 1,
        "startTime": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "timeZone": "UTC"
    }

    if weekDays:
        return {
            **recurr_obj,
            "frequency": "Week",
            "schedule": {
                "hours": list(hours),
                "minutes": list(minutes),
                "weekDays": list(weekDays)
            }
        }
    elif monthDays:
        return {
            **recurr_obj,
            "frequency": "Month",
            "schedule": {
                "hours": list(hours),
                "minutes": list(minutes),
                "monthDays": list(monthDays)
            }
        }
    elif frequency in (None, "Day"):
        obj = {
            **recurr_obj,
            "frequency": "Day"
        }

        if time is not None:
            hour, minute = time.split(":")
        else:
            hour, minute = hours[0], minutes[0]
            obj["schedule"] = {
                "hours": list(hours),
                "minutes": list(minutes)
            }
        obj["startTime"] = (
                start_date + timedelta(hours=int(hour), minutes=int(minute))
            ).strftime(start_time_fmt)

        return obj
    else:
        recurr_obj["frequency"] = frequency
        if interval:
            recurr_obj["interval"] = interval

        return recurr_obj
