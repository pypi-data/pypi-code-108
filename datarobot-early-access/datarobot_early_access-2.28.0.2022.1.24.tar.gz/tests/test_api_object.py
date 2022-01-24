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

import pytest
import trafaret as t
from trafaret import DataError

from datarobot._compat import String
from datarobot.models.api_object import APIObject


def test_safe_data_renaming():
    class Dummy(APIObject):
        _converter = t.Dict({t.Key("renamed") >> "magic": String()})

    data = Dummy._safe_data({"renamed": "nombre"})
    assert data == {"magic": "nombre"}


@pytest.mark.parametrize(
    "data, do_recursive, validation_success",
    [
        ({"l1Prop": {"l2Prop": "x"}}, True, True),
        ({"l1Prop": {"l2_prop": "x"}}, True, True),
        ({"l1Prop": {"l2_prop": "x"}}, False, True),
        ({"l1Prop": {"l2Prop": "x"}}, False, False),
    ],
    ids=[
        "success-converted-recursive",
        "success-convertion_not_needed-recursive",
        "success-convertion_not_needed-not_recursive",
        "failure-no_convertion-not_recursive",
    ],
)
def test_safe_data_recursive(data, do_recursive, validation_success):
    class Dummy(APIObject):
        _converter = t.Dict({t.Key("l1_prop"): t.Dict({t.Key("l2_prop"): String()})})

    if validation_success:
        safe_data = Dummy._safe_data(data, do_recursive=do_recursive)
        assert safe_data == {"l1_prop": {"l2_prop": "x"}}
    else:
        with pytest.raises(DataError):
            Dummy._safe_data(data, do_recursive=do_recursive)
