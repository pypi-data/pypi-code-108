from isc_common.auth.models.user import User
from isc_common.http.DSRequest import DSRequest
from isc_common.http.RPCResponse import RPCResponseConstant


class ChangePassRequest(DSRequest):
    def __init__(self, request):
        DSRequest.__init__(self, request)
        data = self.get_data()

        try:
            user = User.objects.get(pk=data.get('userId', None))
            if user.check_password(data.get('oldPassword', None)):
                user.set_password(data.get('password', None))
                self.response = dict(status=RPCResponseConstant.statusSuccess)
            else:
                self.response = dict(status=RPCResponseConstant.statusValidationError, errorMessage="Пароль не изменен, проверьте вводимые параметры.")

        except Exception as ex:
            self.response = dict(status=RPCResponseConstant.statusFailure, errorMessage=str(ex))
