"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved.
Модуль инициализации логирования в приложении
"""

import logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
