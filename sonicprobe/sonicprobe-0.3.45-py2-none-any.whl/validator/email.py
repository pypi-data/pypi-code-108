# -*- coding: utf-8 -*-
# Copyright (C) 2015-2019 Adrien Delle Cave
# SPDX-License-Identifier: GPL-3.0-or-later
"""sonicprobe.validator.email"""

from sonicprobe.libs import network

class SPValidatorEmail(object): # pylint: disable=useless-object-inheritance
    @staticmethod
    def valid_email_local(local_part):
        return network.valid_email_localpart(local_part)

    @staticmethod
    def valid_email_address(address):
        return network.valid_email_address_literal(address, network.MASK_DOMAIN_TLD)

    @staticmethod
    def validate(email):
        return network.valid_email(email, network.MASK_DOMAIN_TLD)
