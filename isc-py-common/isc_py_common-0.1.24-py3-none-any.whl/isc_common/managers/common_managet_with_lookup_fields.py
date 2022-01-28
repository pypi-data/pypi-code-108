from itertools import groupby

from django.db import transaction

from isc_common import delAttr, setAttr
from isc_common.models.audit import AuditManager, AuditQuerySet
from isc_common.models.base_ref import BaseRefQuerySet


class CommonManagetWithLookUpFieldsQuerySet(AuditQuerySet):
    def create(self, **kwargs):
        setAttr(kwargs, '_operation', 'create')
        return self._create_or_update(**kwargs)

    def update(self, **kwargs):
        setAttr(kwargs, '_operation', 'update')
        return self._create_or_update(**kwargs)

    @transaction.atomic
    def _create_or_update(self, **kwargs):
        def get_objects_data(**data):
            for key in data:
                key1 = None
                key2 = key

                if key.find('__') != -1:
                    key1 = key[0:key.find('__')]
                    key2 = key[key.find('__') + 2:]
                elif key.endswith('_id'):
                    key1 = key[0:key.rfind('_')]
                    key2 = key[key.rfind('_') + 1:]

                yield (((key1, key2), data[key]))

        data_for_grouping = get_objects_data(**kwargs)

        data = dict()
        operation = kwargs.get('_operation')

        for key, group in groupby(data_for_grouping, lambda x: x[0][0]):
            if not data.get(key):
                if key:
                    forignFld = self.get_field(key)
                    group1 = [x for x in group]
                    id = self.get_id_tuple(group1)
                    try:
                        if forignFld:
                            if id is None:
                                data[key] = None
                            else:
                                if isinstance(id, list):
                                    id = id[0]
                                obj = forignFld.related_model.objects.get(pk=id)
                                data[key] = obj

                    except forignFld.related_model.DoesNotExist:
                        data1 = dict()
                        for x in group1:
                            key1 = x[0][1]
                            value = x[1]
                            data1[key1] = value
                        try:
                            if forignFld:
                                obj = forignFld.related_model.objects.get(**data1)
                                data[key] = obj
                        except forignFld.related_model.DoesNotExist:
                            pass
                        except forignFld.related_model.MultipleObjectsReturned:
                            for obj in forignFld.related_model.objects.filter(**data1):
                                data[key] = obj
                                break

                else:
                    group1 = [x for x in group]
                    id = self.get_id_tuple(group1)
                    # if id:
                    #     operation = "update"
                    for x in group1:
                        key = x[0][1]
                        value = x[1]
                        if not data.get(key):
                            data[key] = value

        delAttr(data, 'isFolder')
        delAttr(data, '_operation')
        if operation == 'create':
            return super().create(**data)
        else:
            return super().update(**data)


class  CommonManagetWithLookUpFieldsBaseRefQuerySet(CommonManagetWithLookUpFieldsQuerySet, BaseRefQuerySet):
    pass

class CommonManagetWithLookUpFieldsManager(AuditManager):

    def merge_two_dicts(self, x, y):
        z = x.copy()  # start with x's keys and values
        z.update(y)  # modifies z with y's keys and values & returns None
        return z

    def get_queryset(self):
        return CommonManagetWithLookUpFieldsQuerySet(self.model, using=self._db)
