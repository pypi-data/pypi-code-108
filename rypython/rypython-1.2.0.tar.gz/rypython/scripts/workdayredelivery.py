import pandas as pd
import numpy as np
import re
from rypy.rex import capture_all
from pathlib import Path

LOCALE = 'FRCA'
DIVISIONS = ['Dictionary', 'Intents', 'NER']
WDIR = Path.home() / 'Downloads' / f"Assistant_{LOCALE}"

MASTER_FILES = {
    'Dictionary': 'frca_en_US-doccat-allintents.xlsx',
    'NER': 'frca_master_ner_ids_21-04-08.xlsx',
    'Intents': 'frca_master_gt_ids_21-04-08.xlsx'
}

def get_var(string: str):
    d = capture_all(r'^Variant (?P<num>\d)$', string)
    return int(d.get('num')[0])


def scrub(string: str):
    return str(string).replace('  ', ' ')


for DIVISION in DIVISIONS:
    MASTER = WDIR / 'Assistant_Delivery3' / MASTER_FILES[DIVISION]
    df = pd.read_excel(MASTER)
    df = df.where(pd.notnull(df), None)

    TRANS_DICT = {}
    DICT_DIR = WDIR / DIVISION

    print(f"Grabbing translations from {MASTER_FILES[DIVISION]}...")
    for row in df.itertuples(name='row'):
        if row.translation is not None:
            TRANS_DICT.setdefault(scrub(row.text), []).append(row.translation)


    for file in DICT_DIR.iterdir():
        print(f"Grabbing translations from {file.name}...")
        ddf = pd.read_excel(file)
        ddf = ddf.where(pd.notnull(ddf), None)
        for row in ddf.itertuples(name='row'):
            if row.Translation is not None:
                TRANS_DICT.setdefault(scrub(row.English), []).append(row.Translation)

    for row in df.itertuples(name='row'):
        if not row.translation and row.text in TRANS_DICT:
            if len(TRANS_DICT[row.text]) >= get_var(row.variable):
                df.at[row.Index, 'translation'] = TRANS_DICT[scrub(row.text)][get_var(row.variable) - 1]

    OUTFILE = WDIR / f"{MASTER.stem}_master.xlsx"
    df.to_excel(OUTFILE, index=False)
