#!/usr/bin/env python
# -*- coding: utf-8 -*-
from chibi.atlas import Chibi_atlas
from chibi.file import Chibi_path
import unittest
from chibi_lxc.container import Container, Not_exists_error


class Centos_test( Container ):
    name = 'centos_7_test'
    provision_folders = {
        'scripts': 'tests/scripts'
    }


class Test_provision( unittest.TestCase ):
    @classmethod
    def setUpClass( cls ):
        if not Centos_test.exists:
            Centos_test.create()
        Centos_test.provision()

    def test_provision_folder_should_be_a_chibi_atlas( self ):
        self.assertIsInstance( Centos_test.provision_folder, Chibi_atlas )

    def test_provision_folder_should_be_part_of_root( self ):
        for k, v in Centos_test.provision_folder.items():
            with self.subTest(
                    f"provision folder {k} should be part of rootfs",
                    folder=v ):
                self.assertIn( v, Centos_test.root )

    def test_provision_scripts_should_be_a_chibi_path( self ):
        self.assertIsInstance(
            Centos_test.provision_folder.scripts, Chibi_path )

    def test_provision_scripts_should_have_script_test( self ):
        script = Centos_test.provision_folder.scripts + 'script_test.py'
        self.assertTrue( script.exists )
