from typing import List

from vatis.asr_commons.config import Language
from vatis.asr_commons.custom_models.model import Model


GENERAL = Model(uid='00000000-0000-0000-0000-000000000001', language=Language.ro_RO, name='General',
                description='Specialized model for television and radio data')

models: List[Model] = [
    GENERAL
]

default = GENERAL
