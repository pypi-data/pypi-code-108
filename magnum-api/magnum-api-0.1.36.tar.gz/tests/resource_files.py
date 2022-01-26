import os
from pathlib import Path
import pandas as pd


def read_csv_as_pd(relative_full_file_path):
    full_path = create_resources_path(relative_full_file_path)
    return pd.read_csv(full_path, index_col=0)


def create_resources_path(relative_full_file_path):
    path = Path(os.path.dirname(__file__))
    full_path = os.path.join(path, relative_full_file_path)
    return full_path
