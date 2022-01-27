from typing import List

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.autodiagnosis.Fault import Fault


class AutodiagnosisData(CamelModel):
    faults_list: List[Fault] = list()
