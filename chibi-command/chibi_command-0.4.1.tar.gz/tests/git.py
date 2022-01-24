from unittest import TestCase

from chibi.atlas import Chibi_atlas

from chibi_command.git import Git
from chibi.file.temp import Chibi_temp_path
from chibi.file.snippets import cd, current_dir


class Test_git( TestCase ):
    def setUp( self ):
        self.repo_url = 'https://github.com/dem4ply/chibi_command.git'
        self.root_dir = Chibi_temp_path()
        self.old_dir = current_dir()

    def tearDown( self ):
        if current_dir() != self.old_dir:
            cd( self.old_dir )


class Test_git_clone( Test_git ):
    def test_when_clone_with_destiny_should_doe_in_that_place( self ):
        result = Git.clone( self.repo_url, self.root_dir, captive=True )
        self.assertTrue( result )
        self.assertTrue( list( self.root_dir.ls() ) )

    def test_when_clone_without_destiny_should_use_current_path( self ):
        cd( self.root_dir )
        result = Git.clone( self.repo_url, captive=True )
        self.assertTrue( result )
        self.assertTrue( ( self.root_dir + 'chibi_command' ).exists )

class Test_git_checkout( Test_git ):
    def setUp( self ):
        super().setUp()
        Git.clone( self.repo_url, self.root_dir, captive=True )

    def test_when_do_checkout_wihtout_brnach_should_restore_files( self ):
        result = Git.checkout( src=self.root_dir, captive=True )
        self.assertTrue( result )

    def test_when_do_checkout_wiht_brnach_should_change_branch( self ):
        result = Git.checkout(
            branch='origin/master', src=self.root_dir, captive=True )
        self.assertTrue( result )

    def test_with_track_should_change_the_branch( self ):
        result = Git.checkout_track(
            branch='origin/master', src=self.root_dir, captive=True )
        self.assertFalse( result )

class Test_git_pull( Test_git ):
    def setUp( self ):
        super().setUp()
        result = Git.clone( self.repo_url, self.root_dir, captive=True )
        self.assertTrue( result )

    def test_should_work( self ):
        result = Git.pull( src=self.root_dir, captive=True )
        self.assertTrue( result )
