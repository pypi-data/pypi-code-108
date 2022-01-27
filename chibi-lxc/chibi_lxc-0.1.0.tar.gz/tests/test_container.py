#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from chibi_lxc.container import Container, Not_exists_error
from chibi.config import configuration
from chibi.config import basic_config


# configuration.loggers[ 'chibi.command' ].level = 'DEBUG'


class Unexisting_container( Container ):
    name = 'this container should no exists'


class Centos_test( Container ):
    name = 'centos_7_test'


class Centos_test_auto_rename( Centos_test ):
    pass


class Centos_hosts_extra( Centos_test ):
    extra_hosts = [ 'another' ]


class Test_container_created( unittest.TestCase ):
    @classmethod
    def setUpClass( cls ):
        if Centos_test.exists:
            Centos_test.destroy( stop=True )
        Centos_test.create()

    @classmethod
    def tearDownClass( cls ):
        Centos_test.destroy( stop=True )

    def test_exists_should_return_true( self ):
        self.assertTrue( Centos_test.exists )

    def test_after_created_should_exists_the_rootfs( self ):
        self.assertTrue( Centos_test.root.exists )

    def test_after_created_should_exists_the_config( self ):
        self.assertTrue( Centos_test.config.exists )

    def test_should_have_to_read_the_config_like_dict( self ):
        result = Centos_test.config.open().read()
        self.assertIsInstance( result, dict )

    def test_the_config_should_have_the_expected_keys( self ):
        result = Centos_test.config.open().read()
        self.assertIsInstance( result, dict )
        self.assertIn( 'lxc', result )
        self.assertIn( 'arch', result.lxc )
        self.assertIn( 'rootfs', result.lxc )

    def test_should_write_the_new_value_in_the_dict( self ):
        result = Centos_test.config.open().read()
        result.lxc.net["0"].flags = 'down'
        Centos_test.config.open().write( result )
        result = Centos_test.config.open().read()
        self.assertIsInstance( result, dict )
        self.assertEqual( 'down', result.lxc.net["0"].flags )


class Test_container_no_created( unittest.TestCase ):
    @classmethod
    def setUpClass( cls ):
        if Centos_test.exists:
            Centos_test.destroy( stop=True )

    def tearDown( cls ):
        if Centos_test.exists:
            Centos_test.destroy( stop=True )

    def test_should_no_exists( self ):
        with self.assertRaises( Not_exists_error ):
            Unexisting_container.info

    def test_created( self ):
        result = Centos_test.create()
        self.assertTrue( result )
        info = Centos_test.info
        self.assertTrue( info )
        self.assertFalse( Centos_test.is_running )

    def test_exists_should_return_false( self ):
        self.assertFalse( Centos_test.exists )

    def test_should_rename_the_class_if_is_necesary( self ):
        self.assertEqual(
            Centos_test_auto_rename.name, 'Centos_test_auto_rename' )
        self.assertNotEqual( Centos_test.name, Centos_test_auto_rename.name )


class Test_container_hosts( unittest.TestCase ):
    def test_without_extra_hosts_should_return_only_his_name( self ):
        self.assertEqual( Centos_test.hosts, [ Centos_test.name ] )

    def test_with_extra_hosts_should_return_only_his_name( self ):
        expected = [ Centos_hosts_extra.name, *Centos_hosts_extra.extra_hosts ]
        self.assertEqual( Centos_hosts_extra.hosts, expected )
