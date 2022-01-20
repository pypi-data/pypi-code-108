from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name):
        # Si el nombre del archivo existe, remove it as if it was a true file system
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

def send_mail_orden(host,port,mail,password,destinatarios, asunto, mensaje, archivo,nombre):
	if mail and port and host and password:
		try:
			msg = MIMEMultipart()
			message = mensaje
			if archivo:
				fo=open(archivo,'rb')
				pdfAttachment = MIMEApplication(fo.read(),_subtype="pdf")
				fo.close()
				pdfAttachment.add_header('Content-Disposition','attachment',filename=nombre)
				msg.attach(pdfAttachment)

			msg.attach(MIMEText(mensaje, 'html', _charset="UTF-8"))	
			password = password
			msg['Subject'] = asunto
			
			server = smtplib.SMTP(host, int(port))
			server.ehlo()
			server.starttls()
			server.login(mail, password)

			server.sendmail(mail, destinatarios ,msg.as_string())
			server.quit()
			
			return True
		except Exception as e:
			print(e)
			return False


	
  