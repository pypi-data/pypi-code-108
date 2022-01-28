import logging

from bitfield import BitField
from django.conf import settings
from django.db import transaction
from django.db.models import TextField, DecimalField, ProtectedError, SmallIntegerField
from isc_common import delAttr, setAttr
from isc_common.common.functions import get_dict_only_model_field
from isc_common.fields.related import ForeignKeyProtect
from isc_common.http.DSRequest import DSRequest
from isc_common.models.base_ref import BaseRef, BaseRefManager, BaseRefQuerySet
from isc_common.models.images import Images
from react.models.fragment_param_types import Fragment_param_types
from react.models.fragments import Fragments

logger = logging.getLogger(__name__)


class Fragment_paramsQuerySet(BaseRefQuerySet):
    pass


class Fragment_paramsManager(BaseRefManager):

    def updateFromRequest(self, request, propsArr = None):
        request = DSRequest(request=request)
        data = request.get_data()

        data = self.check_data_for_multi_select(data=data)

        cloned_data = data.copy()
        props = self.get_prp(data=data, propsArr=propsArr)
        if props is not None:
            setAttr(cloned_data, 'props', props)

        id = cloned_data.get('id')
        parent = cloned_data.get('parent')

        with transaction.atomic():
            image = super().get(id=id).image
            setAttr(cloned_data, 'image', image)
            delAttr(cloned_data, 'image_id')

            if cloned_data.get('image_real_name') == 'DELETED':
                ex = settings.SSH_CLIENTS.client(settings.FILES_STORE).exists(str(image.attfile))
                if ex is False:
                    try:
                        image.delete()
                    except ProtectedError:
                        pass

                setAttr(cloned_data, 'image_id', None)
                setAttr(cloned_data, 'image', None)

            if isinstance(parent, int):
                delAttr(cloned_data, 'parent')
                setAttr(cloned_data, 'parent_id', parent)
            res = super().filter(id=id).update(**get_dict_only_model_field(data=cloned_data, model=self.model, exclude=['id']))
            logger.debug(f'res: {res}')

        return data

    @classmethod
    def props(cls):
        return BitField(flags=(
            ('use_generator', 'Используется генератором'),  # 1
        ), default=0, db_index=True)

    @classmethod
    def getRecord(cls, record ) :
        res = {
            'code': record.code,
            'deliting': record.deliting,
            'description': record.description,
            'editing': record.editing,
            'fragment_id': record.fragment.id,
            'id': record.id,
            'name': record.name,
            'num': record.num,
            'path_file': record.path_file,
            'type': record.type.id,
            'type__name': record.type.name,
            'type_id': record.type.id,
            'value_dec': record.value_dec,
            'value_text': record.value_text,
        }
        return res

    def get_queryset(self):
        return Fragment_paramsQuerySet(self.model, using=self._db)


class Fragment_params(BaseRef):
    fragment = ForeignKeyProtect(Fragments)
    image = ForeignKeyProtect(Images, null=True, blank=True)
    num = SmallIntegerField(null=True, blank=True)
    path_file = TextField(null=True, blank=True)
    props = Fragment_paramsManager.props()
    type = ForeignKeyProtect(Fragment_param_types)
    value_dec = DecimalField(decimal_places=4, max_digits=19, null=True, blank=True)
    value_text = TextField(null=True, blank=True)

    objects = Fragment_paramsManager()

    def __str__(self):
        return f'ID:{self.id}, ' \
               f'code: {self.code}, ' \
               f'name: {self.name}, ' \
               f'description: {self.description}, ' \
               f'num: {self.num}, ' \
               f'path_file: {self.path_file}, ' \
               f'value_dec: {self.value_dec}, ' \
               f'value_text: {self.value_text}, ' \
               f'type: [{self.type}], ' \
               f'fragment: [{self.fragment}]'

    def __repr__(self):
        return self.__str__()

    class Meta:
        verbose_name = 'Параметры фрагмента'
