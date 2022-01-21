from unittest import TestCase
from unittest.mock import patch

from magnumapi.geometry.blocks.Block import Block


class TestBlock(TestCase):

    @patch.multiple(Block, __abstractmethods__=set())
    def test_plot_block(self):
        # arrange
        block = Block(cable_def=None,
                      insul_def=None,
                      strand_def=None,
                      conductor_def=None)
        # act
        # assert
        with self.assertRaises(NotImplementedError) as context:
            block.plot_block(None)

        self.assertTrue('This method is not implemented for this class' in str(context.exception))

    @patch.multiple(Block, __abstractmethods__=set())
    def test_build_block(self):
        # arrange
        block = Block(cable_def=None,
                      insul_def=None,
                      strand_def=None,
                      conductor_def=None)
        # act
        # assert
        with self.assertRaises(NotImplementedError) as context:
            block.build_block()

        self.assertTrue('This method is not implemented for this class' in str(context.exception))

    @patch.multiple(Block, __abstractmethods__=set())
    def test_to_roxie_df(self):
        # arrange
        block = Block(cable_def=None,
                      insul_def=None,
                      strand_def=None,
                      conductor_def=None)
        # act
        # assert
        with self.assertRaises(NotImplementedError) as context:
            block.to_block_df()

        self.assertTrue('This method is not implemented for this class' in str(context.exception))
