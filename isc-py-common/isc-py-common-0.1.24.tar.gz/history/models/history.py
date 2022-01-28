import logging

from django.db import connections
from django.db.models import Model, DateTimeField, Manager, TextField, GenericIPAddressField, BigAutoField
from django.utils import timezone

from isc_common.auth.models.user import User
from isc_common.datetime import StrToDate
from isc_common.fields.code_field import CodeField, CodeStrictField, JSONFieldIVC
from isc_common.fields.name_field import NameField
from isc_common.http.DSRequest import DSRequest
from isc_common.managers.common_manager import CommonQuerySet

logger = logging.getLogger(__name__)


class HistoryQuerySet(CommonQuerySet):
    def get_range_rows1(self, request, function=None, distinct_field_names=None):
        request = DSRequest(request=request)

        data = request.get_data()
        begdate = None
        enddate = None
        if data.get('begdate'):
            begdate = StrToDate(data.get('begdate'), '%Y-%m-%d')
        if data.get('enddate'):
            enddate = StrToDate(data.get('enddate'), '%Y-%m-%d')

        with connections['history'].cursor() as cursor:
            if not begdate and not enddate:
                cursor.execute('''select
                                    username,
                                    fio,
                                    count(*)
                                from history_history
                                group by username, fio 
                                order by fio''')
            elif begdate and not enddate:
                cursor.execute('''select
                                        username,
                                        fio,
                                        count(*)
                                    from history_history
                                    where date >= %s
                                    group by username, fio
                                    order by fio''', [begdate])
            elif not begdate and enddate:
                cursor.execute('''select
                                        username,
                                        fio,
                                        count(*)
                                    from history_history
                                    where date <= %s
                                    group by username, fio
                                    order by fio''', [enddate])
            else:
                cursor.execute('''select
                                    username,
                                    fio,
                                    count(*)
                                from history_history
                                where date >= %s and date <= %s
                                group by username, fio
                                order by fio''', [begdate, enddate])
            count_blocks = cursor.fetchall()
            res = dict(
                data=[dict(username=count_block[0], fio=count_block[1], count=count_block[2]) for count_block in count_blocks],
                colors=[dict(fio=user.get_short_name, color=user.color) for user in User.objects.all() if user.color]
            )
            return res


class HistoryManager(Manager):

    def get_queryset(self):
        return HistoryQuerySet(self.model, using=self._db)


class History(Model):
    id = BigAutoField(primary_key=True, verbose_name="Идентификатор")
    date = DateTimeField(db_index=True, default=timezone.now)
    method = CodeField()
    path = CodeStrictField()
    username = NameField()
    fio = NameField()
    data = JSONFieldIVC()
    ip_address = GenericIPAddressField()
    user_agent = TextField()

    objects = HistoryManager()

    def __str__(self):
        return f"method: {self.method} path: {self.path} data{self.data}"

    class Meta:
        verbose_name = 'History'
