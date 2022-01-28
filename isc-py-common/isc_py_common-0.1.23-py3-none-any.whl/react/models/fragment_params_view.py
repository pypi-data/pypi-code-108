import logging

from django.conf import settings
from django.db.models import TextField, DecimalField, BooleanField, SmallIntegerField

from isc_common.fields.name_field import NameField
from isc_common.fields.related import ForeignKeyProtect
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet
from isc_common.models.images import Images
from react.models.fragment_param_types import Fragment_param_types
from react.models.fragment_params import Fragment_paramsManager, Fragment_params
from react.models.fragments import Fragments

logger = logging.getLogger(__name__)


class Fragment_params_viewQuerySet(BaseRefQuerySet):
    pass


class Fragment_params_viewManager(BaseRefManager):

    @classmethod
    def getRecord(cls, record ) :
        image_src = f'{settings.IMAGE_CONTENT_PROTOCOL}://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{record.image_src}&ws_host={settings.WS_HOST}&ws_port={settings.WS_PORT}&ws_channel={settings.WS_CHANNEL}'

        value_text = record.value_text
        if (value_text is None or value_text.strip() == '') and record.image is not None:
            value_text = image_src
            Fragment_params.objects.filter(id=record.id).update(value_text=value_text)

        res = {
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'fragment_id': record.fragment.id,
            'id': record.id,
            'image_id': record.image.id if record.image else None,
            'image_real_name': record.image_real_name,
            'image_src': image_src,
            'name': record.name,
            'num': record.num,
            'path_file': record.path_file,
            'props': record.props,
            'type__name': record.type.name,
            'type_id': record.type.id,
            'use_generator': record.use_generator,
            'value_dec': record.value_dec,
            'value_text': value_text,
        }
        return res

    def get_queryset(self):
        return Fragment_params_viewQuerySet(self.model, using=self._db)


class Fragment_params_view(BaseRef):
    fragment = ForeignKeyProtect(Fragments)
    image = ForeignKeyProtect(Images, null=True, blank=True)
    image_real_name = NameField(null=True, blank=True)
    image_src = NameField()
    num = SmallIntegerField(null=True, blank=True)
    path_file = TextField(null=True, blank=True)
    props = Fragment_paramsManager.props()
    type = ForeignKeyProtect(Fragment_param_types)
    use_generator = BooleanField()
    value_dec = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_text = TextField(null=True, blank=True)

    objects = Fragment_params_viewManager()

    def __str__(self):
        return f'ID:{self.id}'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Параметры фрагмента'
        db_table = 'react_fragment_params_view'
        managed = False
