"""
Created on 20.04.2021

@author: baier
"""

import os
from dotenv import load_dotenv
import pandas as pd
from accessOutlookEmail import save_attachment, create_account

load_dotenv()


def edit_save_morrison(rename_file: str, load_from_folder: str, save_to_folder: str):
    account = create_account(os.getenv('email_robert'), os.getenv('password_robert'))
    # open Excel
    os.chdir(load_from_folder)
    df = pd.read_excel(save_attachment('Morrison', load_from_folder, account))
    z_au_leihe = pd.read_excel(save_to_folder + r'\Z_AU_Leihe.xlsx')

    # edit the file
    df.columns = [c.replace(' ', '_') for c in df.columns]
    ticker = df.Security
    qty = df.Qty_LOCATED
    rows = df[df.columns[0]].count()
    
    z_au_leihe_col_a = z_au_leihe['Security']
    z_au_leihe_col_d = z_au_leihe['Qty LOCATED']
    
    for i in range(rows):
        z_au_leihe_col_a.loc[i] = ticker.iloc[i][0:3]
        z_au_leihe_col_d.loc[i] = qty.iloc[i]

    # save Excel
    os.chdir(save_to_folder)
    z_au_leihe.to_excel(rename_file, index=False)


def main():
    edit_save_morrison(r'testFile.xlsx', r'C:\Users\baier\Downloads', r'O:\Listenpflege\AU_Leihe_Option')


if __name__ == '__main__':
    main()
