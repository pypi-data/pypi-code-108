from infosystem.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return super().routes + [
            {
                'action': 'getApplicationRoles',
                'method': 'GET',
                'url': self.resource_url + '/roles',
                'callback': 'get_roles'
            }
        ]
