from isc_common.isc.data_binding.criterion import Criterion


class AdvancedCriteria(Criterion):
    _constructor = None
    criteria = []

    def get_criterion(self, field_name):
        if isinstance(self.criteria, list):
            return list(filter(lambda x: x.fieldName == field_name, self.criteria))
        else:
            return None

    def __init__(self, **kwargs):
        lst = kwargs.get('lst')
        if isinstance(lst, list):
            for l in lst:
                for k, v in l.items():
                    if isinstance(v, list):
                        setattr(self, k, [AdvancedCriteria(**criterion) if criterion.get('_constructor') == 'AdvancedCriteria' else Criterion(**criterion) for criterion in v])
                    else:
                        setattr(self, k, v() if callable(v) else v)

        else:
            for k, v in kwargs.items():
                if isinstance(v, list):
                    setattr(self, k, [AdvancedCriteria(**criterion) if criterion.get('_constructor') == 'AdvancedCriteria' else Criterion(**criterion) for criterion in v])
                else:
                    setattr(self, k, v() if callable(v) else v)
