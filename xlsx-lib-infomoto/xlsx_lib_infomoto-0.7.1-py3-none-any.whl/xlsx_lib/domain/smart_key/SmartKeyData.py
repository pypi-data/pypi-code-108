from typing import List

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.smart_key.Fault import Fault


class SmartKeyData(CamelModel):
    faults_list: List[Fault] = list()
