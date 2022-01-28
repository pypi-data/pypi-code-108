import logging

from bitfield import BitField
from django.db.models import TextField, PositiveIntegerField

from isc_common.auth.models.user import User
from isc_common.fields.code_field import CodeStrictField
from isc_common.fields.related import ForeignKeyCascade
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditQuerySet, AuditManager, AuditModel
from isc_common.number import DelProps

logger = logging.getLogger(__name__)


class ProgressesQuerySet(AuditQuerySet):
    pass


class ProgressesManager(AuditManager):
    @classmethod
    def props(cls):
        return BitField(flags=(
            ('showCancel', 'Показать кнопку отменить процесс'),
        ), default=0, db_index=True)

    def resoreFromRequest(self, request, removed=None, ):
        from isc_common.progress import Progress

        request = DSRequest(request=request)
        for proces in [ProgressesManager.getRecord(record) for record in Progresses.objects.filter(user=request.user)]:
            Progress(
                qty=proces.get('qty'),
                user=request.user,
                id=proces.get('id_progress'),
                message=proces.get('message'),
                label_contents=proces.get('label_contents'),
                title=proces.get('title'),
                props=proces.get('props')
            )

    @classmethod
    def getRecord(cls, record):
        res = {
            'cnt': record.cnt,
            'deliting': record.deliting,
            'editing': record.editing,
            'id': record.id,
            'id_progress': record.id_progress,
            'label_contents': record.label_contents,
            'path': record.path,
            'props': record.props,
            'qty': record.qty,
            'title': record.title,
        }
        return DelProps(res)

    def get_queryset(self):
        return ProgressesQuerySet(self.model, using=self._db)


class Progresses(AuditModel):
    cnt = PositiveIntegerField()
    id_progress = CodeStrictField()
    label_contents = TextField()
    message = TextField()
    qty = PositiveIntegerField()
    props = ProgressesManager.props()
    title = TextField()
    path = CodeStrictField(default='progress')
    user = ForeignKeyCascade(User)

    objects = ProgressesManager()

    def __str__(self):
        return f'ID:{self.id}, title: {self.title}, qty: {self.qty}, cnt: {self.cnt}, id_progress: {self.id_progress}, user: [{self.user}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Отражение запущенных процессов'
        unique_together = (('user', 'id_progress'),)
