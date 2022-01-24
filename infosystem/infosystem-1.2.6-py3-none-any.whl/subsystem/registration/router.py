from infosystem.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return [
            {
                'action': 'register',
                'method': 'POST',
                'url': '/register',
                'callback': 'register',
                'bypass': True
            },
            {
                'action': 'activate',
                'method': 'POST',
                'url': '/activate',
                'callback': 'activate',
                'bypass': True
            }
        ]
