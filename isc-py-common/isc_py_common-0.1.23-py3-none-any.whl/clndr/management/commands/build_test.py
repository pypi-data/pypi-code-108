import calendar
import logging
from datetime import datetime

from django.core.management import BaseCommand

from clndr.calendar_event import CalendarEvent, CalendarEventLinkedList
from clndr.models.holidays import Holidays

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Создание модели календаря.'

    shifts = CalendarEventLinkedList()
    relaxes = CalendarEventLinkedList()

    def handle(self, *args, **options):

        self.red_label_days = CalendarEventLinkedList(query=Holidays.objects.filter(daytype__isholiday=True).order_by(*['begindate']))
        self.red_label_days.print('red_label_days')

        self.shorted_days = CalendarEventLinkedList(query=Holidays.objects.exclude(daytype__length__isnull=True))
        self.shorted_days.print('shorted_days')

        year = 2019
        for month in range(1, 12):
            _, month_range = calendar.monthrange(year, month)
            for day in range(1, month_range):
                weekday = calendar.weekday(year, month, day)

                if weekday < 5:
                    item = datetime(year=year, month=month, day=day, hour=7)
                    red_label_day = self.red_label_days.find(item, lambda item, x: x.begindate <= item and x.enddate > item)

                    if not red_label_day:
                        if month_range < day + 1:
                            if month + 1 > 12:
                                self.shifts.add(CalendarEvent(
                                    startDate=datetime(year=year, month=month, day=day, hour=16),
                                    endDate=datetime(year=year + 1, month=1, day=1, hour=1),
                                    iswork=True
                                ))
                            else:
                                self.shifts.add(CalendarEvent(
                                    startDate=datetime(year=year, month=month, day=day, hour=16),
                                    endDate=datetime(year=year, month=month + 1, day=1, hour=1),
                                    iswork=True
                                ))
                        else:
                            self.shifts.add(CalendarEvent(
                                startDate=datetime(year=year, month=month, day=day, hour=16),
                                endDate=datetime(year=year, month=month, day=day + 1, hour=1),
                                iswork=True
                            ))

                        self.relaxes.add(CalendarEvent(
                            startDate=datetime(year=year, month=month, day=day, hour=9),
                            endDate=datetime(year=year, month=month, day=day, hour=9, minute=15),

                        ))

                        self.relaxes.add(CalendarEvent(
                            startDate=datetime(year=year, month=month, day=day, hour=11),
                            endDate=datetime(year=year, month=month, day=day, hour=12),

                        ))

                        self.relaxes.add(CalendarEvent(
                            startDate=datetime(year=year, month=month, day=day, hour=14),
                            endDate=datetime(year=year, month=month, day=day, hour=14, minute=15),

                        ))

                        self.relaxes.add(CalendarEvent(
                            startDate=datetime(year=year, month=month, day=day, hour=18),
                            endDate=datetime(year=year, month=month, day=day, hour=18, minute=15),

                        ))

                        self.relaxes.add(CalendarEvent(
                            startDate=datetime(year=year, month=month, day=day, hour=20),
                            endDate=datetime(year=year, month=month, day=day, hour=21),

                        ))

                        self.relaxes.add(CalendarEvent(
                            startDate=datetime(year=year, month=month, day=day, hour=23),
                            endDate=datetime(year=year, month=month, day=day, hour=23, minute=15),

                        ))
                    else:
                        if month_range < day + 1:
                            if month + 1 > 12:
                                self.shifts.add(CalendarEvent(
                                    startDate=red_label_day.begindate,
                                    endDate=datetime(year=red_label_day.begindate.year + 1, month=1, day=1),
                                    name=red_label_day.name,
                                    isredlabelday=True
                                ))
                            else:
                                self.shifts.add(CalendarEvent(
                                    startDate=red_label_day.begindate,
                                    endDate=datetime(year=red_label_day.begindate.year, month=red_label_day.begindate.month + 1, day=1),
                                    name=red_label_day.name,
                                    isredlabelday=True
                                ))
                        else:
                            self.shifts.add(CalendarEvent(
                                startDate=red_label_day.begindate,
                                endDate=datetime(year=red_label_day.begindate.year, month=red_label_day.begindate.month, day=red_label_day.begindate.day + 1),
                                name=red_label_day.name,
                                isredlabelday=True
                            ))
                else:
                    if month_range < day + 1:
                        if month + 1 > 12:
                            self.shifts.add(CalendarEvent(
                                startDate=datetime(year=year, month=month, day=day),
                                endDate=datetime(year=year + 1, month=1, day=1),
                                iswork=True
                            ))
                        else:
                            self.shifts.add(CalendarEvent(
                                startDate=datetime(year=year, month=month, day=day),
                                endDate=datetime(year=year, month=month + 1, day=1),
                                iswork=True
                            ))
                    else:
                        self.shifts.add(CalendarEvent(
                            startDate=datetime(year=year, month=month, day=day),
                            endDate=datetime(year=year, month=month, day=day + 1),
                            iswork=True
                        ))


        self.shifts.fusion(self.relaxes)
        self.shifts.print('shifts')
