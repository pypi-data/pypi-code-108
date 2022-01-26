from typing import List

from camel_model.camel_model import CamelModel

from xlsx_lib.domain.abs.Problem import Problem


class AbsData(CamelModel):
    problems_list: List[Problem] = list()
