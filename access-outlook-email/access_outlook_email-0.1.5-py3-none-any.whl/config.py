from exchangelib import DELEGATE, Account, Credentials


def create_credentials(username: str, password: str):
    credentials = Credentials(
        username=username,
        password=password
    )
    return credentials


def create_account(email_address: str, password: str):
    account = Account(
        primary_smtp_address=email_address,
        credentials=create_credentials(email_address, password),
        autodiscover=True,
        access_type=DELEGATE
    )
    return account
