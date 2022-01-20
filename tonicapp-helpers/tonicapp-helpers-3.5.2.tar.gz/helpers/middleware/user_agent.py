from user_agents import parse


class UserAgentMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ua_string = request.META.get('HTTP_USER_AGENT', None)

        if ua_string:
            request.user_agent = parse(ua_string)
        else:
            request.user_agent = None

        return self.get_response(request)
