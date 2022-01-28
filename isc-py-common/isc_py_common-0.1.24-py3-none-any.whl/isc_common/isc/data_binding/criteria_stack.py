from isc_common import Stack
from isc_common.isc.data_binding.advanced_criteria import AdvancedCriteria
from isc_common.isc.data_binding.criterion import Criterion


class CriteriaStack(Stack):
    def __init__(self, request_criteria):
        self.stack = []

        if isinstance(request_criteria, list):
            self.extend([AdvancedCriteria(**criterion) if criterion.get('_constructor') == 'AdvancedCriteria' else Criterion(**criterion) for criterion in request_criteria])
        elif isinstance(request_criteria, dict):
            self.push(AdvancedCriteria(**request_criteria) if request_criteria.get('_constructor') else Criterion(**request_criteria))
