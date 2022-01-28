#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> from Report import *
>>> data = [
...     {"name": "test0", "level": 5, "id": 0},
...     {"name": "test1", "level": 10, "id": 1},
...     {"name": "test2", "level": 2, "id": 2},
... ]
>>> r = Report(data, "level", "id")
>>> print(r.report_text())
|name         |level        |id           |
|-------------|-------------|-------------|
|test2        |2            |2            |
|test1        |10           |1            |
>>> print(r.report_JSON())
[
    {
        "name": "test2",
        "level": 2,
        "id": 2
    },
    {
        "name": "test1",
        "level": 10,
        "id": 1
    }
]
>>> print(r.report_CSV())
test2,2,2
test1,10,1

>>> print(r.report_HTML())
<table><thead><tr><th>name</th><th>level</th><th>id</th></tr></thead><tbody><tr><td>test2</td><td>2</td><td>2</td></tr><tr><td>test1</td><td>10</td><td>1</td></tr></tbody><tfoot></tfoot></table>
>>> r.statistic()
[{'Name': 'level', 'Sum': 12, 'Max': 10, 'Min': 2, 'Count': 2, 'MaxCount': 1, 'MinCount': 1, 'Average': 6.0, 'Variance': 32, 'Median': 6.0, 'Deviation': 4.0, 'CountGreaterThanAverage': 1, 'CountLessThanAverage': 1, 'CountGreaterThanVariance': 0, 'CountLessThanVariance': 2, 'CountGreaterThanMedian': 1, 'CountLessThanMedian': 1, 'CountGreaterThanDeviation': 1, 'CountLessThanDeviation': 1}, {'Name': 'id', 'Sum': 3, 'Max': 2, 'Min': 1, 'Count': 2, 'MaxCount': 1, 'MinCount': 1, 'Average': 1.5, 'Variance': 0.5, 'Median': 1.5, 'Deviation': 0.5, 'CountGreaterThanAverage': 1, 'CountLessThanAverage': 1, 'CountGreaterThanVariance': 2, 'CountLessThanVariance': 0, 'CountGreaterThanMedian': 1, 'CountLessThanMedian': 1, 'CountGreaterThanDeviation': 2, 'CountLessThanDeviation': 0}]
>>> r2 = Report(r.statistic())
>>> print(r2.report_text(length=26))
|Name                      |Sum                       |Max                       |Min                       |Count                     |MaxCount                  |MinCount                  |Average                   |Variance                  |Median                    |Deviation                 |CountGreaterThanAverage   |CountLessThanAverage      |CountGreaterThanVariance  |CountLessThanVariance     |CountGreaterThanMedian    |CountLessThanMedian       |CountGreaterThanDeviation |CountLessThanDeviation    |
|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|--------------------------|
|level                     |12                        |10                        |2                         |2                         |1                         |1                         |6.0                       |32                        |6.0                       |4.0                       |1                         |1                         |0                         |2                         |1                         |1                         |1                         |1                         |
|id                        |3                         |2                         |1                         |2                         |1                         |1                         |1.5                       |0.5                       |1.5                       |0.5                       |1                         |1                         |2                         |0                         |1                         |1                         |2                         |0                         |
>>>
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = ["Report"]

from typing import Any, Sequence, Union, List, Dict, Tuple
from statistics import fmean, median, pstdev, variance
from collections.abc import Callable, Iterator
from functools import partial
from csv import DictWriter
from io import StringIO
from json import dumps

if __package__:
    from .StringF import strings_tableformat
else:
    from StringF import strings_tableformat


def default_key_function(dict_: dict, attribute: str = None) -> Any:

    """
    This is a key function for sorted or filter function.
    """

    return dict_[attribute]


def customfilter(
    function: Callable, objects: Sequence[dict]
) -> Tuple[List[dict], List[dict]]:

    """
    This function applies a filter on the data.
    """

    new_data = []
    filtered = []
    for object_ in objects:
        if function(object_):
            new_data.append(object_)
        else:
            filtered.append(object_)

    return new_data, filtered


class Report:
    def __init__(
        self,
        objects: Union[Sequence[dict], Sequence[object]],
        sort_value: Union[str, Callable] = None,
        filter_value: Union[str, Callable] = None,
        reverse: bool = False,
    ):
        objects = self.objects = list(self.get_dicts(objects))
        filtered = self.filtered = None
        is_filtered = False

        if isinstance(filter_value, str):
            filter_value = partial(
                default_key_function, attribute=filter_value
            )

        if filter_value is not None:
            r_filter = self.filter = partial(customfilter, filter_value)
            objects, filtered = self.objects, self.filtered = r_filter(objects)
            is_filtered = True

        if isinstance(sort_value, str):
            sort_value = partial(default_key_function, attribute=sort_value)

        if sort_value is not None:
            r_sort = self.sort = partial(
                sorted, key=sort_value, reverse=reverse
            )
            self.objects = r_sort(objects)
            if is_filtered:
                self.filtered = r_sort(filtered)

        self.report_markdown = partial(self.report_text, delimiter="|")

    @staticmethod
    def get_dicts(
        objects: Union[Sequence[dict], Sequence[object]]
    ) -> Iterator[dict]:

        """
        This function returns dict from dict or object.
        """

        for object_ in objects:
            if isinstance(object_, dict):
                yield object_
            else:
                yield {
                    k: v
                    for k, v in object_.__dict__.items()
                    if not isinstance(v, Callable)
                }

    def frequence(
        self, filtered: bool = False, pourcent: bool = True
    ) -> float:

        """
        This function returns the frequence of used/filtered objects
        for report.
        """

        objects, other = (
            (self.filtered, self.objects)
            if filtered
            else (self.objects, self.filtered)
        )

        if not objects or not other:
            return None

        number = len(objects)
        total = number + len(other)

        return (number / total * 100) if pourcent else (number / total)

    def report_text(self, *args, filtered: bool = False, **kwargs) -> str:

        """
        This function returns a text table to report
        objects.

        *args and **kwargs are sent to StringF.strings_tableformat
        """

        objects = self.filtered if filtered else self.objects

        if not objects:
            return None

        columns = objects[0].keys()

        return strings_tableformat(
            [o.values() for o in objects], columns=columns, *args, **kwargs
        )

    def report_HTML(self, filtered: bool = False):

        """
        This function returns a text table to report
        objects.
        """

        objects = self.filtered if filtered else self.objects

        if not objects:
            return None

        columns = (
            "<thead><tr><th>"
            + "</th><th>".join([str(k) for k in objects[0].keys()])
            + "</th></tr></thead>"
        )

        last_index = len(objects) - 1
        body = "<tbody><tr><td>"

        for i, object_ in enumerate(objects):
            body += "</td><td>".join([str(v) for v in object_.values()])
            body += f"</td></tr>{'<tr><td>' if i != last_index else ''}"

        body += "</tbody><tfoot></tfoot>"

        return f"<table>{columns}{body}</table>"

    def report_JSON(
        self, *args, filtered: bool = False, indent: int = 4, **kwargs
    ) -> str:

        """
        This function returns a JSON array of dict to report
        objects.

        *args and **kwargs are sent to json.dumps
        """

        objects = self.filtered if filtered else self.objects

        if not objects:
            return None

        return dumps(objects, *args, indent=indent, **kwargs)

    def report_CSV(self, *args, filtered: bool = False, **kwargs):

        """
        This function returns a CSV content to report
        objects.

        *args and **kwargs are sent to DictWriter.writerows
        """

        objects = self.objects

        if not objects:
            return None

        fieldnames = objects[0].keys()

        report = StringIO()
        csv_report = DictWriter(
            report, dialect="unix", fieldnames=fieldnames, *args, **kwargs
        )
        csv_report.writeheader()
        csv_report.writerows(objects)
        return report.getvalue()

    def statistic(
        self, attributes: Sequence[str] = None, filtered: bool = False
    ) -> List[Dict[str, Union[str, int]]]:

        """
        This function returns statistics to report
        objects statistics.
        """

        objects = self.filtered if filtered else self.objects

        if not objects:
            return None

        if attributes is None:
            attributes = [
                k for k, v in objects[0].items() if isinstance(v, int)
            ]

        data = {a: [] for a in attributes}

        for object_ in objects:
            for attribute in attributes:
                data[attribute].append(object_[attribute])

        statistics = []
        for attribute, values in data.items():
            statistic = {}
            statistics.append(statistic)

            statistic["Name"] = attribute
            statistic["Sum"] = sum(values)
            max_ = statistic["Max"] = max(values)
            min_ = statistic["Min"] = min(values)
            statistic["Count"] = len(values)
            statistic["MaxCount"] = values.count(max_)
            statistic["MinCount"] = values.count(min_)
            average = statistic["Average"] = fmean(values)
            var = statistic["Variance"] = variance(values)
            med = statistic["Median"] = median(values)
            dev = statistic["Deviation"] = pstdev(values)

            gt_average = 0
            lt_average = 0
            gt_variance = 0
            lt_variance = 0
            gt_median = 0
            lt_median = 0
            gt_deviation = 0
            lt_deviation = 0

            for value in values:
                if value > average:
                    gt_average += 1
                elif value < average:
                    lt_average += 1

                if value > var:
                    gt_variance += 1
                elif value < var:
                    lt_variance += 1

                if value > med:
                    gt_median += 1
                elif value < med:
                    lt_median += 1

                if value > dev:
                    gt_deviation += 1
                elif value < dev:
                    lt_deviation += 1

            statistic["CountGreaterThanAverage"] = gt_average
            statistic["CountLessThanAverage"] = lt_average
            statistic["CountGreaterThanVariance"] = gt_variance
            statistic["CountLessThanVariance"] = lt_variance
            statistic["CountGreaterThanMedian"] = gt_median
            statistic["CountLessThanMedian"] = lt_median
            statistic["CountGreaterThanDeviation"] = gt_deviation
            statistic["CountLessThanDeviation"] = lt_deviation

        return statistics
