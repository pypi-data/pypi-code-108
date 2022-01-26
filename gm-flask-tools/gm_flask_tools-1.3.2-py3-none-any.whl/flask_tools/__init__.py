import io
import random
import re
import smtplib
import string
import sys
import datetime
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from flask import (
    send_file, request)

import uuid
import os
from pathlib import Path as _PathlibPath, Path
import base64
import flask_dictabase
import hashlib
from werkzeug.utils import secure_filename


def StripNonHex(string):
    ret = ''
    for c in string.upper():
        if c in '0123456789ABCDEF':
            ret += c
    return ret


def MACFormat(macString):
    # macString can be any string like 'aabbccddeeff'
    macString = StripNonHex(macString)
    return '-'.join([macString[i: i + 2] for i in range(0, len(macString), 2)])


def FormatPhoneNumber(phone):
    '''
    FormatPhoneNumber('562-123-4567') > '+15621234567'
    :param phone:
    :return: str
    '''
    phone = phone
    phone = str(phone)

    ret = ''

    # remove non-digits
    for ch in phone:
        if ch.isdigit() or ch == '+':
            ret += ch

    if not ret.startswith('+1'):
        ret = '+1' + ret

    return ret


RE_PHONE_NUMBER = re.compile('\+\d{1}')


def IsValidPhone(phone):
    '''

    :param phone:
    :return:
    '''
    match = RE_PHONE_NUMBER.search(phone)
    ret = match is not None and len(phone) == 12
    return ret


def IsValidMACAddress(mac):
    if not isinstance(mac, str):
        return False

    return bool(re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()))


def IsValidHostname(hostname):
    if not isinstance(hostname, str):
        return False

    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1]  # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def GetRandomID(length=256):
    hash = ''
    for i in range(length):
        hash += random.choice(string.hexdigits)
    return hash


uniqueID = uuid.getnode()


def GetMachineUniqueID():
    ret = HashIt(uuid.getnode())
    return ret


def GetRandomWord():
    return requests.get('https://grant-miller.com/get_random_word').text


def IsValidEmail(email):
    if len(email) > 7:
        if re.match(".+\@.+\..+", email) != None:
            return True
        return False


def IsValidIPv4(ip):
    '''
    Returns True if ip is a valid IPv4 IP like '192.168.254.254'
    Example '192.168.254.254' > return True
    Example '192.168.254.300' > return False
    :param ip: str like '192.168.254.254'
    :return: bool
    '''
    if not isinstance(ip, str):
        return False
    else:
        ip_split = ip.split('.')
        if len(ip_split) != 4:
            return False

        for octet in ip_split:
            try:
                octet_int = int(octet)
                if not 0 <= octet_int <= 255:
                    return False
            except:
                return False

        return True


def MoveListItem(l, item, units):
    # units is an pos/neg integer (negative it to the left)
    '''
    Exampe;
    l = ['a', 'b', 'c', 'X', 'd', 'e', 'f','g']
    MoveListItem(l, 'X', -2)
    >>> l= ['a', 'X', 'b', 'c', 'd', 'e', 'f', 'g']

    l = ['a', 'b', 'c', 'X', 'd', 'e', 'f','g']
    MoveListItem(l, 'X', -2)
    >>> l= ['a', 'b', 'c', 'd', 'e', 'X', 'f', 'g']

    '''
    l = l.copy()
    currentIndex = l.index(item)
    l.remove(item)
    l.insert(currentIndex + units, item)
    return l


def ModIndexLoop(num, min_, max_):
    '''
    Takes an index "num" and a min/max and loops is around
    for example
    ModIndexLoop(1, 1, 4) = 1
    ModIndexLoop(2, 1, 4) = 2
    ModIndexLoop(3, 1, 4) = 3
    ModIndexLoop(4, 1, 4) = 4
    ModIndexLoop(5, 1, 4) = 1
    ModIndexLoop(6, 1, 4) = 2
    :param num: int
    :param min_: int
    :param max_: int
    :return:
    '''
    # print('\nMod(num={}, min_={}, max_={})'.format(num, min_, max))

    maxMinDiff = max_ - min_ + 1  # +1 to include min_
    # print('maxMinDiff=', maxMinDiff)

    minToNum = num - min_
    # print('minToNum=', minToNum)

    if minToNum == 0:
        return min_

    mod = minToNum % maxMinDiff
    # print('mod=', mod)

    return min_ + mod


global app


def Setup(a):
    global app
    app = a


def ListOfDictToJS(l):
    '''
    take in a list of dict
    return a string like """
    events: [
            {
                title: 'All Day Event2',
                start: new Date(y, m, 1)
            },
            {
                id: 999,
                title: 'Repeating Event',
                start: new Date(y, m, d-3, 16, 0),
                allDay: false,
                className: 'info'
            },
            ]
    """
    :param d:
    :return:
    '''

    string = '['

    for d in l:
        string += '{\r\n'

        d = dict(d)  # just to make sure we arent making changes to the database
        for k, v in d.items():
            if isinstance(v, str):
                string += '{}: "{}",\r\n'.format(k, v)
            elif isinstance(v, datetime.datetime):
                month = v.month - 1
                string += '{}: {},\r\n'.format(k, v.strftime('new Date(%Y, {}, %d, %H, %M)'.format(month)))
            elif isinstance(v, bool):
                string += '{}: {},\r\n'.format(k, {True: 'true', False: 'false'}.get(v))
            elif v is None:
                string += '{}: null,\r\n'.format(k, v)
            else:
                string += '{}: {},\r\n'.format(k, v)

        string += '},\r\n'

    string += ']'
    return string


def DecodeLiteral(string):
    return string.decode(encoding='iso-8859-1')


def EncodeLiteral(string):
    return string.encode(encoding='iso-8859-1')


PROJECT_PATH = '.'


def PathString(path):
    if 'win' in sys.platform:
        path = _PathlibPath(path)
        if str(path).startswith('/') or str(path).startswith('\\'):
            return str(path)[1:]
        else:
            return str(path)

    else:  # linux
        mainPath = _PathlibPath(os.path.dirname(sys.modules['__main__'].__file__)).parent

        if 'app/.heroku' in str(mainPath):
            # for heroku, note: Heroku files are ephemeral
            if str(path).startswith('/'):
                return str(path)[1:]
            else:
                return str(path)

        elif 'virtualenv' in __file__:
            # when using pipenv
            projPath = _PathlibPath(PROJECT_PATH)

            if path.startswith('/'):
                if path.startswith(str(projPath)):
                    # path already starts with project path
                    ret = path
                else:
                    path = path[1:]
                    ret = projPath / path
            else:
                ret = projPath / path

            ret = str(ret)
            return ret

        else:
            newPath = mainPath / path
            return str(newPath)[1:]


class File:
    def __init__(self, *a, **k):
        pass


class FormFile(File):
    def __init__(self, requestFilesKey):
        self._key = requestFilesKey
        self._name = secure_filename(
            str(uuid.uuid4()) + request.files[self._key].filename  # adds uuid prefix to prevent colisions
        )
        super().__init__(self._key)

    def SaveTo(self, newPath):
        if _PathlibPath(newPath).is_dir():
            newPath = _PathlibPath(newPath) / self._name

        self._form[self._key].data.save(PathString(newPath))
        return SystemFile(newPath)

    @property
    def Size(self, asString=False):
        size = len(self._form[self._key].data)
        if asString:
            sizeString = '{:,} Bytes'.format(size)
            return sizeString
        else:
            return size

    @property
    def Extension(self):
        return self._form[self._key].data.filename.split('.')[-1].lower()

    def Read(self):
        return self._form[self._key].data.read()

    def Data(self):
        return self._form[self._key].data

    @property
    def Name(self):
        # returns filename like "image.jpg"
        return self._name

    def RenderResponse(self):
        return send_file(
            io.BytesIO(self.Read()),
            mimetype='image/{}'.format(self.Extension),
            as_attachment=False,  # True will make this download as a file
            attachment_filename=self.Name
        )

    def SaveToDatabaseFile(self):
        data = self.Read()
        data = base64.b64encode(data)
        data = data.decode()

        obj = app.db.New(
            DatabaseFile,
            data=data,
            name=self.Name
        )
        return obj


class SystemFile(File):
    def __init__(self, path, data=None, mode='rt'):
        self._path = PathString(path)
        super().__init__(path)

        if data:
            with open(self._path, mode=mode) as file:
                file.write(data)

    @property
    def Size(self, asString=False):
        ''' returns num of bytes'''
        size = os.stat(PathString(self._path)).st_size
        if asString:
            sizeString = '{:,} Bytes'.format(size)
            return sizeString
        else:
            return size

    @property
    def Exists(self):
        return os.path.exists(self._path)

    @property
    def Extension(self):
        ret = _PathlibPath(self._path).suffix.split('.')[-1]
        return ret

    @property
    def Name(self):
        return _PathlibPath(self._path).name

    @property
    def Read(self):
        with open(self._path, mode='rb') as file:
            return file.read()

    def SendFile(self):
        return send_file(self._path)

    @property
    def Path(self):
        return self._path

    def MakeResponse(self, asAttachment=False):
        typeMap = {
            'jpg': 'image',
            'png': 'image',
            'jpeg': 'image',
            'gif': 'image',
            'jfif': 'image',
            'ico': 'image',

            'flv': 'video',
            'mov': 'video',
            'mp4': 'video',
            'wmv': 'video',

            'mp3': 'audio',
            'wav': 'audio',
            'm4a': 'audio',
        }
        return send_file(
            filename_or_fp=self.Path,
            mimetype='{}/{}'.format(
                typeMap.get(self.Extension.lower(), 'image'),
                self.Extension,
            ),
            as_attachment=True if typeMap.get(self.Extension.lower(), 'image') == 'video' else asAttachment,
            attachment_filename=self.Name,
            cache_timeout=1
        )


class DatabaseFile(flask_dictabase.BaseTable):
    # name (str) b64 encoded data
    # data (str) (b''.encode())

    @property
    def Data(self):
        return base64.b64decode(self['data'].encode())

    @property
    def Size(self, asString=False):
        size = len(self.Data)
        if asString:
            sizeString = '{:,} Bytes'.format(size)
            return sizeString
        else:
            return size

    @property
    def Extension(self):
        return self['name'].split('.')[-1].lower()

    def Read(self):
        return self.Data

    @property
    def Name(self):
        return self['name']

    def MakeResponse(self, asAttachment=False):
        typeMap = {
            'jpg': 'image',
            'png': 'image',
            'jpeg': 'image',
            'gif': 'image',

            'flv': 'video',
            'mov': 'video',
            'mp4': 'video',
            'wmv': 'video',

            'mp3': 'audio',
            'wav': 'audio',
            'm4a': 'audio',
        }
        return send_file(
            io.BytesIO(self.Data),
            mimetype='{}/{}'.format(
                typeMap.get(self.Extension.lower(), 'image'),
                self.Extension,
            ),
            as_attachment=True if typeMap.get(self.Extension.lower(), 'image') == 'video' else asAttachment,
            attachment_filename=self['name'],
            cache_timeout=1
        )


def FormatTimeAgo(dt):
    utcNowDt = datetime.datetime.utcnow()
    delta = utcNowDt - dt
    if delta < datetime.timedelta(days=1):
        # less than 1 day ago
        if delta < datetime.timedelta(hours=1):
            # less than 1 hour ago, show "X minutes ago"
            if delta.total_seconds() < 60:
                return '< 1 min ago'
            else:
                minsAgo = delta.total_seconds() / 60
                minsAgo = int(minsAgo)
                return '{} min{} ago'.format(
                    minsAgo,
                    's' if minsAgo > 1 else '',
                )
        else:
            # between 1hour and 24 hours ago
            hoursAgo = delta.total_seconds() / (60 * 60)
            hoursAgo = int(hoursAgo)
            return '{} hour{} ago'.format(
                hoursAgo,
                's' if hoursAgo > 1 else '',
            )
    else:
        # more than 1 day ago
        if delta.days < 31:
            daysAgo = delta.total_seconds() / (60 * 60 * 24 * 1)
            daysAgo = int(daysAgo)
            return '{} day{} ago'.format(
                daysAgo,
                's' if daysAgo > 1 else '',
            )
        else:
            # more then 30 days ago
            months = int(delta.days / 30)
            return '{} month{} ago'.format(
                months,
                's' if months > 1 else '',
            )


def FormatNumberFriendly(num):
    if num < 1000:
        return '{}'.format(num)
    elif num < 99000:
        return '{}K'.format(round(num / 1000, 1))
    elif num < 1000000000:
        return '{}M'.format(round(num / 1000000, 1))


def RemovePunctuation(word):
    word = ''.join(ch for ch in word if ch not in string.punctuation)
    return word


def RemoveNonLetters(word):
    return ''.join(ch for ch in word if ch in string.ascii_lowercase)


def Log(*args):
    with open('ft.log', mode='at') as file:
        file.write(f'{datetime.datetime.now()}: {" ".join([str(a) for a in args])}\r\n')


def HashIt(strng, salt=''):
    hash1 = hashlib.sha512(bytes(strng, 'utf-8')).hexdigest()
    hash1 += salt
    hash2 = hashlib.sha512(bytes(hash1, 'utf-8')).hexdigest()
    return hash2


def IsValidJSID(strng, fix=False):
    if len(strng) >= 1:
        if strng[0].isalpha():
            if ' ' in strng:
                if fix is False:
                    return False
                else:
                    strng = strng.replace(' ', '_')
        else:
            # JSIDs need to start with letter (upper or lower)
            if fix is False:
                return False
            else:
                strng = 'x_' + strng

        allowedSymbols = ['-', '_', ':', '.']
        for ch in strng:
            if not ch.isalnum():
                if ch not in allowedSymbols:
                    if fix is False:
                        return False
                    else:
                        strng = strng.replace(ch, '_')

    return strng


class HashableDict(dict):
    def __new__(cls, item={}):
        # oldPrint('item=', item)
        if item is None:
            return None
        else:
            return super().__new__(cls, item)

    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, HashableDict):
            return self.__key() == other.__key()
        else:
            return False

    def __contains__(self, other):
        return other.items() <= self.items()

    def __add__(self, other):
        # Other will take precedence if duplicate keys in self/other
        retD = self.copy()
        for key, value in other.items():
            retD[key] = value

        return HashableDict(retD)


def GetClientIP(raiseForLocalAddress=True):
    ret = request.remote_addr
    if raiseForLocalAddress and '127.0.0' in ret:
        raise TypeError(
            'reqeust["remote_addr"] "{}" looks like a local address, '
            'you may need to do "from werkzeug.middleware import proxy_fix; '
            'app.wsgi_app = proxy_fix.ProxyFix(app.wsgi_app)". '
            'Or pass GetClientIP(raiseForLocalAddress=False).'
            'You will also need to add this to your nginx config'
            '# the below will pass the client IP to flask'
            'proxy_set_header X-Forwarded-Proto https;'
            'proxy_set_header X-Forwarded-Host {2};'
            'proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;'
        )
    else:
        return ret


def SendEmail_SMTP(smtpServerURL, smtpUsername, smtpPassword, to, frm, cc=None, bcc=None, subject=None, body=None,
                   html=None, attachments=None):
    """

    :param smtpServerURL:
    :param smtpUsername:
    :param smtpPassword:
    :param to:
    :param frm:
    :param cc:
    :param bcc:
    :param subject:
    :param body:
    :param html: body using html, not supported by all email clients
    :param attachments: list of filepaths
    :return:
    """

    # Create message container - the correct MIME type is multipart/alternative.
    multipart = MIMEMultipart('alternative')

    subject = subject or 'No Subject'

    multipart['Subject'] = subject
    multipart['From'] = frm
    multipart['To'] = to
    if cc:
        multipart['Cc'] = cc
    if bcc:
        multipart['Bcc'] = bcc

    # Create the body of the message (a plain-text and an HTML version).

    # Record the MIME types of both parts - text/plain and text/html.
    partBody = MIMEText(body, 'plain')

    html = html or f'''
            <html>
                <body>
                    {body}
                </body>
            </html>
            '''
    partHTML = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    multipart.attach(partBody)
    multipart.attach(partHTML)

    # attachment files
    attachments = attachments or []
    for attachment in attachments:
        with open(attachment, mode='rb') as aFile:
            file = MIMEApplication(aFile.read())
            name = Path(attachment).name
            file.add_header('Content-Disposition', 'attachment', filename=name)
            multipart.attach(file)

    # send the message
    with smtplib.SMTP_SSL(
            host=smtpServerURL,
            port=465,
    ) as smtp:
        smtp.login(smtpUsername, smtpPassword)

        if sys.platform.startswith('win'):
            smtp.set_debuglevel(1)

        smtp.sendmail(
            from_addr=frm,
            to_addrs=to,
            msg=multipart.as_string(),
        )
        smtp.quit()
