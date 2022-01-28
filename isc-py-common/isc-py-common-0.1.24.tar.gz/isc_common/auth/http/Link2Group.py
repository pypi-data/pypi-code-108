from isc_common.auth.models.user import User
from isc_common.auth.models.usergroup import UserGroup
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant


class Link2Group(DSRequest):
    def __init__(self, request):
        DSRequest.__init__(self, request)
        data = self.get_data()
        user_ids = data.get('user_ids', None)
        group_ids = data.get('group_ids', None)

        if user_ids and group_ids:
            if not isinstance(user_ids, list):
                user_ids = [user_ids]

            if not isinstance(group_ids, list):
                group_ids = [group_ids]

            for user_id in user_ids:
                user = User.objects.get(id=user_id)
                for group_id in group_ids:
                    try:
                        group = UserGroup.objects.get(id=group_id)
                        user.usergroup.add(group)
                    except:
                        pass

        self.response = dict(status=RPCResponseConstant.statusSuccess, user_ids=user_ids)
