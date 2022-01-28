import logging

from clndr.models.calendars import Calendars
from clndr.models.day_types import Day_types
from isc_common.fields.date_time_field import DateTimeField
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.base_ref import BaseRef

logger = logging.getLogger(__name__)


class HolidaysQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class HolidaysManager(CommonManagetWithLookUpFieldsManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'begindate': record.begindate,
            'enddate': record.enddate,
            'description': record.description,
            'calendar_id': record.calendar.id,
            'daytype_id': record.daytype.id,
            'color': record.daytype.color,
            'daytype__code': record.daytype.code,
            'daytype__name': record.daytype.name,
            'daytype__length': record.daytype.length,
        }
        return res

    def get_queryset(self):
        return HolidaysQuerySet(self.model, using=self._db)


class Holidays(BaseRef):
    calendar = ForeignKeyCascade(Calendars)
    daytype = ForeignKeyProtect(Day_types)
    begindate = DateTimeField(verbose_name='Начало', db_index=True)
    enddate = DateTimeField(verbose_name='Конец', db_index=True)

    objects = HolidaysManager()

    def __str__(self):
        return f"ID={self.id}, " \
               f"code={self.code}, " \
               f"name={self.name}, " \
               f"description={self.description}, " \
               f"daytype=[{self.daytype}], " \
               f"begintime={self.begindate}, " \
               f"endtime={self.enddate}"

    class Meta:
        verbose_name = 'Праздничные дни'
