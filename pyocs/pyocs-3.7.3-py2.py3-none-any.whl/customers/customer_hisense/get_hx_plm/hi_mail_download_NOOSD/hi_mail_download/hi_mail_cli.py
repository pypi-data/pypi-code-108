import click
from hi_mail_download.py_hisense_mail import HiMailDownload


@click.command()
@click.option('--account', help='海信邮箱账号')
@click.option('--passwd', help='海信邮箱密码')
def hi_mail_cli(account, passwd):
    td = HiMailDownload()
    td.download_file(account, passwd)

