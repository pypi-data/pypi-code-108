# -*- coding: utf-8 -*-
"""
    tests.build.test_CompositeFactory
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    :copyright: (c) Conceptual Vision Consulting LLC 2015-2016, see AUTHORS for more details.
    :license: MIT, see LICENSE for more details.
"""

from pip_services3_components.build import CompositeFactory


class TestCompositeFactory:

    def test_can_create(self):
        factory = CompositeFactory()
        assert None == factory.can_create(111)
