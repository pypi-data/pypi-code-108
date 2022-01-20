class UserUIDMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_uid = request.META.get('HTTP_TONIC_UID', None)

        request.user_uid = user_uid

        response = self.get_response(request)

        return response
