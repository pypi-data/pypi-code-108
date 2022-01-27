#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

from chibi_lxc.config import Containers
from chibi_lxc.container import Container


class Centos_test( Container ):
    pass


class Test_conifg_container( unittest.TestCase ):
    def test_container( self ):
        config = Containers()
        self.assertNotIn( Centos_test.name, config )
        config.add( Centos_test )
        self.assertIn( Centos_test.name, config )
        self.assertEqual( config[ Centos_test.name ], Centos_test )
