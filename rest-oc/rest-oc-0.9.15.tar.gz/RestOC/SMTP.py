# coding=utf8
"""SMTP

Wrapper for python smtp module
"""

# Compatibility
from past.builtins import basestring

__author__ = "Chris Nasr"
__copyright__ = "OuroborosCoding"
__version__ = "1.0.0"
__email__ = "chris@ouroboroscoding.com"
__created__ = "2018-11-17"

# Python imports
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import smtplib
import socket
from os.path import basename

# Init the local variables
__mdSMTP = {
	"host": "localhost",
	"port": 25,
	"tls": False,
	"passwd": ""
}

# Init the last error message
__msError = '';

# Create the defines
OK = 0
ERROR_UNKNOWN = -1
ERROR_CONNECT = -2
ERROR_LOGIN = -3

def _addresses(l):
	"""Addresses

	Takes a string or list of strings and returns them formatted for to:, cc:,
	or bcc:

	Arguments:
		l (str|str[]): The address or list of addresses

	Returns:
		str
	"""

	# If we got a list, tuple, or set
	if isinstance(l, (list,tuple,set)):
		return ', '.join(l)
	else:
		return l

def _to(l):
	"""To

	Converts all addresses passed, whether strings or lists, into one singular
	list

	Arguments:
		l (list(str|str[])): The list of addresses or lists of addresses

	Returns:
		list
	"""

	# Init the return list
	lRet = []

	# Go through each item in the list
	for m in l:

		# If we got a list
		if isinstance(m, (list,tuple)):
			lRet.extend(m)

		# Else, we got one address
		else:
			lRet.append(m)

	# Return the full list
	return lRet

def init(host="localhost", port=25, tls=False, user=None, passwd=None):
	"""init

	Called to change/set any SMTP information before sending out any e-mails

	Args:
		host (str): The hostname of the SMTP server
		port (uint): The port on the host
		tls (bool): Set to True if we need TLS
		user (str): The authorization username
		passwd (str): The authorization password

	Returns:
		None
	"""

	# Import the module var
	global __mdSMTP

	# If the host is set
	if host:
		__mdSMTP['host'] = host

	# If the port is set
	if port:
		__mdSMTP['port'] = port

	# If we need TLS
	if tls:
		__mdSMTP['tls'] = tls

	# If the user is set
	if user:
		__mdSMTP['user'] = user

	# If the passwd is set
	if passwd:
		__mdSMTP['passwd'] = passwd

def lastError():
	"""Last Error

	Returns the last error message if there is one

	Returns:
		str
	"""
	global __msError
	return __msError

def send(to, subject, text_body = None, html_body = None, from_='root@localhost', bcc=None, attachments=None):
	"""Send

	Sends an e-mail to one or many addresses

	Arguments:
		to (str|str[]): One or email addresses to send to
		subject (str): The email's subject
		text_body (str): The text version of the main content of the email
		html_body (str): The html version of the main content of the email
		from_ (str): The from address of the email, optional
		bcc (str|str[]): Blind carbon copy addresses, optional
		attachments

	Returns:
		bool
	"""

	# Opts
	dOpts = {}

	# Add available options
	if text_body:	dOpts['text'] = text_body
	if html_body:	dOpts['html'] = html_body
	if from_:		dOpts['from'] = from_
	if bcc:			dOpts['bcc'] = bcc
	if attachments:	dOpts['attachments'] = attachments

	# Call new method and return result
	return Send(to, subject, dOpts)

def Send(to, subject, opts):
	"""Send

	Sends an e-mail to one or many addresses based on a dictionary of options

	Arguments:
		to (str|str[]): The email or emails to send the email to
		subject (str): The subject of the email
		opts (dict): The options used to generate the email and any headers
						'html': str
						'text': str
						'from': str,
						'reply-to': str
						'cc': str|str[]
						'bcc': str|str[]
						'attachments': list(str|dict('body', 'filename'))
							If an attachment is a string, a local filename is
							assumed, else if we receive a dictionary, it should
							contain the filename of the file, and the raw body
							of the file
						'unsubscribe': str

	Returns:
		bool
	"""

	# Import the module vars
	global __msError, __mdSMTP

	# Init the list of total "to"s
	lTO = []

	# If from is missing
	if 'from' not in opts:
		opts['from'] = 'noreply@%s' % socket.gethostname()

	# Create a new Mime MultiPart message
	oMMP = MIMEMultipart('mixed')
	oMMP['From'] = opts['from']
	oMMP['To'] = _addresses(to)
	oMMP['Date'] = formatdate()
	oMMP['Subject'] = subject

	# Add the to
	lTO.append(to)

	# If we have a reply-to
	if 'reply-to' in opts:
		oMMP['reply-to'] = opts['reply-to']

	# If we have cc
	if 'cc' in opts:
		oMMP['Cc'] = _addresses(opts['cc'])
		lTO.append(opts['cc'])

	# If we have bcc
	if 'bcc' in opts:
		lTO.append(opts['bcc'])

	# If we have an unsubscribe string
	if 'unsubscribe' in opts:
		oMMP.add_header('List-Unsubscribe', opts['unsubscribe'])

	# Create the alternative part for the content
	oAlternative = MIMEMultipart('alternative')

	# Check that text or html body is set
	if 'text' not in opts and 'html' not in opts:
		return ValueError('need one of "text" or "html" in Send options')

	# Attach the main message
	if 'text' in opts and opts['text']:
		oAlternative.attach(MIMEText(opts['text'], 'plain'))
	if 'html' in opts and opts['html']:
		oAlternative.attach(MIMEText(opts['html'], 'html'))

	# Add the alternative section to the email
	oMMP.attach(oAlternative)

	# If there's any attachments
	if 'attachments' in opts:

		# If we didn't get a list
		if not isinstance(opts['attachments'], (list,tuple)):
			raise ValueError('"attachments" must be a list if set')

		# Loop through the attachments
		for m in opts['attachments']:

			# If we got a string
			if isinstance(m, basestring):

				# Assume it's a file and open it
				with open(m, "rb") as rFile:
					oMMP.attach(MIMEApplication(
						rFile.read(),
						Content_Disposition='attachment; filename="%s"' % basename(m),
						Name=basename(m)
					))

			# Else if we get a dict
			elif isinstance(m, dict):

				# Add it
				oMMP.attach(MIMEApplication(
					m['body'],
					Content_Disposition='attachment; filename="%s"' % m['filename'],
					Name=m['filename']
				))

			# Unknown type
			else:
				raise ValueError('Invalid attachment', m)

	# Generate the body
	sBody = oMMP.as_string()

	# Catch any Connect or Authenticate Errors
	try:

		# Create a new instance of the SMTP class
		oSMTP = smtplib.SMTP(__mdSMTP['host'], __mdSMTP['port'])

		# If we need TLS
		if __mdSMTP['tls']:

			# Start TLS
			oSMTP.starttls()

		# If there's a username
		if __mdSMTP['user']:

			# Log in with the given credentials
			oSMTP.login(__mdSMTP['user'], __mdSMTP['passwd'])

		# Try to send the message, then close the SMTP
		oSMTP.sendmail(opts['from'], _to(lTO), sBody)
		oSMTP.close()

		# Return ok
		return OK

	# If there's a connection error
	except smtplib.SMTPConnectError as e:
		__msError = str(e.args)
		return ERROR_CONNECT

	# If there's am authentication error
	except smtplib.SMTPAuthenticationError as e:
		__msError = str(e.args)
		return ERROR_LOGIN

	# If there's any other error
	except smtplib.SMTPException as e:
		__msError = str(e.args)
		return ERROR_UNKNOWN
