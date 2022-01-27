#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from chibi_lxc.container import Container


class Centos_test( Container ):
    name = 'centos_7_test'
    provision_folders = {
        'scripts': 'tests/scripts/'
    }
    status_scripts = (
        'script_test.sh',
    )


class Centos_one_test( Centos_test ):
    name = 'centos_7_test'
    provision_folders = {
        'scripts': 'tests/scripts/'
    }
    status_scripts = (
        ( 'tuple_script.sh', 'asdfsadfasfd' )
    )


class Centos_two_test( Centos_one_test ):
    name = 'centos_7_test'
    provision_folders = {
        'scripts': 'tests/scripts/'
    }


class Centos_child( Centos_test ):
    name = 'centos_7_test'
    provision_folders = {
        'scripts': 'tests/scripts/'
    }
    status_scripts = (
        'another.sh',
    )


class Test_scripts( unittest.TestCase ):
    @classmethod
    def setUpClass( cls ):
        if not Centos_test.exists:
            Centos_test.create()
        Centos_test.provision()
        Centos_test.start()

    def test_prepare_script_should_return_a_tuple( self ):
        script = Centos_test.status_scripts[0]
        result = Centos_test._prepare_script( 'python.py' )
        self.assertEqual( ( 'python3', 'python.py' ), result )
        script = Centos_test.status_scripts[0]
        result = Centos_test._prepare_script( Centos_test.status_scripts[0] )
        self.assertEqual( ( 'bash', script ), result )

    def test_run_scripts_should_work_property( self ):
        result = Centos_test.run_status_scripts()
        self.assertIsNone( result )

    def test_the_scripts_should_have_heritance( self ):
        self.assertEqual( len( Centos_child.status_scripts ), 2 )

    def test_the_scripts_should_no_repeat_by_heritance( self ):
        self.assertEqual(
            Centos_one_test.status_scripts, Centos_two_test.status_scripts
        )
