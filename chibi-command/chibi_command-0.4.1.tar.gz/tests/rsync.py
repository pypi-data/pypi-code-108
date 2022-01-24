from unittest import TestCase

from chibi_command.rsync import Rsync


class Test_rsync( TestCase ):
    def test_single_option_work( self ):
        options = Rsync.options( '-a' )
        func = Rsync.archive_mode()
        self.assertEqual( options.preview(), func.preview() )

        options = Rsync.options( '-h' )
        func = Rsync.human()
        self.assertEqual( options.preview(), func.preview() )

        options = Rsync.options( '-v' )
        func = Rsync.verbose()
        self.assertEqual( options.preview(), func.preview() )

        options = Rsync.options( '-z' )
        func = Rsync.compress()
        self.assertEqual( options.preview(), func.preview() )

        options = Rsync.options( '--progress' )
        func = Rsync.progress()
        self.assertEqual( options.preview(), func.preview() )

    def test_clone_dir( self ):
        func = Rsync.clone_dir()
        self.assertEqual( 'rsync -a -u', func.preview() )
