import datetime
import telegram
import textwrap
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def mail_to(title: str, text: str, mail_addr='hj3415@hanmail.net') -> bool:
    # 메일을 보내는 함수
    login_id_pass = ('hj3415@gmail.com', 'orlhfaqihcdytvsw')
    # 로그인 인자의 두번째 앱비밀번호는 구글계정 관리에서 설정함.
    smtp = ('smtp.gmail.com', 587)

    msg = MIMEMultipart()
    msg['From'] = login_id_pass[0]
    msg['Subject'] = title
    msg['To'] = mail_addr
    msg.attach(MIMEText(datetime.datetime.today().strftime('%I:%M%p') + '\n' + textwrap.dedent(text)))

    smtp = smtplib.SMTP(smtp[0], smtp[1])
    smtp.ehlo()
    try:
        smtp.starttls()
        smtp.login(login_id_pass[0], login_id_pass[1])
        smtp.sendmail(login_id_pass[0], mail_addr, msg.as_string())
        print(f'Sent mail to {mail_addr} successfully.')
        return True
    except:
        print(f'Unknown error occurred during sending mail to {mail_addr}.')
        return False
    finally:
        smtp.close()


CHAT_ID = '924939307'
BOT_LIST = ['manager', 'dart', 'eval', 'cybos']


def telegram_to(botname: str, text: str, parse_html: bool = False) -> bool:
    # reference from https://pypi.org/project/python-telegram-bot/#learning-by-example
    if botname in BOT_LIST:
        if botname == 'manager':
            token = '1445235613:AAHR5fFT0-9lEoyMmTxXx8VfsafoRnOiZzo'
        elif botname == 'dart':
            token = '1442133926:AAEiknxYWfHsxQgmyVRBOlWTT_vpO3Zc96c'
        elif botname == 'eval':
            token = '1409424097:AAFln-N_Wjfy32uDap4TKB1BjeUr1DvQJBQ'
        elif botname == 'cybos':
            token = '1757566630:AAFntsPJZQ8zWH0DaRe92waFELTzsFzyqmo'
        else:
            raise Exception(f'Invalid bot name : {botname} / {BOT_LIST}')
        bot = telegram.Bot(token=token)

        try:
            if parse_html:
                # Available html tag - <i>, <a href ...>
                bot.send_message(chat_id=CHAT_ID, text=text, parse_mode=telegram.ParseMode.HTML)
            else:
                bot.send_message(chat_id=CHAT_ID, text=textwrap.dedent(text))
            print(f'Sent telegram message successfully.')
            return True
        except:
            print(f'Unknown error occurred during sending message to {botname} bot.')
            return False
    else:
        raise Exception(f'Invalid bot name : {botname} / {BOT_LIST}')
