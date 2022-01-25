import os
from os.path import basename
import traceback
import email
import imaplib
import smtplib
import pandas as pd
import pytz
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timedelta

SPECIAL_CHARS_MAP = {"\\": "", "/": "", ":": "", "*": "", "?": "", "<": "", ">": "", "|": "", "=": "", "\n": "", "\r": ""}


class EmailTool:
    """ Tooling to handle emails """

    def __init__(self, email_user, email_password):
        """ Initialize the class
		:param email_user: Email address from where download attachments
		:param email_password: Email password for the address indicated above
		"""

        self.from_ = email_user
        self.pass_ = email_password
        self.mailserver = None

    def open_write_email(self):
        self.mailserver = smtplib.SMTP('smtp.office365.com', 587)
        self.mailserver.ehlo()
        self.mailserver.starttls()
        self.mailserver.login(self.from_, self.pass_)

    def close_write_email(self):
        self.mailserver.quit()

    def open_read_email(self):
        self.mailserver = imaplib.IMAP4_SSL("outlook.office365.com", 993)
        self.mailserver.login(self.from_, self.pass_)

    def close_read_email(self):
        self.mailserver.logout()

    def send_email(self, subject, body, recipient, hidden_recipient=None, attachment=None, image_to_embed=''):
        """ Send an email with attachment if required
		:param subject: Email subject
		:param body: Email body or message
		:param recipient: Email address to whom the email will be sent
		:param hidden_recipient: Email address for the hidden recipients
		:param attachment: File to attach if required
		:param image_to_embed: Path to the image to be embedded in the email body
		:return: Send an email to the specified address
		"""
        try:

            if isinstance(recipient, list) is False:
                recipient = [recipient]

            self.open_write_email()

            if image_to_embed != '':
                msg = MIMEMultipart('related')
                msg.preamble = 'This is a multi-part message in MIME format.'
                msg_alternative = MIMEMultipart('mixed')
                msg.attach(msg_alternative)
                msg_text = MIMEText(body + '<br><br><img src="cid:image1"><br>', 'html')
                msg_alternative.attach(msg_text)

                fp = open(image_to_embed, 'rb')
                msg_image = MIMEImage(fp.read())
                fp.close()

                msg_image.add_header('Content-ID', '<image1>')
                msg.attach(msg_image)

            else:
                msg = MIMEMultipart('mixed')
                part = MIMEText(body, 'html')
                msg.attach(part)

            msg['Subject'] = subject
            msg['From'] = self.from_
            msg['To'] = ', '.join(recipient)
            to_ = recipient

            if hidden_recipient is not None:
                if isinstance(hidden_recipient, list) is False:
                    hidden_recipient = [hidden_recipient]
                msg['BCC'] = ', '.join(hidden_recipient)
                to_ = recipient + hidden_recipient

            if attachment is not None:
                if isinstance(attachment, list) is False:
                    attachment = [attachment]
                for f in attachment or []:
                    with open(f, "rb") as fil:
                        part = MIMEApplication(fil.read(), Name=basename(f))
                    # After the file is closed
                    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                    msg.attach(part)

            self.mailserver.sendmail(self.from_, to_, msg.as_string())

        except Exception:
            print(traceback.format_exc())
            raise Exception("An unknown error have happened")

        finally:
            self.close_write_email()

    @staticmethod
    def download_file(email_message, extension_files, detach_dir, encode=True):
        """ Download files from email
		:param email_message: Decoded email from string as: email_message = email.message_from_string(raw_email)
		:param extension_files: Indicate the extension of the attachments to download
		:param detach_dir: Indicate the directory in which the attachment will be stored
		:param encode: Indicates whether we need to encode('utf-8') or not
		:return: Send an email to the specified address
		"""
        try:
            attachment = []
            for part in email_message.walk():
                if (part.get_content_maintype() == 'multipart') | (part.get('Content-Disposition') is None):
                    attachment.append('')
                    continue
                attach_name = part.get_filename()
                if len(extension_files) > 0:
                    if not isinstance(extension_files, list):
                        extension_files = [extension_files]
                    if any([ext in attach_name for ext in extension_files]):
                        attachment_name = part.get_filename()
                        attachment_name = ''.join([SPECIAL_CHARS_MAP.get(i, i) for i in attachment_name])
                        attachment.append(attachment_name)
                        att_path = os.path.join(detach_dir, attachment_name).encode('utf-8')
                        if not os.path.isfile(att_path):
                            fp = open(att_path, 'wb')
                            fp.write(part.get_payload(decode=True))
                            fp.close()
                        print('Downloaded file:', attachment_name)
                else:
                    attachment_name = part.get_filename()
                    attachment_name = ''.join([SPECIAL_CHARS_MAP.get(i, i) for i in attachment_name])
                    attachment.append(attachment_name)
                    if encode:
                        att_path = os.path.join(detach_dir, attachment_name).encode('utf-8')
                    else:
                        att_path = os.path.join(detach_dir, attachment_name)
                    if not os.path.isfile(att_path):
                        fp = open(att_path, 'wb')
                        fp.write(part.get_payload(decode=True))
                        fp.close()
                    print('Downloaded file:', attachment_name)
            return attachment
        except Exception:
            print(traceback.format_exc())
            raise Exception("This method is used within retrieve_emails")

    def retrieve_emails(self, unseen=True, folder='Inbox', emails_to_query=10, remove_sender=None, download_type=None,
                        download_type_arg=None, extension_files=None, detach_dir='./', encode=True):
        """ Retrieve some information about the emails and store it in a DataFrame. It also download its attachments
		if required
		:param unseen: Indicate whether to query unseen emails (True) or all the emails (False)
		:param folder: Email folder from where the emails are to be retrieved
		:param emails_to_query: Number of emails to be queried when the method is called
		:param remove_sender: List of senders to avoid
		:param download_type: Indicate the download type to retrieve the emails:
			- None: No attachments will be downloaded.
			- "all": Retrieve all the emails and their attachments; i.e., emails_to_query number of emails.
			- "latest": Retrieve the last received email and its attachments.
			- "time": Retrieve the email received at download_type_arg and its attachments.
		:param download_type_arg: Indicate the datetime in which the email was sent when download_type = 'time'
		:param extension_files: List of the extension of the files to download
		:param detach_dir: Directory in which the attachments are to be saved (by default it saves them in the root of
		the project)
		:param encode: Indicates whether we try encode('utf-8') during file download
		:return: DataFrame containing the queried emails
		"""
        try:
            self.open_read_email()

            # Check download_type if applicable
            download_files = False
            if download_type in ['all', 'latest', 'time']:
                download_files = True
                if download_type == 'latest':
                    emails_to_query = 1
                elif download_type == 'time':
                    if (download_type_arg is None) | (not isinstance(download_type_arg, datetime)):
                        raise TypeError("Please specify a datetime value for 'download_type_arg'.")

            # Check if there are forbidden extensions
            if extension_files is None:
                extension_files = []
            elif not isinstance(extension_files, list):
                extension_files = [extension_files]

            # Check if remove_sender is a list
            if remove_sender is None:
                remove_sender = []
            elif not isinstance(remove_sender, list):
                remove_sender = [remove_sender]

            if self.mailserver.select(folder, readonly=False)[0] == 'NO':
                raise ValueError("The folder name '%s' doesn't exist. Please specify a valid folder name." % folder)

            try:
                if unseen:
                    result, data = self.mailserver.uid('search', None, '(UNSEEN)')
                else:
                    result, data = self.mailserver.uid('search', None, 'ALL')
                inbox_item_list = data[0].split()
                emails_uid = inbox_item_list[-emails_to_query:]
                emails_df = pd.DataFrame()

                for uid in emails_uid:
                    result2, email_data = self.mailserver.uid('fetch', uid, '(RFC822)')
                    raw_email = email_data[0][1].decode("UTF-8")
                    email_message = email.message_from_string(raw_email)
                    sender = email_message['From'].replace('<', '').replace('>', '')

                    if all([sender.upper() not in send.upper() for send in remove_sender]):
                        subject = email_message['Subject']
                        received_str = email_message['Date']
                        try:
                            received = pd.to_datetime(received_str, format='%d %b %Y %H:%M:%S %z').astimezone(pytz.utc).replace(tzinfo=None)
                        except:
                            received = pd.to_datetime(received_str, format='%a, %d %b %Y %H:%M:%S %z').astimezone(pytz.utc).replace(tzinfo=None)

                        sign = received_str[-5:-4]
                        tz = pd.to_datetime(received_str[-4:], format='%H%M').hour
                        if sign == '+':
                            received -= timedelta(hours=tz)
                        if sign == '-':
                            received += timedelta(hours=tz)

                        body = ''
                        body_message = email.message_from_string(raw_email)
                        if body_message.is_multipart():
                            for payload in body_message.get_payload():
                                body = payload.get_payload()
                        else:
                            body = body_message.get_payload()

                        email_df = pd.DataFrame(
                            {'Sender': [sender], 'Subject': [subject], 'Body': [body], 'Received': [received]})

                        if download_files:
                            aux_df = pd.DataFrame()
                            if (not (download_type == 'time')) | (
                                    (download_type_arg == received) & (download_type == 'time')):
                                attachment_name = self.download_file(email_message, extension_files, detach_dir, encode)
                                for dummy_ind in range(len(attachment_name)):
                                    aux_df = aux_df.append(email_df)
                                aux_df['AttachmentName'] = attachment_name

                            email_df = aux_df

                        emails_df = emails_df.append(email_df)

            except IndexError:
                raise IndexError("No emails to retrieve")

        except Exception:
            print(traceback.format_exc())
            raise Exception("An unknown error have happened")

        finally:
            self.close_read_email()

        if 'AttachmentName' in emails_df.columns:
            emails_df = emails_df.loc[emails_df['AttachmentName'] != '']

        return emails_df.drop_duplicates().reset_index(drop=True)
