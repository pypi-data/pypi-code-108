import logging

from django.db import transaction
from django.forms import model_to_dict

from isc_common.fields.code_field import CodeField , JSONFieldIVC
from isc_common.fields.description_field import DescriptionField
from isc_common.fields.name_field import NameField
from isc_common.http.DSRequest import DSRequest
from isc_common.models.audit import AuditManager
from isc_common.models.base_ref import Hierarcy

logger = logging.getLogger(__name__)


class Widgets_treesManager(AuditManager):
    def createFromRequest(self, request, printRequest=False):
        from isc_common.auth.models.usergroup import UserGroup
        from isc_common.auth.models.user import User
        from permission.models.user_permission import User_permission
        from permission.models.usergroup_permission import Usergroup_permission

        request = DSRequest(request=request)
        id = request.json.get('id')
        table_name = request.json.get('table_name')
        mode = request.json.get('mode')

        data = request.get_data()
        if data.get('id_widget') == '/':
            children = data.get('children')
            if isinstance(children, list) and len(children) > 0:
                data = children[0]

        id_widget = data.get('id_widget')

        if id is None and mode is None and mode is None:
            res, create = super().update_or_create(**data)
            return res

        if table_name == 'widgets_trees':
            name = data.get('name')
            class_name = data.get('class_name')
            description = data.get('description')
            res, create = super().update_or_create(
                id_widget=id_widget,
                defaults=dict(
                    id_widget=id_widget,
                    name=name,
                    class_name=class_name,
                    description=description,
                    structure=data
                )
            )
            return model_to_dict(res)

        if table_name == 'user':
            user = User.objects.get(id=id)
            widget = Widgets_trees.objects.get(id_widget=id_widget)
            if mode == 'write':
                User_permission.objects.update_or_create(
                    user=user,
                    widget=widget,
                    defaults=dict(
                        permission=data
                    ))
            elif mode == 'remove':
                User_permission.objects.filter(
                    user=user,
                    widget=widget).delete()

            return dict()

        if table_name == 'user_group':
            usergroup = UserGroup.objects.get(id=id)
            widget = Widgets_trees.objects.get(id_widget=id_widget)

            if mode == 'write':
                Usergroup_permission.objects.update_or_create(
                    usergroup=usergroup,
                    widget=widget,
                    defaults=dict(
                        permission=data
                    ))
            elif mode == 'remove':
                Usergroup_permission.objects.filter(
                    usergroup=usergroup,
                    widget=widget).delete()

            return dict()

        return dict()

    def deleteFromRequest(self, request, removed=None, ):
        request = DSRequest(request=request)
        res = 0
        tuple_ids = request.get_tuple_ids()
        with transaction.atomic():
            for id, mode in tuple_ids:
                if mode == 'hide':
                    super().filter(id=id).soft_delete()
                    res += 1
                elif mode == 'visible':
                    super().filter(id=id).soft_restore()
                else:
                    qty, _ = super().filter(id=id).delete()
                    res += qty
        return res

    @classmethod
    def getRecord(cls, record):
        res = {
            'id': record.id,
            'id_widget': record.id_widget,
            'name': record.name,
            'class_name': record.class_name,
            'description': record.description,
            'parent_id': record.parent.id if record.parent else None,
        }
        return res


class Widgets_trees(Hierarcy):
    def __str__(self):
        return self.id_widget

    id_widget = CodeField(unique=True)
    name = NameField()
    class_name = NameField()
    description = DescriptionField()
    structure = JSONFieldIVC()

    objects = Widgets_treesManager()

    def __str__(self):
        return f"id: {self.id_widget} name:{self.name_widget}, class_name:{self.class_name}"

    class Meta:
        verbose_name = 'Таблица сохранения деревьев виджетов объектов системы'
