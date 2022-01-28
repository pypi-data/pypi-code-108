# -*- coding: utf-8 -*-
#
# Copyright (C) 2016-2020 CERN.
#
# Marshmallow-Utils is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test the marshmallow ISO Language."""

import pytest
from marshmallow import Schema, ValidationError

from marshmallow_utils.fields import ISOLangString


class MySchema(Schema):
    f = ISOLangString()


def test_iso639_3_assert():

    assert MySchema().load({'f': "tes"}) == {'f': "tes"}


@pytest.mark.parametrize('test_input', ["te", "12t", "te!", ",te!"])
def test_iso639_3_raise(test_input):

    pytest.raises(ValidationError, MySchema().load, {'f': test_input})
