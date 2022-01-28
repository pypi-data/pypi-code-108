import calendar
import unittest
from datetime import datetime

from clndr.calendar_event import CalendarEvent, CalendarEventLinkedList


class FusionChainTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.shifts = CalendarEventLinkedList()
        self.relaxes = CalendarEventLinkedList()
        # self.red_letter_days = CalendarEventLinkedList()
        #
        # self.red_letter_days.add(
        #     CalendarEvent(
        #         startDate=datetime(year=2019, month=1, day=1, hour=0, minute=0, second=0),
        #         endDate=datetime(year=2019, month=1, day=9, hour=0, minute=0, second=0),
        #     )
        # )
        #
        # self.red_letter_days.add(
        #     CalendarEvent(
        #         startDate=datetime(year=2019, month=2, day=23, hour=0, minute=0, second=0),
        #         endDate=datetime(year=2019, month=2, day=24, hour=0, minute=0, second=0),
        #     )
        # )
        #
        # self.red_letter_days.add(
        #     CalendarEvent(
        #         startDate=datetime(year=2019, month=3, day=8, hour=0, minute=0, second=0),
        #         endDate=datetime(year=2019, month=3, day=9, hour=0, minute=0, second=0),
        #     )
        # )
        #
        # self.red_letter_days.add(
        #     CalendarEvent(
        #         startDate=datetime(year=2019, month=5, day=1, hour=0, minute=0, second=0),
        #         endDate=datetime(year=2019, month=5, day=4, hour=0, minute=0, second=0),
        #     )
        # )
        #
        # self.red_letter_days.add(
        #     CalendarEvent(
        #         startDate=datetime(year=2019, month=5, day=9, hour=0, minute=0, second=0),
        #         endDate=datetime(year=2019, month=5, day=11, hour=0, minute=0, second=0),
        #     )
        # )
        #
        # self.red_letter_days.add(
        #     CalendarEvent(
        #         startDate=datetime(year=2019, month=6, day=12, hour=0, minute=0, second=0),
        #         endDate=datetime(year=2019, month=6, day=13, hour=0, minute=0, second=0),
        #     )
        # )
        #
        # self.red_letter_days.add(
        #     CalendarEvent(
        #         startDate=datetime(year=2019, month=11, day=4, hour=0, minute=0, second=0),
        #         endDate=datetime(year=2019, month=11, day=5, hour=0, minute=0, second=0),
        #     )
        # )

    def test_одного_рабочего_дня_2_смены_со_всеми_отдыхами_и_перекурами(self):
        self.shifts.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=7),
            endDate=datetime(year=2019, month=1, day=1, hour=16),
        ))

        self.shifts.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=16),
            endDate=datetime(year=2019, month=1, day=2, hour=1),
        ))

        self.relaxes.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=9),
            endDate=datetime(year=2019, month=1, day=1, hour=9, minute=15),
        ))

        self.relaxes.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=11),
            endDate=datetime(year=2019, month=1, day=1, hour=12),
        ))

        self.relaxes.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=14),
            endDate=datetime(year=2019, month=1, day=1, hour=14, minute=15),
        ))

        self.relaxes.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=18),
            endDate=datetime(year=2019, month=1, day=1, hour=18, minute=15),

        ))

        self.relaxes.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=20),
            endDate=datetime(year=2019, month=1, day=1, hour=21),

        ))

        self.relaxes.add(CalendarEvent(
            startDate=datetime(year=2019, month=1, day=1, hour=23),
            endDate=datetime(year=2019, month=1, day=1, hour=23, minute=15),

        ))

        # self.shifts.print('shifts')
        # self.relaxes.print('relaxes')

        self.shifts.fusion(self.relaxes)
        self.shifts.print('shifts')


if __name__ == '__main__':
    unittest.main()
