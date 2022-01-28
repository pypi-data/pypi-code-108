import pandas as pd
from O365.drive import File

from rypython.ry365 import WorkBook


def read_excel365(xl_file: File):
    wb = WorkBook(xl_file)
    wss = wb.get_worksheets()
    ws = wss[0]
    _range = ws.get_used_range()
    cols, *values = _range.values
    df = pd.DataFrame(values, columns=cols)
    df.range = _range
    return df
