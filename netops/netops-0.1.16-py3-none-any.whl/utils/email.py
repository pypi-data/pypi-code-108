import smtplib
#import pytz

from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase
from email.header import Header
from email.utils import formataddr
from email import encoders
#from datetime import datetime


def send_email(sender_address, sender_pass, receivers, subject, message, attach_file_path=None):
    """ TODO: translate to English

    Envia email.
    
    Recebe:
            sender - endereco de email do remetente
            receivers - lista de email dos destinatarios
            subject - assunto da mensagem
            message - mensagem a ser enviada
            
    Retorna:
            email_date - data de envio do email"""
    # Instantiate MIMEMultipart 
    msg = MIMEMultipart() 
    
    # Stores sender email address    
    msg['From'] = formataddr((str(Header('PoP-RJ/RNP', 'utf-8')), sender_address))

    # Stores receivers email addresses
    msg['To'] = ", ".join(receivers)

    # Armazena o assunto  
    msg['Subject'] = subject
    
    # Attaches the email body to the message instance
    msg.attach(MIMEText(message, 'plain')) 

    if attach_file_path is not None:
        # Open the file to be sent
        attachment = open(attach_file_path, "rb")      
        # Instantiate do MIMEBase as p
        p = MIMEBase('application', 'octet-stream') 
        # Change payload as codified format
        p.set_payload((attachment).read()) 
        # Codifies payload in base64
        encoders.encode_base64(p) 
        # Adds the header to the attachment   
        p.add_header('Content-Disposition', "attachment; filename= %s" % attach_file_path) 
        # Adds the payload to the message
        msg.attach(p) 
    
    # Creates smtplib session
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    
    # Starts criptography of SMTP session through TLS protocol
    s.starttls() 
    
    # Auth email
    s.login(sender_address, sender_pass) 

    # Converts Multipart message into a string
    text = msg.as_string() 
    
    # Send the email
    s.sendmail(sender_address, receivers, text) 
    
    # Quit SMTP session
    s.quit()
    #sent_date = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%d/%m/%Y at %H:%M (BR time format)')
    
    # Acknowledge the e-mail sending
    receivers_str_addresses = (', '.join(['%s']*len(receivers)))%tuple(receivers)
    #print('Successfully sent email to %s in %s.' %(receivers_str_addresses, sent_date) )
    print("Successfully sent email of subject '%s' to %s." %(subject, receivers_str_addresses))

    return