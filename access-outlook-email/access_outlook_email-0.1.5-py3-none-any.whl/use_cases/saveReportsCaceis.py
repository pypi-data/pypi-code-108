"""
@author: baier, created on 08.07.2021
This script will provide automatically saved Caceis Files into the desired folder structure.
"""

import os
from accessOutlookEmail import create_account
from exchangelib import Message, FileAttachment, ItemAttachment, EWSDateTime
from dotenv import load_dotenv
import pytz
import datetime

load_dotenv()
account = create_account(os.getenv('email_johanna'), os.getenv('password_johanna'))
day = int(datetime.date.today().strftime("%d"))
month = int(datetime.date.today().strftime("%m"))
year = int(datetime.date.today().strftime("%Y"))
year_str = datetime.date.today().strftime("%Y")
date = (datetime.date.today() + datetime.timedelta(-1)).strftime("%d.%m.%Y")

pytz_tz = pytz.timezone('Europe/Berlin')
py_dt = pytz_tz.localize(datetime.datetime(year, month, day))
today = EWSDateTime.from_datetime(py_dt)


def saveAttachmentCaseisKontoauszuege(exchange_folder_name: str, account_var, lastitems=1):
    dest_fold = rf'Q:\Zwischenlagerung\Abstimmung {year_str}\Caceis\Kontoauszüge'
    folders = os.listdir(dest_fold)

    for monat in folders:
        if monat[0:2] == date[3:5]:
            dest_fold += '\\' + monat
            break

    path = os.path.join(dest_fold, date)
    os.mkdir(path)

    folder = account_var.inbox / exchange_folder_name
    for item in folder.all().order_by('-datetime_received')[:lastitems]:
        if item.datetime_received.astimezone() > today:
            for attachment in item.attachments:
                if isinstance(attachment, FileAttachment):
                    local_path = os.path.join(path, attachment.name)
                    with open(local_path, 'wb') as f:
                        f.write(attachment.content)
                    print('Saved attachment to', local_path)
                elif isinstance(attachment, ItemAttachment):
                    if isinstance(attachment.item, Message):
                        print(attachment.item.subject, attachment.item.body)


def saveAttachmentCaseisClearing(exchange_folder_name: str, account_var, lastitems=1):
    phyabrech_dest_folder = rf'Q:\Zwischenlagerung\Abstimmung {year_str}\Caceis\WP Abrechnungen'
    phyoffpos_dest_folder = rf'Q:\Zwischenlagerung\Abstimmung {year_str}\Caceis\Depotauszüge'
    misctransaction_dest_folder = rf'O:\1 Konvertierer\Caceis\Umbuchungen\{year_str}'

    phyabrech_folders = os.listdir(phyabrech_dest_folder)
    # phyoffposFolders = os.listdir(phyoffpos_dest_folder)
    # misctransactionFolders = os.listdir(misctransaction_dest_folder)

    for monat in phyabrech_folders:
        if monat[0:2] == date[3:5]:
            phyabrech_dest_folder += f'\\{monat}'
            phyoffpos_dest_folder += f'\\{monat}'
            misctransaction_dest_folder += f'\\{monat}'
            break

    local_path = ''
    folder = account_var.inbox / exchange_folder_name
    for item in folder.all().order_by('-datetime_received')[:lastitems]:
        if item.datetime_received.astimezone() > today:
            for attachment in item.attachments:
                if isinstance(attachment, FileAttachment):
                    if attachment.name == 'misctransaction.csv':
                        local_path = os.path.join(misctransaction_dest_folder, date + ' ' + attachment.name)
                        with open(local_path, 'wb') as f:
                            f.write(attachment.content)
                    elif attachment.name == 'phyabrech.pdf':
                        local_path = os.path.join(phyabrech_dest_folder, date + ' ' + attachment.name)
                        with open(local_path, 'wb') as f:
                            f.write(attachment.content)
                    elif attachment.name == 'phyoffpos.pdf':
                        local_path = os.path.join(phyoffpos_dest_folder, date + ' ' + attachment.name)
                        with open(local_path, 'wb') as f:
                            f.write(attachment.content)
                print('Saved attachment to', local_path)


def main():
    saveAttachmentCaseisKontoauszuege(exchange_folder_name='Kontoauszüge Caceis', account_var=account, lastitems=50)
    saveAttachmentCaseisClearing(exchange_folder_name='Clearing Caceis', account_var=account)


if __name__ == '__main__':
    main()
