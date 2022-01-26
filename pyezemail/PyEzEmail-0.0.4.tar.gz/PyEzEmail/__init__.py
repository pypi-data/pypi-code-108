from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from os.path import basename
from smtplib import SMTP


class SmtpConfig:
    """
        Esta clase crea un objeto con la configuracion SMTP necesaria para el envio de correos en la clase Email

        |

        ATRIBUTOS (**kwargs)
        ----
        username: str
            Direccion del correo de envio
        password : str
            Password del correo de envio
        host : str
            Host del correo de envio
        port : int
            Puerto del host a conectar

        |

        METODOS
        ----
        checkcfg() : None
            Chequeo de la configuracion (Este metodo se se ejecuta por defecto al crear el objeto)
    """

    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.host = kwargs['host']
        self.port = kwargs['port'] if 'port' in kwargs else 25
        self.checkcfg()

    def checkcfg(self):
        smtp_object = SMTP(self.host, port=self.port)
        smtp_object.ehlo()
        smtp_object.login(self.username, self.password)
        return True


class MailData:

    """
        Esta clase crea un objeto con todos los datos de envio utlizados por la clase Email

        |

        ATRIBUTOS (**kwargs)
        ----
        to : list
            Correo del destinatario
        cc : list
            Correo en copia
        bcc : list
            Correo en copia oculta
        subject : str
            Asunto del correo
        message : str
            Mensaje del correo en formato html
        attachments : list
            Lista de las rutas de los archivos a adjuntar
    """

    def __init__(self, **kwargs):
        self.to = kwargs['to']
        self.cc = kwargs['cc'] if 'cc' in kwargs else []
        self.bcc = kwargs['bcc'] if 'bcc' in kwargs else []
        self.subject = kwargs['subject']
        self.message = kwargs['message']
        self.attachments = kwargs['attachments'] if 'attachments' in kwargs else []


class Email:

    """
        Esta clase crea y envia un mail utilizando un objeto de configuracion (SmtpConfig) y
        un objeto de datos (MailData) ingresados como parametros cuando se crea.

        |

        PARAMETROS
        ----
        smtpcfg: SmtpConfig
            Configuracion smtp
        data: MailData
            Datos de envio

        |

        ATRIBUTOS
        ----
        username: str
            Direccion del correo de envio
        password : str
            Password del correo de envio
        host : str
            Host del correo de envio
        port : int
            Puerto del host a conectar
        to : str
            Correo del destinatario
        cc : str
            Correo en copia
        bcc : str
            Correo en copia oculta
        subject : str
            Asunto del correo
        message : str
            Mensaje del correo en formato html
        attachments : list
            Lista de las rutas de los archivos a adjuntar
        recipient_address: list
            Lista de todos los destinatarios

        |

        METODOS
        ----
        send() : None
            Envio del correo
    """

    def __init__(self, smtpcfg: SmtpConfig, data: MailData):
        self.mailing_address = smtpcfg.username
        self.password = smtpcfg.password
        self.host = smtpcfg.host
        self.port = smtpcfg.port
        self.to = ','.join(data.to)
        self.cc = ','.join(data.cc)
        self.bcc = ','.join(data.bcc)
        self.subject = data.subject
        self.message = data.message
        self.attachments = data.attachments
        self.recipient_address = data.to + data.cc + data.bcc

    def send(self):
        html_part = MIMEText(self.message, 'html')
        msg_alternative = MIMEMultipart('alternative')
        msg_alternative.attach(html_part)
        msg_mixed = MIMEMultipart('mixed')
        msg_mixed.attach(msg_alternative)
        msg_mixed['From'] = self.mailing_address
        msg_mixed['To'] = self.to
        msg_mixed['Cc'] = self.cc
        msg_mixed['Subject'] = self.subject
        msg_mixed['Date'] = formatdate(localtime=True)

        for attachment in self.attachments:
            file = open(attachment, 'rb')
            filename = basename(attachment)
            attachment = MIMEApplication(file.read())
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg_mixed.attach(attachment)
            file.close()

        smtp_object = SMTP(self.host, port=self.port)
        smtp_object.ehlo()
        smtp_object.login(self.mailing_address, self.password)
        smtp_object.sendmail(msg_mixed['From'], self.recipient_address, msg_mixed.as_string())
        smtp_object.quit()
