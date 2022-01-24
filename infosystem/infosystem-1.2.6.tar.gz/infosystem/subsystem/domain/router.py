from celery.app.utils import Settings
from infosystem.common.subsystem import router


class Router(router.Router):

    def __init__(self, collection, routes=[]):
        super().__init__(collection, routes)

    @property
    def routes(self):
        settings_endpoint = '/settings'
        return super().routes + [
            {
                'action': 'Get Domain By Name',
                'method': 'GET',
                'url': '/domainbyname',
                'callback': 'domain_by_name',
                'bypass': True
            },
            {
                'action': 'Get Domain Logo By Name',
                'method': 'GET',
                'url': '/domainlogobyname',
                'callback': 'domain_logo_by_name',
                'bypass': True
            },
            {
                'action': 'Upload logo to Domain',
                'method': 'PUT',
                'url': self.resource_url + '/logo',
                'callback': 'upload_logo'
            },
            {
                'action': 'Remove logo from Domain',
                'method': 'DELETE',
                'url': self.resource_url + '/logo',
                'callback': 'remove_logo'
            },
            {
                'action': 'Register new Domain',
                'method': 'POST',
                'url': self.collection_url + '/register',
                'callback': 'register',
                'bypass': True
            },
            {
                'action': 'Activate a register Domain',
                'method': 'PUT',
                'url': self.resource_enum_url + '/activate/<id2>',
                'callback': 'activate',
                'bypass': True
            },
            {
                'action': 'Update settings on Domain',
                'method': 'PUT',
                'url': self.resource_url + settings_endpoint,
                'callback': 'update_settings',
                'bypass': False
            },
            {
                'action': 'Remove settings from Domain',
                'method': 'DELETE',
                'url': self.resource_url + settings_endpoint,
                'callback': 'remove_settings',
                'bypass': False
            },
            {
                'action': 'Get settings by keys from Domain',
                'method': 'GET',
                'url': self.resource_url + settings_endpoint,
                'callback': 'get_domain_settings_by_keys',
                'bypass': False
            }
        ]
