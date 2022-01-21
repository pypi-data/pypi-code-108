import logging
pYlbq=set
pYlby=str
pYlbM=None
pYlbh=isinstance
pYlbK=list
pYlbg=Exception
import re
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from localstack.utils.common import now_utc
from localstack.utils.testutil import is_local_test_mode
from localstack_ext import config
from localstack_ext.bootstrap import smtplib_patched
LOG=logging.getLogger(__name__)
SENT_EMAILS=[]
EMAIL_BLACKLIST=pYlbq()
def is_smtp_configured():
 return config.SMTP_HOST
def get_canonical_email(email):
 email=re.sub(r"\s+","",pYlby(email or ""))
 email=email.strip().lower()
 return email
def send_email(subject,message,recipients,from_email=pYlbM,from_name=pYlbM,smtp_host=pYlbM,smtp_user=pYlbM,smtp_pass=pYlbM,images={}):
 smtp_host=smtp_host or config.SMTP_HOST
 smtp_user=smtp_user or config.SMTP_USER
 smtp_pass=smtp_pass or config.SMTP_PASS
 from_email=from_email or config.SMTP_EMAIL
 from_name=from_name or "LocalStack"
 if not smtp_host:
  if is_local_test_mode():
   entry={"time":now_utc(),"smtp_host":smtp_host,"smtp_user":smtp_user,"smtp_pass":smtp_pass,"from_email":from_email,"from_name":from_name,"subject":subject,"message":message,"recipients":recipients}
   SENT_EMAILS.append(entry)
   return
  LOG.debug('SMTP settings not configured, skip sending email to "%s"'%recipients)
  return
 recipients=recipients if pYlbh(recipients,pYlbK)else[recipients]
 message=construct_message(subject,message,from_name,from_email,images=images)
 sign_message(message)
 for recipient in recipients:
  if recipient in EMAIL_BLACKLIST:
   LOG.debug("Skip sending email to receiver in blacklist: %s"%recipient)
   continue
  LOG.debug("Sending email to %s"%recipient)
  message["To"]=recipient
  s=smtplib_patched.SMTP(smtp_host)
  try:
   s.starttls()
  except pYlbg as e:
   LOG.debug("Unable to run STARTTLS command on SMTP connection: %s"%e)
  if smtp_user and smtp_pass:
   try:
    s.login(smtp_user,smtp_pass)
   except pYlbg as e:
    LOG.debug("Unable to run login/auth command against SMTP server, skipping: %s"%e)
  s.sendmail(from_email,[recipient],message.as_string())
  s.quit()
def sign_message(msg):
 pass
def is_email_address(value):
 return re.match(r"[^@]+@[^@]+\.[^@]+",value or "")
def construct_message(subject,message,from_name,from_email,images=pYlbM):
 result=MIMEText(message)
 if images:
  result=MIMEMultipart("related")
  msg_alternative=MIMEMultipart("alternative")
  result.attach(msg_alternative)
  msg_plain=MIMEText(message)
  msg_alternative.attach(msg_plain)
  msg_html=MIMEText(message,"html")
  msg_alternative.attach(msg_html)
  for image_id,image_bytes in images.items():
   msg_image=MIMEImage(image_bytes)
   msg_image.add_header("Content-ID","<%s>"%image_id)
   result.attach(msg_image)
 result["Subject"]=subject
 result["From"]=formataddr((pYlby(Header(from_name,"utf-8")),from_email))
 return result
# Created by pyminifier (https://github.com/liftoff/pyminifier)
