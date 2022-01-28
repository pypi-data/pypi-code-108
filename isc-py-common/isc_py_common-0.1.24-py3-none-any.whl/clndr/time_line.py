import calendar
import datetime
import uuid

from django.conf import settings

from clndr.calendar_event import CalendarEvent, CalendarEventLinkedList
from clndr.models.calendar_shifts_days import Calendar_shifts_days
from clndr.models.calendars import Calendars
from clndr.models.holidays import Holidays
from clndr.models.shift_day_relax import Shift_day_relax
from isc_common.auth.models.user import User
from isc_common.common import uuid4
from isc_common.ws.progressStack import ProgressStack


class Timeline:
    logger = None
    calendar = None
    calendar_id = None
    head = None
    top_ce = None
    cur_ce = None

    def __init__(self, *args, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v() if callable(v) else v)

        if not self.calendar and not isinstance(self.calendar, Calendars):
            if self.calendar_id:
                self.calendar = Calendars.objects.get(id=self.calendar_id)
        else:
            self.calendar_id = self.calendar.id

        if not self.calendar:
            raise Exception(f'Не выбран календарь.')

        if not self.logger:
            raise Exception(f'Не установлен логер.')

        self.shiftsList = CalendarEventLinkedList()
        self.relaxesList = CalendarEventLinkedList()

        self.shifts = Calendar_shifts_days.objects.filter(calendar=self.calendar)

        self.red_label_days = CalendarEventLinkedList(query=Holidays.objects.filter(calendar=self.calendar, daytype__isholiday=True).order_by(*['begindate']))
        # self.red_label_days.print('red_label_days')

        self.shorted_days = CalendarEventLinkedList(query=Holidays.objects.exclude(calendar=self.calendar, daytype__length__isnull=True))
        # self.shorted_days.print('shorted_days')

    def select_build_shift_day(self, shift, dayweek):
        if dayweek == 0:
            return shift.monday
        elif dayweek == 1:
            return shift.tuesday
        elif dayweek == 2:
            return shift.wednesday
        elif dayweek == 3:
            return shift.thursday
        elif dayweek == 4:
            return shift.friday
        elif dayweek == 5:
            return shift.saturday
        elif dayweek == 6:
            return shift.sunday

    def dayweek_name(self, dayweek):
        dayweek = dayweek.weekday()
        if dayweek == 0:
            return 'Понедельник'
        elif dayweek == 1:
            return 'Вторник'
        elif dayweek == 2:
            return 'Среда'
        elif dayweek == 3:
            return 'Четверг'
        elif dayweek == 4:
            return 'Пятница'
        elif dayweek == 5:
            return 'Суббота'
        elif dayweek == 6:
            return 'Воскресенье'

    def check_next_day(self, begindatetime, endtime):
        if not isinstance(begindatetime, datetime.datetime):
            raise Exception('begindatetime is not datetime.datetime type')

        if not isinstance(endtime, datetime.time):
            raise Exception('endtime is not datetime.time type')

        if begindatetime.hour > endtime.hour or \
                begindatetime.hour == endtime.hour and begindatetime.minute > endtime.minute or \
                begindatetime.hour == endtime.hour and begindatetime.minute == endtime.minute and begindatetime.second > endtime.second or \
                begindatetime.hour == endtime.hour and begindatetime.minute == endtime.minute and begindatetime.second == endtime.second and begindatetime.microsecond > endtime.microsecond:  # or \
            # begindatetime.hour == endtime.hour and begindatetime.minute == endtime.minute and begindatetime.second == endtime.second and begindatetime.microsecond == endtime.microsecond:

            _, month_range = calendar.monthrange(begindatetime.year, begindatetime.month)
            if month_range < begindatetime.day + 1:
                if begindatetime.month + 1 > 12:
                    return datetime.datetime(year=begindatetime.year + 1, month=1, day=1, hour=endtime.hour, minute=endtime.minute, second=endtime.second)
                else:
                    return datetime.datetime(year=begindatetime.year, month=begindatetime.month + 1, day=1, hour=endtime.hour, minute=endtime.minute, second=endtime.second)
            else:
                return datetime.datetime(year=begindatetime.year, month=begindatetime.month, day=begindatetime.day + 1, hour=endtime.hour, minute=endtime.minute, second=endtime.second)
        else:
            return datetime.datetime(year=begindatetime.year, month=begindatetime.month, day=begindatetime.day, hour=endtime.hour, minute=endtime.minute, second=endtime.second)

    def build_shift_day(self, shift, shiftday):
        startDate = self.curdate
        _, month_range = calendar.monthrange(startDate.year, startDate.month)

        red_label_day = self.red_label_days.find(startDate, lambda item, x: x.begindate <= item and x.enddate > item)
        if red_label_day:
            if month_range < startDate.day + 1:
                if red_label_day.month + 1 > 12:
                    self.shiftsList.add(CalendarEvent(
                        id=uuid4(),
                        backgroundColor=red_label_day.daytype.color,
                        endDate=datetime.datetime(year=startDate.year + 1, month=1, day=1),
                        isredlabelday=True,
                        lane=self.calendar.code,
                        name=f'{red_label_day.name}',
                        startDate=startDate,
                    ))
                else:
                    self.shiftsList.add(CalendarEvent(
                        id=uuid4(),
                        backgroundColor=red_label_day.daytype.color,
                        endDate=datetime.datetime(year=startDate.year, month=startDate.month + 1, day=1),
                        isredlabelday=True,
                        lane=self.calendar.code,
                        name=f'{red_label_day.name}',
                        startDate=startDate,
                    ))
            else:
                self.shiftsList.add(CalendarEvent(
                    id=uuid4(),
                    backgroundColor=red_label_day.daytype.color,
                    endDate=datetime.datetime(year=startDate.year, month=startDate.month, day=startDate.day + 1),
                    isredlabelday=True,
                    lane=self.calendar.code,
                    name=f'{red_label_day.name}',
                    startDate=startDate,
                ))

            # self.shiftsList.print('shiftsList')

            return False

        if shiftday.daytype.isholiday:
            if month_range < startDate.day + 1:
                if startDate.month + 1 > 12:
                    endDate = datetime.datetime(year=startDate.year + 1, month=1, day=1)
                else:
                    endDate = datetime.datetime(year=startDate.year, month=startDate.month + 1, day=1)
            else:
                endDate = datetime.datetime(year=startDate.year, month=startDate.month, day=startDate.day + 1)
        else:
            shorted_day = self.shorted_days.find(startDate, lambda item, x: x.begindate <= item and x.enddate > item)

            startDate = self.check_next_day(self.curdate, shiftday.begintime)
            if shorted_day:
                endDate = self.check_next_day(startDate, shiftday.endtime)

                length = (endDate - startDate) - datetime.timedelta(hours=shorted_day.daytype.length.hour + 1, minutes=shorted_day.daytype.length.minute, seconds=shorted_day.daytype.length.second)
                endDate = endDate - length
            else:
                endDate = self.check_next_day(startDate, shiftday.endtime)

        # print(f'curdate: {self.curdate}')
        # print(f'startDate: {startDate}')
        # print(f'endDate: {endDate}')

        self.shiftsList.add(CalendarEvent(
            id=uuid4(),
            backgroundColor=shiftday.daytype.color,
            description=f'{shift.shift.name} {shiftday.description if shiftday.description else ""}',
            endDate=endDate,
            isholiday=shiftday.daytype.isholiday,
            isworkday=not shiftday.daytype.isholiday,
            lane=self.calendar.code,
            name=shiftday.name,
            startDate=startDate,
        ))

        # self.shiftsList.print('shiftsList')

        if not shiftday.daytype.isholiday:
            for shift_day_relax in Shift_day_relax.objects.filter(shiftday=shiftday).order_by(*['relaxorder']):
                startDateRelax = self.check_next_day(startDate, shift_day_relax.begintime)
                endDateRelax = self.check_next_day(startDateRelax, shift_day_relax.endtime)

                # print(f'startDateRelax: {startDateRelax}')
                # print(f'endDateRelax: {endDateRelax}')

                if endDateRelax > endDate:
                    raise Exception(f'Неправильнно заполнен {shift_day_relax} конечное время {endDateRelax} не может быть больше конечного времени смены {endDate}.')

                if startDate < startDate:
                    raise Exception(f'Неправильнно заполнен {shift_day_relax} начальное время {startDate} не может быть меньше начального времени смены {startDate}.')

                # Данные перекура
                self.relaxesList.add(CalendarEvent(
                    id=uuid4(),
                    backgroundColor=shift_day_relax.color,
                    description=f'{shift.shift.name} ({shift_day_relax.name})',
                    endDate=endDateRelax,
                    isholiday=shift_day_relax.shiftday.daytype.isholiday,
                    lane=self.calendar.code,
                    name=shift_day_relax.shiftday.name,
                    startDate=startDateRelax,
                ))

            # self.shiftsList.print('shiftsList')
            return True
        else:
            return False

    def build(self, data):
        self.curdate = self.calendar.begindate
        enddate = self.calendar.enddate
        if data.get('user_id') is None or not isinstance(data.get('user_id'), int):
            raise Exception(f'user_id not found')
        user = User.objects.get(id=data.get('user_id'))

        progress = ProgressStack(
            host=settings.WS_HOST,
            port=settings.WS_PORT,
            channel=f'common_{user.username}',
            user_id=user.id
        )

        id_progress = f'launch_{user.id}'

        demand_str = f'<h3>Создание календаря : {self.calendar.full_name}</h3>'

        cntAll = (self.calendar.enddate - self.calendar.begindate).days
        progress.show(
            title=f'<b>Выполнено</b>',
            label_contents=demand_str,
            cntAll=cntAll,
            id=id_progress
        )

        cnt = 0

        while self.curdate < enddate:
            dayweek = self.curdate.weekday()
            for dw in range(dayweek, 7):
                for shift in self.shifts:
                    if not self.build_shift_day(shift, self.select_build_shift_day(shift, dw)):
                        break

                _, month_range = calendar.monthrange(self.curdate.year, self.curdate.month)

                if month_range < self.curdate.day + 1:
                    if self.curdate.month + 1 > 12:
                        self.curdate = datetime.datetime(year=self.curdate.year + 1, month=1, day=1)
                    else:
                        self.curdate = datetime.datetime(year=self.curdate.year, month=self.curdate.month + 1, day=1)
                else:
                    self.curdate = datetime.datetime(year=self.curdate.year, month=self.curdate.month, day=self.curdate.day + 1)

                progress.setCntDone(cnt, id_progress)
                cnt += 1

                if self.curdate >= enddate:
                    break

        # self.shiftsList.print('shiftsList')
        self.shiftsList.fusion(self.relaxesList)
        progress.close(id=id_progress)
        # self.shiftsList.print('shifts')
        return self.shiftsList
