import logging

from django.db import transaction
from django.db.models import PositiveIntegerField
from django.forms import model_to_dict

from clndr.models.calendars import Calendars
from clndr.models.shift_day import Shift_day
from clndr.models.shifts import Shifts
from isc_common import delAttr, setAttr
from isc_common.fields.related import ForeignKeyProtect, ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_managet_with_lookup_fields import CommonManagetWithLookUpFieldsManager, CommonManagetWithLookUpFieldsQuerySet
from isc_common.models.audit import AuditModel

logger = logging.getLogger(__name__)


class Calendar_shifts_daysQuerySet(CommonManagetWithLookUpFieldsQuerySet):

    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)

    def delete(self):
        with transaction.atomic():
            for item in self:
                try:
                    item.monday.delete()
                except Exception as ex:
                    logger.warning(ex)

                try:
                    item.tuesday.delete()
                except Exception as ex:
                    logger.warning(ex)

                try:
                    item.wednesday.delete()
                except Exception as ex:
                    logger.warning(ex)

                try:
                    item.thursday.delete()
                except Exception as ex:
                    logger.warning(ex)

                try:
                    item.friday.delete()
                except Exception as ex:
                    logger.warning(ex)

                try:
                    item.saturday.delete()
                except Exception as ex:
                    logger.warning(ex)

                try:
                    item.sunday.delete()
                except Exception as ex:
                    logger.warning(ex)


            return super().delete()


class Calendar_shifts_daysManager(CommonManagetWithLookUpFieldsManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'shift_id': record.shift.id,
            'shift__name': record.shift.name,
            'shift__description': record.shift.name,
            'shiftorder': record.shiftorder,

            'monday_id': record.monday.id,
            'monday__info': record.monday.info,

            'tuesday_id': record.tuesday.id,
            'tuesday__info': record.tuesday.info,

            'wednesday_id': record.wednesday.id,
            'wednesday__info': record.wednesday.info,

            'thursday_id': record.thursday.id,
            'thursday__info': record.thursday.info,

            'friday_id': record.friday.id,
            'friday__info': record.friday.info,

            'saturday_id': record.saturday.id,
            'saturday__info': record.saturday.info,

            'sunday_id': record.sunday.id,
            'sunday__info': record.sunday.info,
        }
        return res

    def get_queryset(self):
        return Calendar_shifts_daysQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        _data = data.copy()
        delAttr(_data, 'monday__info')
        delAttr(_data, 'tuesday__info')
        delAttr(_data, 'wednesday__info')
        delAttr(_data, 'thursday__info')
        delAttr(_data, 'friday__info')
        delAttr(_data, 'saturday__info')
        delAttr(_data, 'sunday__info')

        res = super().create(**_data)
        setAttr(data, 'id', res.id)

        return data

    def copyFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        id = data.get('id')

        calendar_shifts_days = Calendar_shifts_days.objects.get(id=id)
        calendar_shifts_days = calendar_shifts_days.copy()

        calendar_shifts_days = model_to_dict(calendar_shifts_days)

        return calendar_shifts_days


class Calendar_shifts_days(AuditModel):
    calendar = ForeignKeyProtect(Calendars)
    shift = ForeignKeyProtect(Shifts)
    shiftorder = PositiveIntegerField()

    monday = ForeignKeyProtect(Shift_day, related_name='monday_rel')
    tuesday = ForeignKeyProtect(Shift_day, related_name='tuesday_rel')
    wednesday = ForeignKeyProtect(Shift_day, related_name='wednesday_rel')
    thursday = ForeignKeyCascade(Shift_day, related_name='thursday_rel')
    friday = ForeignKeyProtect(Shift_day, related_name='friday_rel')
    saturday = ForeignKeyProtect(Shift_day, related_name='saturday_rel')
    sunday = ForeignKeyProtect(Shift_day, related_name='sunday_rel')

    objects = Calendar_shifts_daysManager()

    def copy(self):
        with transaction.atomic():
            kwargs = dict()
            setAttr(kwargs, 'calendar', self.calendar)
            setAttr(kwargs, 'shift', self.shift)
            setAttr(kwargs, 'shiftorder', self.shiftorder)
            setAttr(kwargs, 'monday', self.monday.copy())
            setAttr(kwargs, 'tuesday', self.tuesday.copy())
            setAttr(kwargs, 'wednesday', self.wednesday.copy())
            setAttr(kwargs, 'thursday', self.thursday.copy())
            setAttr(kwargs, 'friday', self.friday.copy())
            setAttr(kwargs, 'saturday', self.saturday.copy())
            setAttr(kwargs, 'sunday', self.sunday.copy())

            return Calendar_shifts_days.objects.create(**kwargs)

    def __str__(self):
        return f"ID={self.id}, " \
               f"\n  shiftorder={self.shiftorder}, " \
               f"\n\n  calendar=[{self.calendar}], " \
               f"\n\n  shift=[{self.shift}], " \
               f"\n\n  monday=[{self.monday}], " \
               f"\n\n  tuesday=[{self.tuesday}], " \
               f"\n\n  wednesday=[{self.wednesday}], " \
               f"\n\n  thursday=[{self.thursday}], " \
               f"\n\n  friday=[{self.friday}], " \
               f"\n\n  friday=[{self.friday}], " \
               f"\n\n  sunday=[{self.sunday}]"

    class Meta:
        verbose_name = 'Рабочие смены по дням'
        ordering = ['shiftorder']
