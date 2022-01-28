from django.db import connection

from isc_common.auth.models.user import User
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant
from isc_common.json import StrToJson


class GetPermissionRequest(DSRequest):
    def __init__(self, request):
        from permission.models.widgets_trees import Widgets_trees
        from permission.models.user_permission import User_permission

        DSRequest.__init__(self, request)
        data = self.get_data()
        id = data.get('id', None)
        res = []
        widget = None

        try:
            id_widget = data.get('id_widget', None)
            widget = Widgets_trees.objects.get(id_widget=id_widget)
        except Widgets_trees.DoesNotExist:
            pass

        if widget:
            user = User.objects.get(id=id)
            user_permission = None
            try:
                user_permission = User_permission.objects.get(user=user, widget=widget).permission
                if isinstance(user_permission, str):
                    user_permission = StrToJson(user_permission)
            except User_permission.DoesNotExist:
                pass

            grouops_first_level = list(user.usergroup.filter(parent__isnull=True).order_by('id'))
            if len(grouops_first_level) == 0:
                grouops_first_level = list(user.usergroup.filter())

            if user_permission:
                res = [dict(user_id=user.id, permission=user_permission)]

            with connection.cursor() as cursor:
                for group in grouops_first_level:
                    cursor.execute("""WITH RECURSIVE r AS (
                                       SELECT id group_id, 1 AS level
                                       FROM isc_common_usergroup
                                       WHERE id = %s
                                    
                                       UNION ALL
                                    
                                       SELECT g.id  group_id, r.level + 1 AS level
                                       FROM isc_common_usergroup g
                                         JOIN r
                                              ON (g.parent_id = r.group_id) 
                                    )
                                    
                                    SELECT gp.usergroup_id, r.level, gp.permission FROM r 
                                        join isc_common_user_usergroup ug 
                                            on (r.group_id = ug.usergroup_id)
                                        join isc_common_usergroup_permission gp
                                            on (gp.usergroup_id = ug.usergroup_id)
                                        join isc_common_widgets_trees wt
                                            on (wt.id = gp.widget_id)
                                            
                                        where ug.user_id = %s
                                        and wt.id_widget = %s
                                        order by r.level desc """, [group.id, user.id, id_widget])
                    row = cursor.fetchall()
                    for group, level, permission in row:
                        if isinstance(permission, str):
                            permission = StrToJson(permission)
                        res.append(dict(level=level, permission=permission))

                        # print(f'group : {group}, level: {level}, permission: {permission}')

        self.response = dict(response=dict(status=RPCResponseConstant.statusSuccess), data=res)
