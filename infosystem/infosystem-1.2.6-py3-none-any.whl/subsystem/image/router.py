from infosystem.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        return [
            {
                'action': 'create',
                'method': 'POST',
                'url': self.collection_url,
                'callback': 'create'
            },
            {
                'action': 'get',
                'method': 'GET',
                'bypass': True,
                'url': self.resource_url,
                'callback': 'get'
            },
            {
                'action': 'list',
                'method': 'GET',
                'url': self.collection_url,
                'callback': 'list'
            },
            {
                'action': 'update',
                'method': 'PUT',
                'url': self.resource_url,
                'callback': 'update'
            },
            {
                'action': 'delete',
                'method': 'DELETE',
                'url': self.resource_url,
                'callback': 'delete'
            }
        ]
