# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import os

import pytest
from mock import patch

from tcell_agent.instrumentation.lfi import utils


class GetNativeFileModeFromStrTests(object):
    @pytest.mark.parametrize(
        'mode, native_mode', (
            ('r+', 'ReadWrite'),
            ('r+b', 'ReadWrite'),
            ('r+w', 'ReadWrite'),
            ('w+', 'ReadWrite'),
            ('r+a', 'ReadWrite'),
            ('w+t', 'ReadWrite'),
            ('r', 'Read'),
            ('rb', 'Read'),
            ('w', 'Write'),
            ('wb', 'Write'),
            ('rw', 'Write'),
            ('a', 'Write'),
            ('x', 'Write'),
        )
    )
    def test_returns_correct_native_mode(self, mode, native_mode):
        assert utils.get_native_file_mode_from_str(mode) == native_mode


class GetNativeFileModeFromFlagsTests(object):
    @pytest.mark.parametrize(
        'flags, native_mode', (
            (os.O_RDONLY, 'Read'),
            (os.O_WRONLY, 'Write'),
            (os.O_RDONLY | os.O_WRONLY, 'Write'),
            (os.O_RDWR, 'ReadWrite'),
            (os.O_WRONLY | os.O_RDWR, 'ReadWrite'),
        )
    )
    def test_returns_correct_native_mode(self, flags, native_mode):
        assert utils.get_native_file_mode_from_flags(flags) == native_mode


class ShouldBlockFileOpenTests(object):
    def test_returns_false_no_file_path(self):
        assert utils.should_block_file_open(None, 'a', 'b') is False

    @patch('tcell_agent.instrumentation.lfi.utils.TCellAgent')
    def test_returns_false_if_send_lfi_path_discovery_is_disabled(self, agent):
        agent.get_policy.return_value.send_lfi_path_discovery = False
        assert utils.should_block_file_open('a', 'b', 'c') is False

    @patch('tcell_agent.instrumentation.lfi.utils.TCellAgent')
    def test_calls_block_command_with_correct_args(self, agent):
        agent.get_policy.return_value.send_lfi_path_discovery = True
        utils.should_block_file_open('a', 'b', 'c')
        agent.get_policy.return_value.block_command.assert_called_once_with(
            file_path='a', mode='b', opener_class='c', tcell_context=None
        )
