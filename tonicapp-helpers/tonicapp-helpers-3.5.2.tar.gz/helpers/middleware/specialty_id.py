import logging

logger = logging.getLogger()


class SpecialtyIdMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_specialty_id = request.META.get('HTTP_SPECIALTY_ID', None)

        specialty_id = None
        if user_specialty_id:
            try:
                specialty_id = int(user_specialty_id)
            except Exception as e:
                logger.warning(f'The specialty id of the user is not a int number. User specialty id: {user_specialty_id}; {e}')

        request.specialty_id = specialty_id

        response = self.get_response(request)

        return response
