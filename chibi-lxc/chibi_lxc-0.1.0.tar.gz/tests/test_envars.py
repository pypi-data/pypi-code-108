#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from chibi_lxc.container import Container


class Centos_test( Container ):
    name = 'centos_7_test'
    env_vars = {
        'envar': 'test_1'
    }


class Centos_one_test( Centos_test ):
    name = 'centos_7_test'
    env_vars = {
        'envar': 'test_1_1'
    }


class Centos_two_test( Centos_one_test ):
    name = 'centos_7_test'
    env_vars = {
        'envar2': 'test_2'
    }


class Centos_child( Centos_two_test ):
    name = 'centos_7_test'
    env_vars = {
        'envar2': 'test_2_2'
    }


class Test_envars( unittest.TestCase ):

    def test_the_envars_should_be_additive( self ):
        self.assertIn( 'PROVISION_PATH', Centos_test.env_vars )
        self.assertIn( 'envar', Centos_test.env_vars )
        self.assertNotIn( 'envar2', Centos_test.env_vars )
        self.assertIn( 'PROVISION_PATH', Centos_two_test.env_vars )
        self.assertIn( 'envar', Centos_two_test.env_vars )
        self.assertIn( 'envar2', Centos_two_test.env_vars )

    def test_the_envars_should_remplace_the_newone( self ):
        self.assertEqual( Centos_test.env_vars.envar, 'test_1' )
        self.assertEqual( Centos_one_test.env_vars.envar, 'test_1_1' )
        self.assertEqual( Centos_two_test.env_vars.envar2, 'test_2' )
        self.assertEqual( Centos_child.env_vars.envar2, 'test_2_2' )
