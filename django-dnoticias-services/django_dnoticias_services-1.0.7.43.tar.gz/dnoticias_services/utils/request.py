from django.contrib.auth import get_user_model

User = get_user_model()


def get_headers(api_key):
    return {
        "Authorization" : "Api-Key {}".format(api_key)
    }


class RequestObject:
    """
    Simulates a request object with is_ajax, GET and POST methods (request is no mutable)
    Used in get user email list datatable because the MetronicProcess class
    uses the request methods.
    """
    def __call__(self, GET={}, POST={}, user_id=None, ajax=False):
        self.GET = GET
        self.POST = POST
        self.ajax = ajax
        self.user = self.set_user(user_id) if user_id else None

    def is_ajax(self):
        return self.ajax

    def set_ajax(self, value):
        self.ajax = bool(value)

    def set_user(self, user_id=None, email=None):
        if user_id:
            filter = {'pk': user_id}
        else:
            filter = {'email': email}

        try:
            self.user = User.objects.get(**filter)
        except:
            self.user = None

request_object = RequestObject()


__all__ = ("request_object")