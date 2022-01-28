# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************


# Resume Strategy / Old Offline MODE
RESUME_STRATEGY_GET = "get"
RESUME_STRATEGY_GET_OR_CREATE = "get_or_create"
RESUME_STRATEGY_CREATE = "create"

DEPRECATED_OFFLINE_MODE_CREATE = "create"
DEPRECATED_OFFLINE_MODE_APPEND = "append"

DEPRECATED_OFFLINE_MODE_TO_RESUME_STRATEGY_MAP = {
    DEPRECATED_OFFLINE_MODE_APPEND: RESUME_STRATEGY_GET,
    DEPRECATED_OFFLINE_MODE_CREATE: RESUME_STRATEGY_CREATE,
}
