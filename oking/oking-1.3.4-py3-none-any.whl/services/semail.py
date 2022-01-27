import smtplib
import ssl
import logging
import traceback
from email.message import EmailMessage
# from email.mime.multipart import MIMEMultipart
from src import globals

logger = logging.getLogger()

smtp_server = globals.mail_smtp
smtp_port = globals.mail_port
smtp_admin = globals.mail_admin  # 'smtp.mail'
smtp_password = globals.mail_password  # '5C6117'
email_from = globals.mail_from  # 'OKING <sistemas@openk.com.br>'
email_to = globals.mail_suporte  # 'eunice.borges@openk.com.br'
email_copy = globals.mail_copias  # 'ernane.crato@openk.com.br'


def enviar(mensagem, assunto):
    if smtp_port == 465:
        send_ssl(mensagem)
    else:
        send_tls(mensagem, assunto)


def send_ssl(message):
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
                smtp_server, smtp_port, context=context) as server:
            server.login(smtp_admin, smtp_password)
            server.sendmail(email_from, email_to, message)
    except Exception as e:
        logger.error(str(e), exc_info=True)
        traceback.print_exc()
    finally:
        server.quit()


def send_tls(message, assunto):
    texto = 'Atenção! ocorreu o erro abaixo: \n\n{}'.format(message)

    msg = EmailMessage()
    msg['Subject'] = assunto + ' da '
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Cc'] = email_copy
    msg.set_content(texto)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            # server.ehlo()
            server.starttls()
            # server.ehlo()
            server.login(smtp_admin, smtp_password)
            server.send_message(msg)
            server.quit()
    except Exception as e:
        logger.error(str(e), exc_info=True)
        traceback.print_exc()
    # finally:
        # server.quit()
