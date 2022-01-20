"""
Created on 20.04.2021

@author: baier
"""
import pandas as pd
import os
from dotenv import load_dotenv
from accessOutlookEmail import create_account, send_email, save_attachment

load_dotenv()


def edit_save_report(save_to_folder: str, account):
    # open Excel
    os.chdir(save_to_folder)
    df = pd.read_excel(save_attachment('JoinITReport', r'U:\baier.ORCA\Attachments', account))
    
    # edit the file
    new_header = df.iloc[1] 
    df = df[2:] 
    df.columns = new_header
    df = df.reset_index(drop=True)
    rows = df[df.columns[0]].count()
    col_c = df['ISIN']
    for isin in range(rows):
        if col_c[isin][:2] != "JP":
            df = df.drop([isin])
            
    # change width of columns
    writer = pd.ExcelWriter(r"U:\baier.ORCA\Attachments\reportJP.xlsx")
    df.to_excel(writer, sheet_name='report', index=False, na_rep='NaN')
    
    # Auto-adjust columns' width
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets['report'].set_column(col_idx, col_idx, column_width)
    
    writer.save()


def main():
    account = create_account(os.getenv('email_robert'), os.getenv('password_robert'))
    edit_save_report(r'U:\baier.ORCA\Attachments', account)

    attachments = []
    os.chdir(r'U:\baier.ORCA\Attachments')
    with open('reportJP.xlsx', 'rb') as f:
        content = f.read()
    attachments.append((r'reportJP.xlsx', content))

    send_email(account, 'JP Common Stocks', 'This is an automated email - do not reply',
               ['kugler@orcacapital.de'], attachments=attachments)
    print('Email was sent to Kugler Christoph')


if __name__ == '__main__':
    main()
