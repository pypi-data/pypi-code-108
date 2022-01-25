#!/usr/bin/env python

import sys
from pathlib import Path

import pandas as pd

from puddl.db.alchemy import App

fd = Path(sys.argv[1]).expanduser().open()
data_iter = (line.rstrip("\n") for line in fd)
df = pd.DataFrame(data_iter, columns=["line"])

app = App("bash_profile")
app.df_dump(df, "lines", drop_cascade=True)
