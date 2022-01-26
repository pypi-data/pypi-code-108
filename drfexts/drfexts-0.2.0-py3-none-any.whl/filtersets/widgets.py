import re

from django.forms import Select
from django_filters.widgets import RangeWidget


class ExtendedSelectMultiple(Select):
    allow_multiple_selected = True

    def value_from_datadict(self, data, files, name):
        values = list()
        pattern = rf"{name}(\[\d*\])?"
        for k, v in data.items():
            if re.fullmatch(pattern, k):
                values.append(v)
        return values

    def value_omitted_from_data(self, data, files, name):
        # An unselected <select multiple> doesn't appear in POST data, so it's
        # never known if the value is actually omitted.
        return False


class ExtendedRangeWidget(RangeWidget):
    """
    支持以下格式查询参数
    1. query/company/?a_min=1&a_max=10 -> data=[1,10]
    2. query/company/?a_min=1 -> data=[1, None]
    3. query/company/?a_max=10 -> data=[None, 10]
    4. query/company/?a=1 -> data=[1,1]
    """

    def value_from_datadict(self, data, files, name):
        return [
            widget.value_from_datadict(data, files, self.suffixed(name, suffix))
            or widget.value_from_datadict(data, files, name)
            for widget, suffix in zip(self.widgets, self.suffixes)
        ]

    def value_omitted_from_data(self, data, files, name):
        return all(
            widget.value_omitted_from_data(data, files, self.suffixed(name, suffix))
            or widget.value_omitted_from_data(data, files, name)
            for widget, suffix in zip(self.widgets, self.suffixes)
        )


class ExtendedDateRangeWidget(ExtendedRangeWidget):
    suffixes = ['after', 'before']
