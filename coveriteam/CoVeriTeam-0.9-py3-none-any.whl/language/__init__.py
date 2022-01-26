# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0


class CoVeriLangException(Exception):
    """
    A bit on error codes:
        1**: failure in policy enforcement
        2**: yaml related errors
    """

    def __init__(self, msg, errorCode=1):
        super().__init__(msg)
        self.errorCode = errorCode
