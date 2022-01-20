from ry365 import O365Account, WorkBook
import pandas as pd
import sys


def main(LOCALE: str, DOMAIN: str):
    SITE = 'msteams_08dd34'
    ACCOUNT = O365Account(site=SITE)

    CODE = f"{LOCALE}-{DOMAIN}"

    PATH = ['Lex Official Production', LOCALE, 'Full_Production', CODE, f"{CODE}-Phase-2", '02_Code-Switching', '03_CodeSwitch_Complete']

    fol = ACCOUNT.get_folder(*PATH, site=SITE)

    items = list(fol.get_items())

    INFILE = items[0]
    wb = WorkBook(INFILE)
    wss = [ws for ws in wb.get_worksheets() if ws.name not in ['Glossary Count']]
    dfs = []
    for ws in wss:
        _range = ws.get_used_range()
        cols, *values = _range.values
        dfs.append(pd.DataFrame(values, columns=cols))
    df = pd.concat(dfs)
    df = df.drop_duplicates('Utterance', keep='last')
    print(f"{CODE} Total Utterances: {len(df)}")
