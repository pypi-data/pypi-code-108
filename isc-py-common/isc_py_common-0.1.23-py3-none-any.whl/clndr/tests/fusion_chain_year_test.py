import calendar
import unittest
from datetime import datetime

from clndr.calendar_event import CalendarEvent, CalendarEventLinkedList


class FusionChainTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.shifts = CalendarEventLinkedList()
        self.relaxes = CalendarEventLinkedList()

    def test_одного_года_2_смены_со_всеми_отдыхами_и_перекурами(self):
        year = 2019
        for month in range(1, 12):
            _, month_range = calendar.monthrange(year, month)
            for day in range(1, month_range):
                weekday = calendar.weekday(year, month, day)

                if weekday < 5:
                    self.shifts.add(CalendarEvent(
                        startDate=datetime(year=year, month=month, day=day, hour=7),
                        endDate=datetime(year=year, month=month, day=day, hour=16),
                        iswork=True
                    ))

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
                        isrelax=True
                    ))

                    self.relaxes.add(CalendarEvent(
                        startDate=datetime(year=year, month=month, day=day, hour=11),
                        endDate=datetime(year=year, month=month, day=day, hour=12),
                        isrelax=True
                    ))

                    self.relaxes.add(CalendarEvent(
                        startDate=datetime(year=year, month=month, day=day, hour=14),
                        endDate=datetime(year=year, month=month, day=day, hour=14, minute=15),
                        isrelax=True
                    ))

                    self.relaxes.add(CalendarEvent(
                        startDate=datetime(year=year, month=month, day=day, hour=18),
                        endDate=datetime(year=year, month=month, day=day, hour=18, minute=15),
                        isrelax=True
                    ))

                    self.relaxes.add(CalendarEvent(
                        startDate=datetime(year=year, month=month, day=day, hour=20),
                        endDate=datetime(year=year, month=month, day=day, hour=21),
                        isrelax=True
                    ))

                    self.relaxes.add(CalendarEvent(
                        startDate=datetime(year=year, month=month, day=day, hour=23),
                        endDate=datetime(year=year, month=month, day=day, hour=23, minute=15),
                        isrelax=True
                    ))

        self.shifts.fusion(self.relaxes)
        self.shifts.print('shifts')


if __name__ == '__main__':
    unittest.main()
