# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved
from __future__ import unicode_literals

from tcell_agent.policies.base_policy import TCellPolicy


class LocalFileInclusionPolicy(TCellPolicy):
    api_identifier = "lfi"

    def __init__(self, native_agent, enablements, _):
        TCellPolicy.__init__(self)
        self.native_agent = native_agent
        self.lfi_enabled = False

        self.update_enablements(enablements)

    def update_enablements(self, enablements):
        if not enablements:
            enablements = {}

        self.lfi_enabled = enablements.get("local_file_access", False)

    def block_command(self, file_path, mode, opener_class, tcell_context):
        if not self.lfi_enabled:
            return False

        result = self.native_agent.apply_lfi(
            file_path=file_path,
            mode=mode,
            opener_class=opener_class,
            tcell_context=tcell_context
        )
        return result.get('blocked', False)
