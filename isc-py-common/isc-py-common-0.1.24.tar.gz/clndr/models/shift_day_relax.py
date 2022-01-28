import logging
import random

from django.db.models import PositiveIntegerField
from django.forms import model_to_dict

from clndr.models.shift_day import Shift_day
from isc_common import setAttr, delAttr
from isc_common.fields.code_field import CodeField
from isc_common.fields.related import ForeignKeyCascade
from isc_common.fields.time_field import TimeField
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet

logger = logging.getLogger(__name__)


class Shift_day_relaxQuerySet(BaseRefQuerySet):
    def filter(self, *args, **kwargs):
        return super().filter(*args, **kwargs)


class Shift_day_relaxManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'code': record.code,
            'name': record.name,
            'description': record.description,
            'begintime': record.begintime,
            'endtime': record.endtime,
            'shiftday_id': record.shiftday.id,
            'color': record.color,
            'relaxorder': record.relaxorder,
        }
        return res

    def get_queryset(self):
        return Shift_day_relaxQuerySet(self.model, using=self._db)

    def createFromRequest(self, request):
        request = DSRequest(request=request)
        data = request.get_data()
        setAttr(data, 'id', random.randint(1, 100000000))
        return data

    def updateFromRequest(self, request):
        request = DSRequest(request=request)
        return request.get_data()

    # def deleteFromRequest(self, request):
    #     request = DSRequest(request=request)
    #     return 1


class Shift_day_relax(BaseRef):
    color = CodeField()
    relaxorder = PositiveIntegerField()
    shiftday = ForeignKeyCascade(Shift_day)

    begintime = TimeField(verbose_name='Начало периода', db_index=True)
    endtime = TimeField(verbose_name='Конец периода', db_index=True)

    def copy(self):
        data = model_to_dict(Shift_day_relax.objects.get(id=self.id))
        delAttr(data, 'id')
        return Shift_day_relax.objects.create(**data)

    @property
    def period_html(self):
        return f'<p><u>{self.begintime} - {self.endtime}</u></p>'

    @property
    def html(self):
        descr = '' if self.description is None else f'({self.description})'
        return f'<div><font color="{self.color}"><p><b>{self.name} {descr}</b></p>{self.period_html}</font></div>'

    objects = Shift_day_relaxManager()

    def __str__(self):
        return f"ID={self.id}, " \
            f"code={self.code}, " \
            f"name={self.name}, " \
            f"description={self.description}, " \
            f"color={self.color}, " \
            f"shiftday=[{self.shiftday}]"

    class Meta:
        verbose_name = 'Запланированные перекуры и отдыхи'
        ordering = ['relaxorder', 'shiftday']
        unique_together = (('relaxorder', 'shiftday'),)
