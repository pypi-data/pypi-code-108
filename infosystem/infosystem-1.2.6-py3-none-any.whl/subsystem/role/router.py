from infosystem.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'createPolicies',
                'method': 'POST',
                'url': self.resource_url + '/policies',
                'callback': 'create_policies'
            }
        ]
