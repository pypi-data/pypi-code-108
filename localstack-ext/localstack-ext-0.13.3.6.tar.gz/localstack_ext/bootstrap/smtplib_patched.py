import base64
sgQbC=None
import hmac
import smtplib
from base64 import b64encode
from smtplib import SMTPAuthenticationError,SMTPException
from localstack.utils.common import to_bytes,to_str
def base64_encode(s):
 result=to_str(b64encode(to_bytes(s))).strip()
 return result
class SMTP(smtplib.SMTP):
 def login(self,user,password):
  def encode_cram_md5(challenge,user,password):
   challenge=base64.decodestring(challenge)
   response=user+" "+hmac.HMAC(password,challenge).hexdigest()
   return base64_encode(response)
  def encode_plain(user,password):
   return base64_encode("\0%s\0%s"%(user,password))
  AUTH_PLAIN="PLAIN"
  AUTH_CRAM_MD5="CRAM-MD5"
  AUTH_LOGIN="LOGIN"
  self.ehlo_or_helo_if_needed()
  if not self.has_extn("auth"):
   raise SMTPException("SMTP AUTH extension not supported by server.")
  authlist=self.esmtp_features["auth"].split()
  preferred_auths=[AUTH_CRAM_MD5,AUTH_PLAIN,AUTH_LOGIN]
  authmethod=sgQbC
  for method in preferred_auths:
   if method in authlist:
    authmethod=method
    break
  if authmethod==AUTH_CRAM_MD5:
   tmp=self.docmd("AUTH",AUTH_CRAM_MD5)
   code=tmp[0]
   resp=tmp[1]
   if code==503:
    return(code,resp)
   tmp=self.docmd(encode_cram_md5(resp,user,password))
   code=tmp[0]
   resp=tmp[1]
  elif authmethod==AUTH_PLAIN:
   tmp=self.docmd("AUTH",AUTH_PLAIN+" "+encode_plain(user,password))
   code=tmp[0]
   resp=tmp[1]
  elif authmethod==AUTH_LOGIN:
   encoded_username=base64_encode(user)
   encoded_password=base64_encode(password)
   tmp=self.check_codes(encoded_username,encoded_password)
   code=tmp[0]
   resp=tmp[1]
  elif authmethod is sgQbC:
   raise SMTPException("No suitable authentication method found.")
  if code not in(235,503):
   raise SMTPAuthenticationError(code,resp)
  return(code,resp)
 def check_codes(self,encoded_username,encoded_password):
  AUTH_LOGIN="LOGIN"
  tmp=self.docmd("AUTH",AUTH_LOGIN)
  code=tmp[0]
  resp=tmp[1]
  if code!=334:
   raise SMTPAuthenticationError(code,resp)
  tmp=self.docmd(encoded_username)
  code=tmp[0]
  resp=tmp[1]
  if code!=334:
   raise SMTPAuthenticationError(code,resp)
  tmp=self.docmd(encoded_password)
  code=tmp[0]
  resp=tmp[1]
  if code!=235:
   raise SMTPAuthenticationError(code,resp)
  return code,resp
# Created by pyminifier (https://github.com/liftoff/pyminifier)
