# coding=utf-8
"""
(C) FHCS GmbH

Class representing single FA task used for planning tasks through FA API
"""

from datetime import datetime, timedelta
from json import dumps
from typing import Dict, List, Optional, Union


class FATask:
    """
    Representing singe FA task for planning through FA API.
    """

    def __init__(self,
                 title: str,
                 details: str,
                 language: str,
                 site: int,
                 start: datetime,
                 end: datetime,
                 *,
                 owners: Optional[List[int]] = None,
                 approvers: Optional[List[int]] = None,
                 watchers: Optional[List[int]] = None,
                 spaces: Optional[Dict[str, List[int]]] = None,
                 duration: Optional[timedelta] = None) -> None:
        """
        Constructs the FA task object.

        :param title: Task title, UTF-8
        :param details: Task details string, may be multilene, UTF-8
        :param language: Task title and description language, "ru", "en", etc.
        :param site: Site ID in FA
        :param start: date and time when first occurence of task is planned to start, timezone information ignored
        :param end: date and time of deadline when first occurence is planned to copmlete, timezone information ignored
        :param owners: list of user IDs in FA to assign the task on, users will be responsible for tasks
        :param approvers: list of user IDs in FA who will become approvers, usually managers
        :param watchers: list of user IDs in FA who will have access to watch task status
        :param spaces: dict of spaces on which to plan the task, {"floor ID": [list of space IDs]}
        :param duration: duration of task as timedelta object
        """
        _d = (0, 0, 0)
        if duration is not None:
            (_dh, _ds) = divmod(duration.total_seconds(), 3600)
            _d = ((int(_dh),) + divmod(int(_ds), 60))
        self._task = {
                "advanced":                           "1",
                "id":                                 "",
                "task_title_id":                      "",
                "task_title":                         title,
                "description_field":                  details,
                "element":                            [],
                "date_start":                         start.strftime("%Y-%m-%d"),
                "hour_start":                         start.strftime("%H"),
                "minute_start":                       start.strftime("%M"),
                "date_end":                           end.strftime("%Y-%m-%d"),
                "hour_end":                           end.strftime("%H"),
                "minute_end":                         end.strftime("%M"),
                "locations":                          str(site),
                "owners":                             [str(_o) for _o in owners] if (owners is not None) else [],
                "duration_hour":                      str(_d[0]) if _d[0] != 0 else str(_d[0]).zfill(2),
                "duration_minute":                    str(_d[1]).zfill(2),
                "duration_second":                    str(_d[2]).zfill(2),
                "remove_upload":                      "",
                "repeat_interval_period":             "never",
                "repeat_interval_length":             "1",
                "frequency_monthly_type":             "monthly",
                "frequency_stop_repeat_number_value": "",
                "end_after_date":                     "",
                "frequency_stop_repeat":              "0",
                "sampling_select":                    "",
                "owner_roles":                        [],
                "approvers":                          [str(_a) for _a in approvers] if (approvers is not None) else [],
                "approver_roles":                     [],
                "watchers":                           [str(_w) for _w in watchers] if (watchers is not None) else [],
                "watcher_roles":                      [],
                "labels":                             [],
                "undefined":                          [],
                "task_sampling_select":               [],
                "task_complete_emails":               0,
                "task_canceled_emails":               0,
                "translations":                       {
                        f"{language.lower()}_{language.upper()}": title
                        },
                "description_translations":           {
                        f"{language.lower()}_{language.upper()}": details
                        },
                "floors_spaces":                      dict() if spaces is None else spaces
                }

    def __getitem__(self, item: str):
        """ Returns the task property by name """
        return self._task[item]

    def get(self, token: str) -> str:
        """
        Get the FA task as stringified JSON, given token value.

        :param token: FA API _token value
        :return: Full JSON as string, for POSTing to FA API
        """
        return dumps({"_token": token, **self._task}, ensure_ascii=False)

    def setrecurrence(self,
                      repeat: str,
                      *,
                      interval: Optional[int] = None,
                      dayset: Optional[List[str]] = None,
                      weekdayrepeat: Optional[bool] = None,
                      monthset: Optional[List[str]] = None,
                      end: Optional[Union[datetime, int]] = None,
                      ) -> None:
        """
        Sets the given recurrence pattern

        :param repeat: uppercased repetition frequency, "DAILY", "MONTHLY", and etc.
        :param interval: optional interval integer, 1 means repeat each period, 2 means one in two periods, and so on,
                         default is repeat each period
        :param dayset: optional list of strings representing day of the week to repeat, default is repeating each day,
                       for example ["1", "2", "7"], used only for "DAILY" frequency, ignored for other frequencies
        :param weekdayrepeat: optional only for monthly frequency, set to True to repeat monthly on the same day
                              of week as first task occurence, default is False which means repeat monthly the same day
                              of month; used only for "MONTHLY" frequency, ignored for other frequencies
        :param monthset: optional list of strings representing monthes to repeat, default is repeating each month,
                         for example ["3", "5", "6"]; used only for "MONTHLY" frequency, ignored for other frequencies
        :param end: optional datetime date after which stop task repetition, last repetition can happen on this date,
                    or if integer given then number of repetitions, default is None which means task is planned forever
        """
        # Check frequency
        if repeat in self.supportedfreqs():
            self._task["repeat_interval_period"] = repeat.lower()
        else:
            raise NotImplementedError(f"Not supported repetition frequency: {repeat}")
        # Check interval
        if interval is None:
            self._task["repeat_interval_length"] = str(1)
        else:
            if isinstance(interval, int) and interval > 0:
                self._task["repeat_interval_length"] = str(interval)
            else:
                raise RuntimeError(f"Wrong interval given: {interval}")
        # Check allowed days parameter
        if dayset is not None and repeat == "DAILY":
            if isinstance(dayset, list):
                for _i in dayset:
                    if not isinstance(_i, str) or int(_i) not in [1, 2, 3, 4, 5, 6, 7]:
                        raise RuntimeError(f"Wrong day given in day set: {_i}")
                _items_count = 0
                for _i in range(7):
                    if str(_i + 1) in dayset:
                        _items_count += 1
                if _items_count < 7:
                    self._task["frequency_daily_repeat"] = dayset
        # Check weekday repeat parameter
        if weekdayrepeat is not None and repeat == "MONTHLY":
            if isinstance(weekdayrepeat, bool):
                if weekdayrepeat:
                    self._task["frequency_monthly_type"] = "weekly"
            else:
                raise TypeError(f"Wrong value of weekdayrepeat given: {weekdayrepeat}")
        # Check allowed months parameter
        if monthset is not None and repeat == "MONTHLY":
            if isinstance(monthset, list):
                for _i in monthset:
                    if not isinstance(_i, str) or int(_i) not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                        raise RuntimeError(f"Wrong month given in month set: {_i}")
                _items_count = 0
                for _i in range(12):
                    if str(_i + 1) in monthset:
                        _items_count += 1
                if _items_count < 12:
                    self._task["frequency_monthly_repeat"] = monthset
        # Check end date or number repetitions
        if end is not None:
            if isinstance(end, datetime):
                self._task["end_after_date"] = end.strftime("%d-%m-%Y")
                self._task["frequency_stop_repeat"] = str(2)
            elif isinstance(end, int) and end > 0:
                self._task["frequency_stop_repeat_number_value"] = end
                self._task["frequency_stop_repeat"] = str(1)
            else:
                raise RuntimeError(f"Wrong end parameter given: {end}")

    @staticmethod
    def supportedfreqs() -> List[str]:
        """
        :return: list of supported recurrence frequencies
        """
        return ["DAILY", "MONTHLY"]
