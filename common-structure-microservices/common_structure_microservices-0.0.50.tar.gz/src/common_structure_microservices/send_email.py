import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from common_structure_microservices import exception
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


def _get_data_image(file, base_dir, path, data=None):
    if data is None:
        path_template = f"{Path(path)}{os.sep}"
        path_file = base_dir + path_template + file[0] + '.' + file[1]
        data = open(path_file, 'rb').read()

    return {
        'name': file[0],
        'extension': file[1],
        'data': data
    }


def _attach_content_email(subject, file_type, user=None, files=None, html_content=None):
    html_part = MIMEMultipart(_subtype='related')
    html_part.attach(MIMEText(html_content, _subtype='html'))
    html_part['Subject'] = subject

    if files is None:
        files = []

    for file in files:
        if file_type == 'pdf':
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file['data'])
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= Hoja de vida - {user}.pdf",
            )
            html_part.attach(part)

        elif file_type == 'img':
            part = MIMEImage(file['data'], file['extension'])
            part.add_header('Content-Id', f"<{file['name']}>")
            part.add_header("Content-Disposition", "inline", filename=file['name'])
            html_part.attach(part)

    return html_part


def send_email(file, send_to_list, subject, file_type=None, user=None, files=None, context=None):
    kwargs = {
        'subject': subject,
        'body': None,
        'to': send_to_list
    }
    email = EmailMessage(**kwargs)

    if files is None:
        files = []

    html_content = render_to_string(file, context=context)
    html_attachment = _attach_content_email(subject=subject, user=user, files=files, html_content=html_content,
                                            file_type=file_type)
    email.attach(html_attachment)

    try:
        email.send()
    except smtplib.SMTPException:
        raise exception.SendEmailError
