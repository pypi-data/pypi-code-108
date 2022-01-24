"""
Creates a test case class for use with the unittest library that is built into Python.
"""

from heaserver.service.testcase.mockmongotestcase import get_test_case_cls_default
from heaserver.service.testcase import expectedvalues
from heaserver.volume import service
from heaobject.user import NONE_USER
from heaserver.service.testcase.expectedvalues import ActionSpec

db_store = {
    service.MONGODB_VOLUME_COLLECTION: [{
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
        'type': 'heaobject.volume.Volume',
        'version': None
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
            'type': 'heaobject.volume.Volume',
            'version': None
        }],
    service.MONGODB_FILE_SYSTEM_COLLECTION: [{
        'id': '666f6f2d6261722d71757578',
        'created': None,
        'derived_by': None,
        'derived_from': [],
        'description': 'Access to Amazon Web Services (AWS)',
        'display_name': 'Amazon Web Services',
        'invited': [],
        'modified': None,
        'name': 'aws_file_system',
        'owner': NONE_USER,
        'shared_with': [],
        'source': None,
        'type': 'heaobject.volume.AWSFileSystem',
        'version': None
    },
        {
            'id': '0123456789ab0123456789ab',
            'created': None,
            'derived_by': None,
            'derived_from': [],
            'description': None,
            'display_name': 'Local MongoDB instance',
            'invited': [],
            'modified': None,
            'name': 'local_mongodb_file_system',
            'owner': NONE_USER,
            'shared_with': [],
            'source': None,
            'type': 'heaobject.volume.MongoDBFileSystem',
            'version': None,
            'database_name': 'hea',
            'connection_string': 'mongodb://heauser:heauser@localhost:27017/hea'
        }]
}

VolumeTestCase = get_test_case_cls_default(coll=service.MONGODB_VOLUME_COLLECTION,
                                     wstl_package=service.__package__,
                                     href='http://localhost:8080/volumes/',
                                     fixtures=db_store,
                                     get_actions=[ActionSpec(name='heaserver-volumes-volume-get-properties',
                                                             rel=['properties']),
                                                  ActionSpec(name='heaserver-volumes-volume-get-open-choices',
                                                             url='/volumes/{id}/opener',
                                                             rel=['hea-opener-choices']),
                                                  ActionSpec(name='heaserver-volumes-volume-duplicate',
                                                             url='/volumes/{id}/duplicator',
                                                             rel=['duplicator'])
                                                  ],
                                     get_all_actions=[ActionSpec(name='heaserver-volumes-volume-get-properties',
                                                             rel=['properties']),
                                                      ActionSpec(name='heaserver-volumes-volume-get-open-choices',
                                                                 url='/volumes/{id}/opener',
                                                                 rel=['hea-opener-choices']),
                                                      ActionSpec(name='heaserver-volumes-volume-duplicate',
                                                                 url='/volumes/{id}/duplicator',
                                                                 rel=['duplicator'])],
                                     expected_opener=expectedvalues.LinkSpec(url=f'/volumes/{db_store[service.MONGODB_VOLUME_COLLECTION][0]["id"]}/content', rel=['hea-default', 'application/x.folder']),
                                     duplicate_action_name='heaserver-volumes-volume-duplicate-form',
                                     put_content_status=405)


FileSystemTestCase = get_test_case_cls_default(coll=service.MONGODB_FILE_SYSTEM_COLLECTION,
                                     wstl_package=service.__package__,
                                     href='http://localhost:8080/filesystems/',
                                     fixtures=db_store,
                                     get_actions=[ActionSpec(name='heaserver-volumes-file-system-get-properties',
                                                             rel=['properties']),
                                                  ActionSpec(name='heaserver-volumes-file-system-duplicate',
                                                             url='/filesystems/{id}/duplicator',
                                                             rel=['duplicator'])
                                                  ],
                                     get_all_actions=[ActionSpec(name='heaserver-volumes-file-system-get-properties',
                                                             rel=['properties']),
                                                      ActionSpec(name='heaserver-volumes-file-system-duplicate',
                                                                 url='/filesystems/{id}/duplicator',
                                                                 rel=['duplicator'])],
                                     duplicate_action_name='heaserver-volumes-file-system-duplicate-form',
                                     put_content_status=404)
