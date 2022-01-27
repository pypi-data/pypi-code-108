# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
import os

from tcell_agent.agent import TCellAgent
from tcell_agent.instrumentation.utils import get_tcell_context
from tcell_agent.policies.policy_types import PolicyTypes

from tcell_agent.instrumentation.decorators import catches_generic_exception

def get_native_file_mode_from_str(mode):
    if '+' in mode:
        return 'ReadWrite'

    if any((m in ('w', 'x', 'a') for m in mode)):
        return 'Write'

    return 'Read'


def get_native_file_mode_from_flags(flags):
    if flags & os.O_RDWR:
        return 'ReadWrite'

    if flags & os.O_WRONLY:
        return 'Write'

    return 'Read'


@catches_generic_exception(__name__,
                           "Error in extracting mode from file open call, assumed 'Read' as default.",
                           return_value="Read")
def get_native_file_mode(mode):
    if type(mode) == str:
        return get_native_file_mode_from_str(mode)

    return get_native_file_mode_from_flags(mode)


def should_block_file_open(file_path, mode, opener_class):
    if not file_path:
        return False

    system_enablements = TCellAgent.get_policy(PolicyTypes.SYSTEM_ENABLEMENTS)
    if not system_enablements.send_lfi_path_discovery:
        return False

    policy = TCellAgent.get_policy(PolicyTypes.LOCAL_FILE_INCLUSION)
    return policy.block_command(
        file_path=file_path,
        mode=mode,
        opener_class=opener_class,
        tcell_context=get_tcell_context()
    )
