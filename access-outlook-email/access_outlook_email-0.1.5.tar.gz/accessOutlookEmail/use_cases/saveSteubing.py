"""
Created on 10.05.2021

@author: baier
"""
import os

from dotenv import load_dotenv
from accessOutlookEmail import create_account, save_attachment

load_dotenv()


def main():
    account = create_account(os.getenv('email_robert'), os.getenv('password_robert'))
    save_attachment('Steubing', r'W:\01. ORCA Depot\Z InputConfirms\Steubing', account)


if __name__ == '__main__':
    main()
