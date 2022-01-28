from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant


class CopyPermission(DSRequest):
    def __init__(self, request):
        from permission.models.usergroup_permission import Usergroup_permission
        from permission.models.user_permission import User_permission

        DSRequest.__init__(self, request)
        data = self.get_data()

        source = data.get('source')
        source_record = source.get('record')
        table_name_source = source.get('table_name')

        desctination = data.get('destination')
        desctination_record = desctination.get('record')
        table_name_destination = desctination.get('table_name')

        if source_record.get('id') == desctination_record.get('id'):
            raise Exception("Источник и приемник не могут совпадать.")

        if source and desctination:
            if table_name_source == 'user_group':
                for user_group_permission in Usergroup_permission.objects.filter(usergroup_id=source_record.get('id')):
                    if table_name_destination == 'user_group':
                        Usergroup_permission.objects.update_or_create(
                            usergroup_id=desctination_record.get('id'),
                            widget=user_group_permission.widget,
                            defaults=dict(permission=user_group_permission.permission)
                        )
                    elif table_name_destination == 'user':
                        User_permission.objects.update_or_create(
                            usergroup_id=desctination_record.get('id'),
                            widget=user_group_permission.widget,
                            defaults=dict(permission=user_group_permission.permission)
                        )
            elif table_name_source == 'user':
                for user_permission in User_permission.objects.filter(usergroup_id=source_record.get('id')):
                    if table_name_destination == 'user_group':
                        Usergroup_permission.objects.update_or_create(
                            usergroup_id=desctination_record.get('id'),
                            widget=user_permission.widget,
                            defaults=dict(permission=user_permission.permission)
                        )
                    elif table_name_destination == 'user':
                        User_permission.objects.update_or_create(
                            usergroup_id=desctination_record.get('id'),
                            widget=user_permission.widget,
                            defaults=dict(permission=user_permission.permission)
                        )

        self.response = dict(status=RPCResponseConstant.statusSuccess)
