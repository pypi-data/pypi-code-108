import logging

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.db.models import Model, BooleanField, BigAutoField, DateTimeField, Transform, CharField, TextField, BigIntegerField
from django.utils import timezone
from isc_common import setAttr, delAttr
from isc_common.fields.code_field import CodeField
from isc_common.managers.common_manager import CommonManager, CommonQuerySet
from isc_common.number import GetListFromStringCortege
from transliterate import translit
from transliterate.exceptions import LanguageDetectionError

logger = logging.getLogger(__name__)


class Model_withOldId(Model):
    old_id = BigIntegerField(db_index=True, null=True, blank=True, unique=True)

    class Meta:
        abstract = True


class Model_withOldIdStr(Model):
    old_id = CodeField(unique=True)

    class Meta:
        abstract = True


class Model_withOldIds(Model):
    old_ids = ArrayField(BigIntegerField(), null=True, blank=True, unique=True)

    class Meta:
        abstract = True


class AuditQuerySet(CommonQuerySet):
    def getOptional(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def _check_ed_izm_qty(self, **kwargs):
        if kwargs.get('ed_izm') is not None and kwargs.get('qty') is None or kwargs.get('ed_izm') is None and kwargs.get('qty') is not None:
            raise Exception(f'Единица измерения не может быть указана без количества')

    def __init__(self, model=None, query=None, using=None, hints=None, alive_only=True):
        self.alive_only = alive_only
        super().__init__(model=model, query=query, using=using, hints=hints, alive_only=alive_only)

    def rearrange_parent(self, json):
        # _criteria = json.get('data').get('criteria')
        # if isinstance(_criteria, list):
        #     for criterion in _criteria:
        #         if criterion.get('fieldName') == 'parent_id':
        #             item_id = criterion.get('value')
        #             if (item_id, int):
        #                 criteria_lst = [criterion for criterion in _criteria if criterion.get('fieldName') == 'parent_id' and criterion.get('value') is not None]
        #                 if len(criteria_lst) > 0:
        #                     setAttr(json.get('data'), 'criteria', criteria_lst)
        return json

    def soft_delete(self):
        res = super().update(deleted_at=timezone.now())
        if res > 0:
            return self
        else:
            return None

    def soft_restore(self):
        res = super().update(deleted_at=None)
        return res

    def hard_delete(self):
        res = super().delete()
        return res

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)

    def update(self, **kwargs):
        if kwargs.get('lastmodified') is None:
            setAttr(kwargs, 'lastmodified', timezone.now())
        return super().update(**kwargs)


class AuditModelQuerySet(AuditQuerySet):
    pass


class AuditManager(CommonManager):
    @classmethod
    def getRecord(cls, record):
        return dict()

    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return AuditQuerySet(model=self.model, alive_only=self.alive_only).filter(deleted_at=None)
        return AuditQuerySet(model=self.model, alive_only=self.alive_only)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

    def soft_delete(self):
        return self.get_queryset().soft_delete()

    def soft_restore(self):
        return self.get_queryset().soft_restore()

    def getOptional(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

    def getOr(self, *args, **kwargs):
        alternative = kwargs.get('alternative')
        try:
            delAttr(kwargs, 'alternative')
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            if not callable(alternative):
                raise Exception('alternative must be callable')
            return alternative()
        except self.model.MultipleObjectsReturned as ex:
            old_ids = kwargs.get('old_ids__overlap')
            old_id = kwargs.get('old_id')
            if old_ids is None and old_id is None:
                if not callable(alternative):
                    raise Exception('alternative must be callable')
                return alternative()

            if len(old_ids) > 1:
                raise ex

            old_id = old_ids[0]

            for item in self.filter(*args, **kwargs):
                if len(item.old_ids) > 1:
                    item.old_ids = list(filter(lambda x: x != old_id, item.old_ids))
                    item.save()

            return self.get(*args, **kwargs)

    def get_record(self, record):
        record = self.get(id=record.id if isinstance(record, Model) else record.get('id'))
        self.getRecord(record=record)


class AuditModelManager(AuditManager):
    pass


class Manager(CommonManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return AuditQuerySet(model=self.model)


class AuditModel(Model):
    id = BigAutoField(primary_key=True, verbose_name="Идентификатор")
    deleted_at = DateTimeField(verbose_name="Дата мягкого удаления", null=True, blank=True, db_index=True)
    editing = BooleanField(verbose_name="Возможность редактирования", default=True)
    deliting = BooleanField(verbose_name="Возможность удаления", default=True)
    lastmodified = DateTimeField(verbose_name='Последнее обновление', editable=False, db_index=True, default=timezone.now)

    @classmethod
    def get_urls_datas(cls, record, keyimages, model, model_images, main_model, imports, django_model, django_model_images, code=None, add_params=[]):
        from isc_common.number import DelProps

        if not isinstance(record, dict):
            raise Exception('Record must be dict.')

        record = DelProps(record)
        res = list()
        idx = 0
        for keyimage in keyimages:
            real_name, image_src = cls.get_urls_data(
                add_params=add_params[idx] if len(add_params) != 0 else '',
                code=code,
                django_model=django_model,
                django_model_images=django_model_images,
                id=record.get('id'),
                imports=imports,
                keyimage=keyimage,
                main_model=main_model,
                model=model,
                model_images=model_images,
            )
            idx += 1

            real_name, image_id = GetListFromStringCortege(real_name)
            image_src = f'{settings.IMAGE_CONTENT_PROTOCOL}://{settings.IMAGE_CONTENT_HOST}:{settings.IMAGE_CONTENT_PORT}/{image_src}'
            item = {
                f'{keyimage}_image_id': image_id,
                f'{keyimage}_image_src': image_src,
                f'{keyimage}_real_name': real_name,
            }
            res.append(item)

        for urls_data in res:
            for k, v in urls_data.items():
                setAttr(record, k, v)
        return record

    @classmethod
    def get_urls_data(cls, id, keyimage, model, model_images, main_model, imports, django_model, django_model_images, code=None, add_params=''):
        if code is None:
            code = main_model

        if add_params:
            add_params = f'&{add_params}'

        _imports = ','.join(map(lambda x: x.replace(' ', '__'), imports))

        with connection.cursor() as cursor:
            sql_str = f'''select (select (ici.real_name, usi.image_id)
                                        from {model_images} as usi
                                                 join isc_common_images ici on ici.id = usi.image_id
                                                 join isc_common_image_types icit on usi.type_id = icit.id
                                        where usi.main_model_id = cd.id
                                          and icit.code = %s
                                          and icit.keyimage = %s
                                          and usi.deleted_at is null
                                        limit 1)                                                                                                           as real_name,
                                       concat('logic/Imgs/Download/', (
                                           select usi.image_id
                                           from {model_images} as usi
                                                    join isc_common_images ici on ici.id = usi.image_id
                                                    join isc_common_image_types icit on usi.type_id = icit.id
                                           where usi.main_model_id = cd.id
                                             and icit.code = %s
                                             and icit.keyimage = %s
                                             and usi.deleted_at is null
                                           limit 1), '?', 
                                           'code={code}', 
                                           '&', 
                                           'keyimage={keyimage}', 
                                           '&', 
                                           'path={main_model}', 
                                           '&', 
                                           'main_model={main_model}', 
                                           '&', 
                                           'main_model_id=', cd.id, 
                                           '&', 
                                           'imports=', '{_imports}', 
                                           '&', 
                                           'django_model=', '{django_model._meta.object_name}',
                                           '&', 
                                           'django_model_images=', '{django_model_images._meta.object_name}',
                                           '{add_params}'
                                           ) as image_src
                                from {model} as cd
                                where cd.id = %s'''

            cursor.execute(sql_str, [code, keyimage, code, keyimage, id])
            record = cursor.fetchone()
            return record

    @classmethod
    def uncapitalize(cls, str):
        from isc_common.common.functions import uncapitalize
        return uncapitalize(str)

    @classmethod
    def translit(cls, value):
        if isinstance(value, int):
            return str(value)
        elif value is None:
            return None

        try:
            return cls.uncapitalize(translit(value, reversed=True).replace("'", '').replace(' ', '_').replace('.', '_'))
        except LanguageDetectionError:
            return cls.uncapitalize(value.replace("'", '').replace(' ', '_').replace('.', '_'))

    @classmethod
    def dbl_qutes_str(cls, str):
        from isc_common.common.functions import dbl_qutes_str
        return dbl_qutes_str(str)

    @classmethod
    def qutes_str(cls, str):
        from isc_common.common.functions import qutes_str
        return qutes_str(str)

    @property
    def idHidden(self):
        return not self is None

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save()
        return self

    def soft_restore(self):
        self.deleted_at = None
        self.save()
        return self

    objects = AuditManager()
    all_objects = AuditManager(alive_only=False)


class Dbl_spacesValue(Transform):
    lookup_name = 'delete_dbl_spaces'
    function = 'delete_dbl_spaces'


CharField.register_lookup(Dbl_spacesValue)
TextField.register_lookup(Dbl_spacesValue)


class Trim_Value(Transform):
    lookup_name = 'trim'
    function = 'trim'


CharField.register_lookup(Trim_Value)
TextField.register_lookup(Trim_Value)


class Upper_Value(Transform):
    lookup_name = 'upper'
    function = 'upper'


CharField.register_lookup(Upper_Value)
TextField.register_lookup(Upper_Value)
