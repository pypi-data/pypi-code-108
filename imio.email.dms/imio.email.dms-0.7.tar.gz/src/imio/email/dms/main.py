# -*- coding: utf-8 -*-

"""
Usage: process_mails FILE [--requeue_errors] [--list_emails=<number>] [--get_eml=<mail_id>]  [--gen_pdf=<mail_id>]
                          [--get_eml_orig] [--stats]

Arguments:
    FILE         config file

Options:
    -h --help               Show this screen.
    --requeue_errors        Put email in error status back in waiting for processing.
    --list_emails=<number>  List last xx emails.
    --get_eml=<mail_id>     Get eml of original/contained email id.
    --get_eml_orig          Get eml of original email id (otherwise contained).
    --gen_pdf=<mail_id>     Generate pdf of contained email id.
    --stats                 Get email stats following stats
"""
from datetime import datetime
from datetime import timedelta
from docopt import docopt
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from hashlib import md5
from imio.email.dms.imap import IMAPEmailHandler
from imio.email.dms.imap import MailData
from imio.email.dms.utils import safe_unicode
from imio.email.parser.parser import Parser  # noqa
from io import BytesIO
from smtplib import SMTP
import configparser
import imaplib
import json
import logging
import os
import re
import requests
import six
import sys
import tarfile
import zc.lockfile
from imio.email.dms.utils import save_as_eml

try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

logger = logging.getLogger("imio.email.dms")
logger.setLevel(logging.INFO)
chandler = logging.StreamHandler()
chandler.setLevel(logging.INFO)
logger.addHandler(chandler)


ERROR_MAIL = u"""
Problematic mail is attached.\n
Client ID : {0}
IMAP login : {1}\n
mail id : {2}\n
Corresponding exception : {3}
{4}\n
"""

UNSUPPORTED_ORIGIN_EMAIL = u"""
Dear user,

The attached email has been refused because it wasn't sent to us as an attachment.\n
\n
Please try again, by following one of these methods.\n
\n
If you are using Microsoft Outlook:\n
- In the ribbon, click on the More dropdown button next to the standard Forward button\n
- Choose Forward as Attachment\n
- Send the opened draft to the GED import address.\n
\n
If you are using Mozilla Thunderbird:\n
- Open the email you want to import into the GED.\n
- Click on the menu Message > Forward As > Attachment.\n
- Send the opened draft to the GED import address.\n
\n
Please excuse us for the inconvenience.\n
"""

UNSUPPORTED_ORIGIN_EMAIL = u"""
Cher utilisateur d'iA.Docs,

Le transfert de l'email attaché a été rejeté car il n'a pas été transféré correctement.\n
Veuillez refaire le transfert du mail original en transférant "en tant que pièce jointe".\n
Si vous utilisez Microsoft Outlook:\n
- Dans le ruban, cliquez sur la flèche du ménu déroulant située sur le bouton de transfert\n
- Choisissez le transfert en tant que pièce jointe\n
- Envoyez le mail sans rien compléter d'autre à l'adresse prévue pour iA.Docs.\n
\n
Si vous utilisez Mozilla Thunderbird:\n
- Faites un clic droit sur l'email pour ouvrir le menu contextuel\n
- Sélectionnez "Transférer au format" > "Pièce jointe".\n
- Envoyez le mail sans rien compléter d'autre à l'adresse prévue pour iA.Docs.\n
\n
Cordialement.\n
"""

IGNORED_MAIL = u"""
Bonjour,
Votre adresse email {3} n'est pas autorisée à transférer un email vers iA.docs.
Si cette action est justifiée, veuillez prendre contact avec votre référent interne.\n
Le mail concerné est en pièce jointe.\n
Client ID : {0}
IMAP login : {1}
mail id : {2}
pattern : "{4}"
"""

RESULT_MAIL = u"""
Client ID : {0}
IMAP login : {1}\n
{2}\n
"""


class DmsMetadataError(Exception):
    """ The response from the webservice dms_metadata route is not successful """


class FileUploadError(Exception):
    """ The response from the webservice file_upload route is not successful """


def notify_exception(config, mail_id, mail, error):
    client_id = config["webservice"]["client_id"]
    login = config["mailbox"]["login"]
    smtp_infos = config["smtp"]
    sender = smtp_infos["sender"]
    recipient = smtp_infos["recipient"]

    msg = MIMEMultipart()
    msg["Subject"] = "Error handling an email for client {}".format(client_id)
    msg["From"] = sender
    msg["To"] = recipient

    error_msg = error
    if hasattr(error, 'message'):
        error_msg = safe_unicode(error.message)
    elif hasattr(error, 'reason'):
        try:
            error_msg = u"'{}', {}, {}, {}".format(error.reason, error.start, error.end, error.object)
        except Exception:
            error_msg = error.reason
    main_text = MIMEText(ERROR_MAIL.format(client_id, login, mail_id, error.__class__, error_msg), "plain")
    msg.attach(main_text)

    attachment = MIMEBase("message", "rfc822")
    attachment.set_payload(mail.as_string())
    attachment.add_header("Content-Disposition", "inline")
    msg.attach(attachment)

    smtp = SMTP(str(smtp_infos["host"]), int(smtp_infos["port"]))
    msg_content = msg.as_string().encode("utf8") if six.PY3 else msg.as_string()
    smtp.sendmail(sender, recipient, msg_content)
    smtp.quit()


def notify_unsupported_origin(config, mail, from_):
    smtp_infos = config["smtp"]
    sender = smtp_infos["sender"]

    msg = MIMEMultipart()
    msg["Subject"] = "Error importing email into iA.docs"
    msg["Subject"] = "Erreur de transfert de votre email dans iA.Docs"
    msg["From"] = sender
    msg["To"] = from_

    main_text = MIMEText(UNSUPPORTED_ORIGIN_EMAIL, "plain")
    msg.attach(main_text)

    attachment = MIMEBase("message", "rfc822")
    attachment.set_payload(mail.as_string())
    attachment.add_header("Content-Disposition", "inline")
    msg.attach(attachment)

    smtp = SMTP(str(smtp_infos["host"]), int(smtp_infos["port"]))
    msg_content = msg.as_string().encode("utf8") if six.PY3 else msg.as_string()
    smtp.sendmail(sender, from_, msg_content)
    smtp.quit()


def notify_ignored(config, mail_id, mail, from_):
    client_id = config["webservice"]["client_id"]
    login = config["mailbox"]["login"]
    smtp_infos = config["smtp"]
    sender = smtp_infos["sender"]
    recipient = smtp_infos["recipient"]

    msg = MIMEMultipart()
    msg["Subject"] = "Transfert non autorisé de {} pour le client {}".format(from_, client_id)
    msg["From"] = sender
    msg["To"] = from_
    msg["Bcc"] = recipient

    main_text = MIMEText(IGNORED_MAIL.format(client_id, login, mail_id, from_, config['mailinfos']['sender-pattern']),
                         "plain")
    msg.attach(main_text)

    attachment = MIMEBase("message", "rfc822")
    attachment.set_payload(mail.as_string())
    attachment.add_header("Content-Disposition", "inline")
    msg.attach(attachment)

    smtp = SMTP(str(smtp_infos["host"]), int(smtp_infos["port"]))
    msg_content = msg.as_string().encode("utf8") if six.PY3 else msg.as_string()
    smtp.sendmail(sender, recipient, msg_content)
    smtp.quit()


def notify_result(config, subject, message):
    client_id = config["webservice"]["client_id"]
    login = config["mailbox"]["login"]
    smtp_infos = config["smtp"]
    sender = smtp_infos["sender"]
    recipient = smtp_infos["recipient"]

    msg = MIMEMultipart()
    msg["Subject"] = "{} for client {}".format(subject, client_id)
    msg["From"] = sender
    msg["To"] = recipient

    main_text = MIMEText(RESULT_MAIL.format(client_id, login, message), "plain")
    msg.attach(main_text)

    smtp = SMTP(str(smtp_infos["host"]), int(smtp_infos["port"]))
    msg_content = msg.as_string().encode("utf8") if six.PY3 else msg.as_string()
    smtp.sendmail(sender, recipient, msg_content)
    smtp.quit()


def check_transferer(sender, pattern):
    if re.match(pattern, sender, re.I):
        return True
    return False


def get_mailbox_infos(config):
    mailbox_infos = config["mailbox"]
    host = str(mailbox_infos["host"])
    port = int(mailbox_infos["port"])
    ssl = mailbox_infos["ssl"] == "true" and True or False
    login = mailbox_infos["login"]
    password = mailbox_infos["pass"]
    return host, port, ssl, login, password


def get_preview_pdf_path(config, mail_id):
    mail_infos = config["mailinfos"]
    output_dir = mail_infos["pdf-output-dir"]
    filename = "{0}.pdf".format(mail_id.decode("UTF-8"))
    return os.path.join(output_dir, filename)


def send_to_ws(config, headers, main_file_path, attachments, mail_id):
    ws = config["webservice"]
    client_id = "{0}Z{1}".format(ws['client_id'][:2], ws['client_id'][-4:])
    counter_dir = Path(ws['counter_dir'])
    next_id_path = counter_dir / client_id
    if next_id_path.exists() and next_id_path.read_text():
        next_id = int(next_id_path.read_text()) + 1
    else:
        next_id = 1
    external_id = "{0}{1:08d}".format(client_id, next_id)

    tar_path = Path('/tmp') / '{}.tar'.format(external_id)
    with tarfile.open(str(tar_path), "w") as tar:
        # 1) email pdf printout or eml file
        mf_contents = Path(main_file_path).open('rb').read()
        basename, ext = os.path.splitext(main_file_path)
        mf_info = tarfile.TarInfo(name='email{}'.format(ext))
        mf_info.size = len(mf_contents)
        tar.addfile(tarinfo=mf_info, fileobj=BytesIO(mf_contents))

        # 2) metadata.json
        metadata_contents = json.dumps(headers).encode("utf8") if six.PY3 else json.dumps(headers)
        metadata_info = tarfile.TarInfo(name='metadata.json')
        metadata_info.size = len(metadata_contents)
        tar.addfile(tarinfo=metadata_info, fileobj=BytesIO(metadata_contents))

        # 3) every attachment file
        for attachment in attachments:
            attachment_contents = attachment['content']
            attachment_info = tarfile.TarInfo(name='/attachments/{}'.format(attachment['filename']))
            attachment_info.size = len(attachment_contents)
            tar.addfile(tarinfo=attachment_info, fileobj=BytesIO(attachment_contents))

    tar_content = tar_path.read_bytes()
    now = datetime.now()
    metadata = {
        "external_id": external_id,
        "client_id": client_id,
        "scan_date": now.strftime("%Y-%m-%d"),
        "scan_hour": now.strftime("%H:%M:%S"),
        "user": "testuser",
        "pc": "pc-scan01",
        "creator": "scanner",
        "filesize": len(tar_content),
        "filename": tar_path.name,
        "filemd5": md5(tar_content).hexdigest(),
    }

    auth = (ws['login'], ws['pass'])
    proto = ws['port'] == '443' and 'https' or 'http'
    metadata_url = '{proto}://{ws[host]}:{ws[port]}/dms_metadata/{client_id}/{ws[version]}'.format(
        proto=proto,
        ws=ws,
        client_id=client_id,
    )
    metadata_req = requests.post(metadata_url, auth=auth, json=metadata)
    req_content = json.loads(metadata_req.content)
    if not req_content['success'] or 'id' not in req_content:
        msg = u"mail_id: {}, code: '{}', error: '{}', metadata: '{}'".format(mail_id, req_content['error_code'],
                                                                             req_content['error'],
                                                                             metadata).encode('utf8')
        raise DmsMetadataError(msg)
    response_id = req_content['id']

    upload_url = '{proto}://{ws[host]}:{ws[port]}/file_upload/{ws[version]}/{id}'.format(proto=proto, ws=ws,
                                                                                         id=response_id)
    files = {'filedata': ('archive.tar', tar_content, 'application/tar', {'Expires': '0'})}
    upload_req = requests.post(upload_url, auth=auth, files=files)
    req_content = json.loads(upload_req.content)
    if not req_content['success']:
        msg = u"mail_id: {}, code: '{}', error: '{}'".format(mail_id, req_content['error_code'],
                                                             req_content.get('error') or
                                                             req_content['message']).encode('utf8')
        raise FileUploadError(msg)

    next_id_txt = str(next_id) if six.PY3 else str(next_id).decode()
    next_id_path.write_text(next_id_txt)


def process_mails():
    arguments = docopt(__doc__)
    config = configparser.ConfigParser()
    config_file = arguments["FILE"]
    config.read(config_file)

    host, port, ssl, login, password = get_mailbox_infos(config)
    counter_dir = Path(config["webservice"]["counter_dir"])
    counter_dir.mkdir(exist_ok=True)
    lock_filepath = counter_dir / "lock_{0}".format(config['webservice']['client_id'])
    lock = zc.lockfile.LockFile(lock_filepath.as_posix())

    handler = IMAPEmailHandler()
    handler.connect(host, port, ssl, login, password)

    if arguments.get("--requeue_errors"):
        amount = handler.reset_errors()
        logger.info("{} emails in error were put back in waiting state".format(amount))
        handler.disconnect()
        lock.close()
        sys.exit()
    elif arguments.get("--list_emails"):
        handler.list_last_emails(nb=int(arguments.get("--list_emails")))
        # import ipdb; ipdb.set_trace()
        # handler.mark_reset_error('58')
        # handler.mark_reset_ignored('77')
        # res, data = handler.connection.search(None, 'SUBJECT "JBC client"')
        # for mail_id in data[0].split():
        #      mail = handler.get_mail(mail_id)
        #      mail_infos = MailData(mail_id, mail)
        #      email = mail_infos.mail
        #     logger.info(email['Subject'])
        handler.disconnect()
        lock.close()
        sys.exit()
    elif arguments.get("--get_eml"):
        mail_id = arguments['--get_eml']
        if not mail_id:
            logger.error('Error: you must give an email id (--get_eml=25 by example)')
        mail = handler.get_mail(mail_id)
        parsed = Parser(mail)
        logger.info(parsed.headers)
        message = parsed.message
        filename = '{}.eml'.format(mail_id)
        if arguments.get('--get_eml_orig'):
            message = parsed.initial_message
            filename = '{}_o.eml'.format(mail_id)
        logger.info('Writing {} file'.format(filename))
        save_as_eml(filename, message)
        handler.disconnect()
        lock.close()
        sys.exit()
    elif arguments.get("--gen_pdf"):
        mail_id = arguments['--gen_pdf']
        if not mail_id:
            logger.error('Error: you must give an email id (--gen_pdf=25 by example)')
        mail = handler.get_mail(mail_id)
        parsed = Parser(mail)
        logger.info(parsed.headers)
        pdf_path = get_preview_pdf_path(config, mail_id.encode('utf8'))
        logger.info('Generating {} file'.format(pdf_path))
        parsed.generate_pdf(pdf_path)
        handler.disconnect()
        lock.close()
        sys.exit()
    elif arguments.get("--stats"):
        logger.info('Started at {}'.format(datetime.now()))
        stats = handler.stats()
        logger.info("Total mails: {}".format(stats.pop('tot')))
        for flag in sorted(stats['flags']):
            logger.info("Flag '{}' => {}".format(flag, stats['flags'][flag]))
        handler.disconnect()
        lock.close()
        logger.info('Ended at {}'.format(datetime.now()))
        sys.exit()

    imported = errors = unsupported = ignored = 0
    # import ipdb; ipdb.set_trace()
    for mail_info in handler.get_waiting_emails():
        mail_id = mail_info.id
        mail = mail_info.mail
        main_file_path = get_preview_pdf_path(config, mail_id)
        try:
            parser = Parser(mail)
            if parser.origin == 'Generic inbox':
                mail_sender = parser.headers["From"][0][1]
                notify_unsupported_origin(config, mail, mail_sender)
                handler.mark_mail_as_unsupported(mail_id)
                unsupported += 1
                continue
            headers = parser.headers
            # we check if the pushing agent has a permitted email format
            if not check_transferer(headers['Agent'][0][1], config['mailinfos'].get('sender-pattern', '.+')):
                handler.mark_mail_as_ignored(mail_id)
                notify_ignored(config, mail_id, mail, headers['Agent'][0][1])
                # logger.error('Rejecting {}: {}'.format(headers['Agent'][0][1], headers['Subject']))
                ignored += 1
                continue
            # logger.info('Accepting {}: {}'.format(headers['Agent'][0][1], headers['Subject']))
            attachments = parser.attachments
            try:
                parser.generate_pdf(main_file_path)
            except Exception as pdf_exc:
                # if 'XDG_SESSION_TYPE=wayland' not in str(pdf_exc):
                main_file_path = main_file_path.replace('.pdf', '.eml')
                save_as_eml(main_file_path, parser.message)
            send_to_ws(config, headers, main_file_path, attachments, mail_id)
            handler.mark_mail_as_imported(mail_id)
            imported += 1
        except Exception as e:
            logger.error(e, exc_info=True)
            notify_exception(config, mail_id, mail, e)
            handler.mark_mail_as_error(mail_id)
            errors += 1

    logger.info("{} emails have been imported. {} emails are unsupported. {} emails have caused an error. {} emails "
                "are ignored".format(imported, unsupported, errors, ignored))
    handler.disconnect()
    lock.close()


def clean_mails():
    """Clean mails from imap box.

    Usage: clean_mails FILE [-h] [--kept_days=<number>] [--ignored_too] [--list_only]

    Arguments:
        FILE         config file

    Options:
        -h --help               Show this screen.
        --kept_days=<number>    Days to keep [default: 30]
        --ignored_too           Get also not imported emails
        --list_only             Only list related emails, do not delete
    """
    arguments = docopt(clean_mails.__doc__)
    config = configparser.ConfigParser()
    config.read(arguments["FILE"])
    days = int(arguments["--kept_days"])
    doit = not arguments["--list_only"]
    host, port, ssl, login, password = get_mailbox_infos(config)
    handler = IMAPEmailHandler()
    handler.connect(host, port, ssl, login, password)
    before_date = (datetime.now() - timedelta(days)).strftime("%d-%b-%Y")  # date string 01-Jan-2021
    # before_date = '01-Jun-2021'
    res, data = handler.connection.search(None, '(BEFORE {0})'.format(before_date))
    if res != "OK":
        logger.error("Unable to fetch mails before '{}'".format(before_date))
        handler.disconnect()
        sys.exit()
    deleted = ignored = error = 0
    mail_ids = data[0].split()
    mail_ids_len = len(mail_ids)
    out = [u"Get '{}' emails older than '{}'".format(mail_ids_len, before_date)]
    logger.info("Get '{}' emails older than '{}'".format(mail_ids_len, before_date))
    # sys.exit()
    for mail_id in mail_ids:
        res, flags_data = handler.connection.fetch(mail_id, '(FLAGS)')
        if res != "OK":
            logger.error("Unable to fetch flags for mail {0}".format(mail_id))
            error += 1
            continue
        flags = imaplib.ParseFlags(flags_data[0])
        if not arguments["--ignored_too"] and b"imported" not in flags:
            ignored += 1
            continue
        mail = handler.get_mail(mail_id)
        if not mail:
            error += 1
            continue
        parser = Parser(mail)
        logger.info(u"{}: '{}'".format(mail_id, parser.headers['Subject']))
        out.append(u"{}: '{}'".format(mail_id, parser.headers['Subject']))
        if doit:
            handler.connection.store(mail_id, "+FLAGS", "\\Deleted")
        deleted += 1
    if deleted:
        logger.info("Get '{}' emails older than '{}'".format(mail_ids_len, before_date))
        if doit:
            res, data = handler.connection.expunge()
            if res != "OK":
                out.append(u"ERROR: Unable to deleted mails !!")
                logger.error("Unable to deleted mails")
    handler.disconnect()
    out.append(u"{} emails have been deleted. {} emails are ignored. {} emails have caused an error.".format(
               deleted, ignored, error))
    logger.info("{} emails have been deleted. {} emails are ignored. {} emails have caused an error.".format(
                deleted, ignored, error))
    notify_result(config, 'Result of clean_mails', u'\n'.join(out))
