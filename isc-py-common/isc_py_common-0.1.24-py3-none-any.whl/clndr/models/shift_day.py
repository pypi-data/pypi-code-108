import datetime
import logging

from django.db import transaction
from django.forms import model_to_dict

from clndr.models.day import Day
from clndr.models.day_types import Day_types
from isc_common import delAttr, setAttr
from isc_common.datetime import StrToDate
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.fields.time_field import TimeField
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class Shift_dayQuerySet(CommonManagetWithLookUpFieldsQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Shift_dayManager(CommonManagetWithLookUpFieldsManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,

            'day_id': record.day.id,
            'day__code': record.day.code,
            'day__name': record.day.name,
            'day__description': record.day.description,

            'daytype_id': record.daytype.id,
            'daytype__code': record.daytype.code,
            'daytype__name': record.daytype.name,
            'daytype__color': record.daytype.color,
            'daytype__length': record.daytype.length,

            'color': record.daytype.color,
            'begintime': record.begintime,
            'endtime': record.endtime,
            'description': record.description,

            'info': record.info,
        }
        return res

    def get_queryset(self):
        return Shift_dayQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):

        request = DSRequest(request=request)
        data = request.get_data()

        return self.create_update(data)

    def updateFromRequest(self, request):

        request = DSRequest(request=request)
        data = request.get_data()

        return self.create_update(data)

    def copyFromRequest(self, request):

        request = DSRequest(request=request)
        data = request.get_data()
        id = data.get('id')

        shiftday = Shift_day.objects.get(id = id)
        shiftday = shiftday.copy()

        _shiftday = model_to_dict(shiftday)
        setAttr(_shiftday, 'info', shiftday.info)
        setAttr(_shiftday, 'color', shiftday.color)

        return _shiftday

    def create_update(self, data):
        from clndr.models.shift_day_relax import Shift_day_relax
        shiftdays_relax = data.get('shiftdays_relax')
        delAttr(data, 'shiftdays_relax')
        delAttr(data, 'color')
        delAttr(data, 'info')
        id = data.get('id')
        delAttr(data, 'id')

        with transaction.atomic():
            delAttr(data, 'day')
            delAttr(data, 'daytype')
            delAttr(data, 'daytype')
            delAttr(data, 'day__name')
            delAttr(data, 'daytype__name')

            shiftday, _ = super().update_or_create(id=id, defaults=data)
            Shift_day_relax.objects.filter(shiftday_id=shiftday.id).delete()

            if isinstance(shiftdays_relax, list):
                for shiftday_relax in shiftdays_relax:
                    delAttr(shiftday_relax, 'id')
                    shiftday_relax = self._remove_prop_(shiftday_relax)
                    setAttr(shiftday_relax, 'shiftday', shiftday)
                    Shift_day_relax.objects.create(**shiftday_relax)

            setAttr(data, 'id', shiftday.id)
            setAttr(data, 'color', shiftday.color)
            setAttr(data, 'info', shiftday.info)
            setAttr(data, 'day__name', shiftday.day.name)
            setAttr(data, 'begintime', StrToDate(shiftday.begintime,'%H:%M:%S.%f').time())
            setAttr(data, 'endtime', StrToDate(shiftday.endtime,'%H:%M:%S.%f').time())
            setAttr(data, 'daytype__name', shiftday.daytype.name)
            return data


class Shift_day(AuditModel):
    description = DescriptionField()

    day = ForeignKeyProtect(Day)
    daytype = ForeignKeyProtect(Day_types)

    begintime = TimeField(verbose_name='Начало', db_index=True)
    endtime = TimeField(verbose_name='Конец', db_index=True)

    @property
    def name(self):
        return self.day.name

    def copy(self):
        from clndr.models.shift_day_relax import Shift_day_relax

        data = model_to_dict(Shift_day.objects.get(id=self.id))
        delAttr(data, 'id')

        day = data.get('day')
        delAttr(data, 'day')
        setAttr(data, 'day_id', day)

        daytype = data.get('daytype')
        delAttr(data, 'daytype')
        setAttr(data, 'daytype_id', daytype)

        with transaction.atomic():
            shiftday = Shift_day.objects.create(**data)

            for shift_day_relax in Shift_day_relax.objects.filter(shiftday_id=self.id):
                shift_day_relax = model_to_dict(shift_day_relax)
                delAttr(shift_day_relax, 'id')
                setAttr(shift_day_relax, 'shiftday', shiftday)
                Shift_day_relax.objects.create(**shift_day_relax)

            return shiftday

    @property
    def day_html(self):
        return f'<font color="{self.daytype.color}"><b>{self.day.name} ({self.daytype.name})</b></font>'

    @property
    def period_html(self):
        if self.begintime == self.endtime:
            return ''
        return f'<p><b>{self.begintime} - {self.endtime}</b></p>'

    @property
    def color(self):
        return self.daytype.color

    @property
    def info(self):
        from clndr.models.shift_day_relax import Shift_day_relax
        res = self.day_html
        res += self.period_html

        for sd_rx in Shift_day_relax.objects.filter(shiftday=self).order_by(*['relaxorder']):
            res += sd_rx.html
        return f'<div style="border:1px solid grey; merging: 2px; padding: 5px">{res}</div>'

    objects = Shift_dayManager()

    def __str__(self):
        return f"ID={self.id}, " \
               f"\n  description={self.description}, " \
               f"\n  day=[{self.day}], " \
               f"\n  daytype=[{self.daytype}], " \
               f"\n  begintime={self.begintime}, " \
               f"\n  endtime={self.endtime}"

    class Meta:
        verbose_name = 'День смены'
