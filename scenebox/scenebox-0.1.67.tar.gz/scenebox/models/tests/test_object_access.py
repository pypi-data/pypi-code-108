#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#

import pytest

from ..object_access import ObjectAccess, ObjectAccessError, ObjectAccessMedium


class TestObjectAccess:
    def test_valid_object_access_1(self):

        url = "http://test"
        object_access = ObjectAccess(url=url,
                                     id="abc")

        assert object_access.url == url
        assert object_access.to_dic() == {'id': 'abc',
                                          'medium': 'url',
                                          'url': 'http://test'}

    def test_valid_object_access_2(self):

        id = "test"
        object_access = ObjectAccess(id=id,
                                     filename="this_file")

        assert object_access.id == id
        assert object_access.to_dic() == {'id': 'test',
                                          'medium': 'asset-manager',
                                          'filename': 'this_file'}

    def test_valid_object_access_3(self):
        object_access = ObjectAccess.from_dict(
            {'id': 'test',
             'medium': 'asset-manager',
             'filename': 'this_file'})
        assert object_access.id == 'test'
        assert object_access.medium == 'asset-manager'

    def test_invalid_object_access_1(self):
        with pytest.raises(ObjectAccessError):
            ObjectAccess()
