"""
Creates a test case class for use with the unittest library that is build into Python.
"""

from heaserver.service.testcase.mockmongotestcase import get_test_case_cls_default
from heaserver.registry import service
from heaobject.user import NONE_USER
from heaserver.service.testcase.expectedvalues import ActionSpec

db_store = {
    service.MONGODB_COMPONENT_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': None,
        'display_name': 'Reximus',
        'invited': [],
        'modified': None,
        'name': 'reximus',
        'owner': NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.registry.Component',
        'version': None,
        'base_url': 'http://localhost/foo',
        'resources': [{
            'type': 'heaobject.registry.Resource',
            'resource_type_name': 'heaobject.folder.Folder',
            'base_path': '/folders',
            'file_system_name': 'DEFAULT_MONGODB'
        }]
    },
        {
            'id': '0123456789ab0123456789ab',
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Luximus',
            'invited': [],
            'modified': None,
            'name': 'luximus',
            'owner': NONE_USER,
            'shared_with': [],
            'source': None,
            'type': 'heaobject.registry.Component',
            'version': None,
            'base_url': 'http://localhost/foo',
            'resources': [{
                'type': 'heaobject.registry.Resource',
                'resource_type_name': 'heaobject.folder.Item',
                'base_path': '/folders',
                'file_system_name': 'DEFAULT_MONGODB'
            }]
        }]}

ComponentTestCase = get_test_case_cls_default(coll=service.MONGODB_COMPONENT_COLLECTION,
                                              href='http://localhost:8080/components/',
                                              wstl_package=service.__package__,
                                              fixtures=db_store,
                                              get_actions=[
                                                  ActionSpec(name='heaserver-registry-component-get-properties',
                                                             rel=['properties']),
                                                  ActionSpec(name='heaserver-registry-component-duplicate',
                                                             url='/components/{id}/duplicator',
                                                             rel=['duplicator'])
                                              ],
                                              get_all_actions=[
                                                  ActionSpec(name='heaserver-registry-component-get-properties',
                                                             rel=['properties']),
                                                  ActionSpec(name='heaserver-registry-component-duplicate',
                                                             url='/components/{id}/duplicator',
                                                             rel=['duplicator'])],
                                              duplicate_action_name='heaserver-registry-component-duplicate-form')
