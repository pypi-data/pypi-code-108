#!/usr/bin/env python3
"""
Module MAIL -- Email Utilities
Sub-Package STDLIB of Package PLIB3
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from email.message import Message
from email.utils import formatdate
import smtplib
import types


def readline(self, size=-1):
    if size < 0:
        size = None
    str = b""
    chr = None
    while chr != b"\n":
        if size is not None and len(str) > size:
            break
        chr = self.sslobj.read(1)
        if not chr:
            break
        str += chr
    return str


def fix_readline(smtp):
    # Hack to work around login bug in some Python 3 versions with SSL file object
    # (must be called after starttls so that smtp.file is an SSLFakeFile)
    if smtp.file.readline.__func__.__code__.co_argcount == 1:
        smtp.file.readline = types.MethodType(readline, smtp.file)


def sendmail(fromaddr, toaddr, subject, payload, headers=None,
             mimetype="text/plain", charset="us-ascii", msgdate=None,
             server='localhost', portnum=25, username=None, password=None,
             verbose=True):
    """Send an email.
    
    This is a simple utility function to allow programs
    to send simple emails without having to grovel into
    the depths of the python stdlib email package. It takes
    the following parameters, which should generally be in
    a format that complies with the email RFCs:
    
    - ``fromaddr`` - the "From" address
    
    - ``toaddr`` - a string containing a single "To" address,
      or a list of "To" addresses
    
    - ``subject`` - what goes in the "Subject" line
    
    - ``payload`` - the actual message.
    
    The above four parameters must always be supplied, as
    positional arguments. The rest of the parameters are
    optional, and can be supplied as keyword arguments (the
    preferred method):
    
    - ``headers`` - if present, a dictionary of header names and
      values; you should only use "X-" header names here (the
      Python email library fills in all the RFC standard headers
      for you, so you only need to worry about ones that are
      specific to your use case)
    
    - ``mimetype`` - the MIME type of the message; defaults to
      text/plain, and I would really like it if you *never*
      overrode that, since I'm highly allergic to HTML email :-)
    
    - ``charset`` - the character set of the message; defaults
      to us-ascii, since that's the easiest type to use for
      text/plain, but any charset that's compatible with the
      MIME type you're using will work
    
    - ``msgdate`` - the send date/time of the message; defaults
      to the current system date/time (you should only override
      this if you know your system clock is inaccurate or not
      configured properly)
    
    - ``server`` - the SMTP server to connect to; the default
      of localhost probably won't work unless you have a full
      MTA running on your machine (which you may under Linux,
      but most probably won't on a Mac, and won't unless hell
      freezes over on Windows...)
    
    - ``portnum`` - the port to connect to on the server; the
      default is the standard SMTP port, but servers that will
      do SSL/TLS (see below) often change the port
    
    - ``username`` - the username to authenticate to the server;
      if this is present, SSL/TLS will be used, and if a password
      is required, the ``password`` argument must be present
    
    - ``password`` - the password to authenticate to the server
    """
    
    msg = Message()
    msg['From'] = fromaddr
    toaddr = [toaddr] if isinstance(toaddr, str) else toaddr
    msg['To'] = ', '.join(toaddr)  # meets RFC2822 address-list spec
    msg['Date'] = msgdate or formatdate()
    msg['Subject'] = subject
    if headers:
        for hname, hvalue in headers.items():
            msg['X-{}'.format(hname)] = hvalue
    msg.set_type(mimetype)
    msg.set_payload(payload, charset)
    server = smtplib.SMTP(server, int(portnum))
    server.set_debuglevel(int(verbose))
    if username and password:
        server.starttls()
        fix_readline(server)
        server.login(username, password)
    server.sendmail(fromaddr, toaddr, msg.as_string())
    server.quit()
