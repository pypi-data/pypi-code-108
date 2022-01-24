# coding: utf-8
#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from datarobot import Model
from tests.utils import assert_equal_py2, assert_equal_py3


class TestRepr(object):
    """Tests of method Model.__repr__"""

    def test_model_type_str(self):
        # when both model_type and id are set
        frozen_model = Model(id="id", model_type="model_type")
        # then repr contains only model_type
        assert repr(frozen_model) == "Model('model_type')"

    def test_model_type_unicode(self):
        # when model_type contains non-ascii characters
        frozen_model = Model(model_type=u"тайп")
        # then repr is an ascii string
        assert_equal_py2(repr(frozen_model), "Model(u'\\u0442\\u0430\\u0439\\u043f')")
        assert_equal_py3(repr(frozen_model), "Model('тайп')")

    def test_id(self):
        # when id is set and model_type is missing
        frozen_model = Model(id="58668cb5bf36cd77a5d8056c")
        # then repr contains id
        assert repr(frozen_model) == "Model('58668cb5bf36cd77a5d8056c')"
