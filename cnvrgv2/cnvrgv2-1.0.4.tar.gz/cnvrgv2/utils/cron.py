import pytz

from cnvrgv2.config import error_messages
from cnvrgv2.errors import CnvrgArgumentsError


class Cron:
    def __init__(self, minute="*", hour="*", day_of_month="*", month="*", day_of_week="*", timezone=None):
        Cron.validate_input(locals())
        self._minute = minute
        self._hour = hour
        self._day_of_month = day_of_month
        self._month = month
        self._day_of_week = day_of_week
        self._timezone = timezone

    @staticmethod
    def validate_input(cron_params):
        # type check
        allowed_values = {
            "minute": {"min": 0, "max": 59},
            "hour": {"min": 0, "max": 23},
            "day_of_month": {"min": 1, "max": 31},
            "month": {"min": 1, "max": 12},
            "day_of_week": {"min": 0, "max": 6}
        }

        argument_errors = {}
        for param_name, edges in allowed_values.items():
            current_value = cron_params[param_name]
            if current_value == "*":
                continue

            if not isinstance(current_value, int) or current_value not in range(edges["min"], edges["max"] + 1):
                message = error_messages.INVALID_CRON_ARGUMENT.format(param_name, edges["min"], edges["max"])
                argument_errors[param_name] = message

        timezone = cron_params.get("timezone", None)
        if timezone and timezone not in pytz.all_timezones:
            argument_errors["timezone"] = error_messages.CRON_INVALID_TIMEZONE

        if argument_errors:
            raise CnvrgArgumentsError(argument_errors)

    @staticmethod
    def validate_cron_syntax(cron_string):
        cron_parts = cron_string.strip().split()
        if len(cron_parts) < 5:
            raise CnvrgArgumentsError(error_messages.CRON_ARGUMENTS_MISSING)

        cron_params = {
            "minute": cron_parts[0],
            "hour": cron_parts[1],
            "day_of_month": cron_parts[2],
            "month": cron_parts[3],
            "day_of_week": cron_parts[4],
            "timezone": cron_parts[5] if 5 < len(cron_parts) else None
        }

        try:
            for key, value in cron_params.items():
                if key == "timezone":
                    continue
                if value != "*":
                    cron_params[key] = int(value)
        except ValueError:
            raise CnvrgArgumentsError(error_messages.CRON_INVALID_ARGUMENT)

        Cron.validate_input(cron_params)

    def __str__(self):
        cron_string = "{} {} {} {} {}".format(
            self._minute,
            self._hour,
            self._day_of_month,
            self._month,
            self._day_of_week
        )

        if self._timezone is not None:
            cron_string += " " + self._timezone

        return cron_string
