from __future__ import annotations

import re
import requests
from requests.exceptions import HTTPError
from rypython.ry365.logger import get_logger
from O365.excel import Range as _Range
from O365.excel import WorkBook as _WorkBook
from O365.excel import WorkSheet as _WorkSheet


logger = get_logger(__file__)

class Range(_Range):
    pattern = r'^.*!(?P<left>[A-Z]+)(?P<top>[0-9]+)(:(?P<right>[A-Z]+)(?P<bottom>[0-9]+))?$'

    def __init__(self, parent=None, session=None, **kwargs):
        super().__init__(parent=parent, session=session, **kwargs)
        self.ws = parent
        self.matchgroup = re.search(self.pattern, self.address).groupdict()

    def batch_update(self, divs: int = 5):
        range_length = len(self.values)
        step = range_length // divs
        top = self.top
        left = self.left
        right = self.right
        batches = [(self.values[i:i+step], i+top) for i in range(0, len(self.values), step)]
        for batch, start_row in batches:
            update_address = f"{left}{start_row}:{right}{start_row + len(batch) - 1}"
            print(update_address)
            _range = self.ws.get_range(update_address)
            _range.update(values=batch, allow_batch=False)

    def update(self, values: list, divs: int = None, allow_batch: bool = True):
        self.values = values
        if allow_batch and (len(self.values) > 1000 or len(self.values[0]) > 1000):
            divs = divs or (len(self.values) // 1000) + 1
            return self.batch_update(divs=divs)
        try:
            super().update()
        except (requests.exceptions.HTTPError, HTTPError):
            logger.error(f"HTTP Error. Adjusting update shape.")
            max_len = max(len(row) for row in self.values)
            for row in self.values:
                for i in range(max_len - len(row)):
                    row.append('')
            self.batch_update()

    @property
    def left(self):
        return self.matchgroup.get('left')

    @property
    def right(self):
        return self.matchgroup.get('right')

    @property
    def top(self):
        return int(self.matchgroup.get('top'))

    @property
    def bottom(self):
        return int(self.matchgroup.get('bottom'))


class WorkSheet(_WorkSheet):
    range_constructor = Range

    def protect(self):
        payload = {
            'options': {
                'allowFormatCells': False,
                'allowFormatColumns': False,
                'allowFormatRows': False,
                'allowInsertColumns': False,
                'allowInsertRows': False,
                'allowInsertHyperlinks': False,
                'allowDeleteColumns': False,
                'allowDeleteRows': False,
                'allowSort': True,
                'allowAutoFilter': True,
                'allowPivotTables': True
            }
        }
        url = self.build_url('/protection/protect')
        return bool(self.session.post(url, json=payload))

    def unprotect(self):
        url = self.build_url('/protection/unprotect')
        return bool(self.session.post(url))

    def auto_fit_columns(self):
        _range = self.get_used_range()
        format = _range.get_format()
        format.auto_fit_columns()


class WorkBook(_WorkBook):
    worksheet_constructor = WorkSheet

    def __init__(self, file_item, *, use_session=False, persist=False):
        super().__init__(file_item, use_session=use_session, persist=persist)
