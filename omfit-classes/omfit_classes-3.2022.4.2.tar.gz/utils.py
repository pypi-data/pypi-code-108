print('Loading utility functions...')

from omfit_classes.utils_base import *
from omfit_classes.utils_base import _available_to_user_math, _available_to_user_util, _available_to_user_plot
import omfit_classes.utils_base
import omfit_classes.utils_base as utils_base

from omfit_classes.utils_plot import *
import omfit_classes.utils_plot
import omfit_classes.utils_plot as utils_plot

from omfit_classes.utils_math import *
import omfit_classes.utils_math
import omfit_classes.utils_math as utils_math

from omfit_classes.utils_fit import *
import omfit_classes.utils_fit
import omfit_classes.utils_fit as utils_fit

from omfit_classes.utils_fusion import tokamak, is_device
from omfit_classes.utils_fusion import _available_to_user_fusion
import omfit_classes.utils_fusion
import omfit_classes.utils_fusion as utils_fusion

from utils_widgets import *
import utils_widgets

# ---------------------
# Sending email
# ---------------------
class EmailException(Exception):
    """
    An Exception class to be raised by a send_email function
    """

    pass


@_available_to_user_util
def send_email(
    to='',
    cc='',
    fromm='',
    subject='',
    message='',
    attachments=None,
    server=None,
    port=None,
    username=None,
    password=None,
    isTls=False,
    quiet=True,
):
    """
    Send an email, using localhost as the smtp server.

    :param to: must be one of
        1) a single address as a string
        2) a string of comma separated multiple address
        3) a list of string addresses

    :param fromm: String

    :param subject: String

    :param message: String

    :param attachments: List of path to files

    :param server: SMTP server

    :param port: SMTP port

    :param username: SMTP username

    :param password: SMTP password

    :param isTls: Puts the connection to the SMTP server into TLS mode

    :return: string that user can decide to print to screen
    """

    from email.mime.multipart import MIMEMultipart
    from email.mime.base import MIMEBase
    from email.mime.text import MIMEText
    from email.utils import formatdate
    from email import encoders

    if isinstance(to, str):
        to = to.split(',')
    if isinstance(cc, str):
        cc = cc.split(',')

    if attachments is None:
        attachments = []

    for address in [_f for _f in tolist(to) + tolist(fromm) if _f]:
        if not re.match(r'.*@.*\..*', address):
            raise EmailException('<%s> is not a valid email address' % address)

    msg = MIMEMultipart()
    msg['From'] = fromm
    msg['To'] = ','.join(to)
    msg['CC'] = ','.join(cc)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach(MIMEText(message))

    for f in attachments:
        part = MIMEBase('application', "octet-stream")
        with open(f, "rb") as _f:
            part.set_payload(_f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    if server is None and system_executable('sendmail') is not None:
        p = subprocess.Popen(
            [system_executable('sendmail'), "-t", "-oi"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        std_out, std_err = list(map(b2s, p.communicate(bytes(msg.as_string(), 'utf8'))))
        if p.returncode:
            raise OMFITexception(f'Could not send email with `sendmail`!\n\n{std_out}\n\n{std_err}')
    else:
        try:
            import smtplib

            if port is None:
                port = 25
                if isTls:
                    port = 587

            smtp = smtplib.SMTP(server, port)
            smtp.connect()
            if isTls:
                smtp.starttls()
            if username or password:
                smtp.login(username, password)
            smtp.sendmail(fromm, to, msg.as_string())
            smtp.quit()
        except Exception as _excp:
            raise OMFITexception('Could not send email: %s\n\nTry installing `sendmail` on your system.' % repr(_excp))

    return f'Email `{subject}` sent to {[k for k in tolist(to) + tolist(cc) if k]}'


class AskPassGUI(tk.Toplevel, AskPass):
    """
    Class that builds a Tk GUI to ask password and one-time-password secret if credential file does not exists
    """

    def __init__(self, credential, force_ask=False, parent=None, title='Enter password', OTP=False, **kw):
        r"""
        :param credential: credential filename to look for under the  OMFITsettingsDir+os.sep+'credentials' directory

        :param force_ask: force asking for the password (if file exists pwd is shown for amendment)

        :param OTP: ask for one-time-password secret; if 'raw' do not pass through pyotp.now()

        :param parent: parent GUI

        :param title: title of the GUI

        :param \**kw: extra arguments passed to tk.Toplevel
        """
        AskPass.__init__(self, credential, force_ask=force_ask, OTP=OTP, parent=parent, title=title, **kw)

    def ask(self, pwd, otp, OTP, store, **kw):
        title = kw.pop('title', 'Enter password')
        parent = kw.pop('parent', None)
        if parent is None:
            parent = OMFITaux['rootGUI']
        tk.Toplevel.__init__(self, parent, **kw)
        self.withdraw()
        self.transient(parent)
        self.wm_title(self.credential)

        frm = ttk.Frame(self)
        frm.pack(side=tk.TOP, padx=5, pady=5)
        ttk.Label(frm, text=self.explain).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Separator(self).pack(side=tk.TOP, padx=5, pady=5, fill=tk.X, expand=tk.NO)

        self.otp = ttk.Entry()
        OTP_text = []
        if OTP and OTP != 'raw':
            OTP_text = ['OTP secret (32 digits)']
        else:
            OTP_text = ['OTP']
        for k, field in enumerate(['Username', 'Password', 'Server', 'Port'] + OTP_text + ['Save']):
            frm = ttk.Frame(self)
            frm.pack(side=tk.TOP, padx=5, pady=5, fill=tk.X, expand=tk.NO)
            if field == 'Password':
                e = ttk.Entry(frm, width=20, show='*')
            elif field == 'Save':
                e = ttk.Checkbutton(frm, text='Save credentials')
                e.state(['!alternate'])
            else:
                e = ttk.Entry(frm, width=20)
            e.pack(side=tk.RIGHT, padx=5, pady=5, fill=tk.X, expand=tk.YES)
            if field == 'Password':
                self.pwdGUI = e
                e.insert('insert', pwd)
            elif field.startswith('OTP'):
                self.otpGUI = e
                e.insert('insert', otp)
            elif field == 'Save':
                self.storeGUI = e
                e.state([['!selected', 'selected'][store]])
            else:
                e.insert('insert', parse_server(self.credential)[k])
                e.config(state=tk.DISABLED)

            if field != 'Save':
                ttk.Label(frm, text=field + ':').pack(side=tk.RIGHT, padx=5, pady=5)

        def doStore(event=None):
            self.store = self.storeGUI.state()
            self.pwd = self.pwdGUI.get()
            self.otp = self.otpGUI.get()
            # if we decide not to store the password, the credential file is still generated but it will contain an empty password and OTP
            if self.store:
                self.encrypt(self.pwd, self.otp)
            else:
                self.encrypt('', '')

        self.pwdGUI.bind('<Return>', doStore)
        self.otpGUI.bind('<Return>', doStore)
        self.storeGUI.bind('<Return>', doStore)
        self.bind('<Escape>', lambda event=None: self.destroy())

        tk_center(self, parent)
        self.deiconify()
        self.wait_window(self)


# ---------------------
# Licenses
# ---------------------
OMFITlicenses = {}


class LicenseException(Exception):
    """
    An Exception class to be raised by a License object
    """

    pass


class License(object):
    """
    The purpose of this class is to have a single point of interaction with a
    given license.  After the License is initialized, then it should be checked
    when the given code (or member of a suite) is to be run.

    All licenses are stored in $HOME/.LICENCES/<codename>

    :param codename: The name of the code (or suite) to which the license applies

    :param fn: The location (filename) of the software license

    :param email_dict: (optional) At least two members

        * email_address - The address(es) to which the email should be sent,
                        if multiple, as a list

        * email_list - A message describing any lists to which the user should
                        be added for email notifications or discussion

    :param rootGUI: tkInter parent widget

    :param web_address: (optional) A URL for looking up the code license
    """

    def __init__(self, codename, fn, email_dict={}, web_address=None, rootGUI=None):
        if not os.path.exists(fn):
            raise OSError('The license file %s must exist' % fn)

        self.rootGUI = rootGUI
        self.codename = codename
        self.fn = fn
        self.web_address = web_address
        self.email_dict = email_dict

        if 'email_address' in email_dict:
            if not isinstance(email_dict['email_address'], (list, tuple)):
                self.email_dict['email_address'] = [email_dict['email_address']]

        with open(fn, 'r') as f:
            self.license = f.read()

        lic_dir = '%s/.LICENSES/' % (os.environ['HOME'],)
        if not os.path.exists(lic_dir):
            os.makedirs(lic_dir)

        self.lic_fn = lic_dir + codename
        self.exists = False
        self.up_to_date = False

        if os.path.exists(self.lic_fn):
            # If there is the right license file, use it
            self.exists = True

            # up_to_date if identical
            with open(self.lic_fn, 'r') as f:
                tmp = f.read()
                # do not prompt for re-signing the license if only
                # the url of OMFIT users agreement form has changed
                if codename == 'OMFIT':
                    tmp = tmp.replace('http://www.emailmeform.com/builder/form/DI304clW1R', 'https://forms.gle/oLihKwkXSy4sRXPbA')
                    tmp = tmp.replace('https://forms.gle/oLihKwkXSy4sRXPbA', 'http://form.omfit.io')
                if self.license == tmp:
                    self.up_to_date = True
                # up-do-date if newer, which can happen if user switched
                # between versions (then we do not keep asking each time)
                elif os.path.getmtime(self.lic_fn) > os.path.getmtime(fn):
                    self.up_to_date = True

        else:
            # Alternatively, check if the user has signed the same
            # exact license file but with a different codename
            # (then we can skip asking to sign it over and over)
            for k in glob.glob(lic_dir + '*'):
                with open(k, 'r') as f:
                    tmp = f.read()
                    # do not prompt for re-signing the license if only
                    # the url of OMFIT users agreement form has changed
                    if codename == 'OMFIT':
                        tmp = tmp.replace('http://www.emailmeform.com/builder/form/DI304clW1R', 'https://forms.gle/oLihKwkXSy4sRXPbA')
                        tmp = tmp.replace('https://forms.gle/oLihKwkXSy4sRXPbA', 'http://form.omfit.io')
                if self.license == tmp:
                    self.exists = True
                    self.up_to_date = True
                    break

    def check(self):
        """
        Check if license was accepted and is up-to-date.
        If not up-to-date ask to accept new license, but do not send email/web-browser and such.

        :return: whether the licence was accepted and up-to-date
        """

        if self.exists and self.up_to_date:
            return

        accept = False

        if self.exists and not self.up_to_date:
            dialog(
                title='%s License Has Been Updated' % self.codename,
                message=f'The license for {self.codename} has been updated, here it is for your approval.',
                answers=['Ok'],
                icon='info',
            )

            accept = self.present_license()

        if not self.exists:
            dialog(
                title='%s License Not Yet Accepted' % self.codename,
                message='You have not yet accepted the license for %s.\n'
                'You will now be presented with the methods for '
                'accepting the license.\n'
                'If accepted, the license will be stored in\n'
                '%s' % (self.codename, self.lic_fn),
                answers=['Ok'],
                icon='info',
            )

            # present it online
            if self.web_address:
                from omfit_classes.omfit_weblink import openInBrowser

                openInBrowser(self.web_address)
                time.sleep(10)
                accept = (
                    dialog(
                        title='Accept %s License?' % self.codename,
                        message='Do you accept the license for %s ' 'as it is presented in the web' 'browser?' % self.codename,
                        answers=['Yes', 'No'],
                        icon='question',
                    )
                    == 'Yes'
                )

            # email it
            elif 'email_address' in self.email_dict:
                try:
                    eml = tk.email_widget(
                        OMFITaux['rootGUI'],
                        fromm=self.email_dict.get('fromm', ''),
                        to=','.join(self.email_dict['email_address']),
                        subject='Accepting %s License Through OMFIT' % self.codename,
                        message=str('\n\n-------------\n\n' + self.license),
                        lock_to=True,
                        lock_subject=True,
                        prompt=self.email_dict.setdefault('email_prompt', None),
                        title='Email acceptance of %s license agreement' % self.codename,
                        quiet=False,
                    )
                    eml.wait_window(eml)
                except Exception as _excp:
                    top.destroy()
                    dialog(
                        title='Failed email license',
                        message='Automatic send of email has failed: %s\n'
                        'Please send an email to %s in order to use %s.' % (repr(_excp), self.email_dict['email_address'], self.codename),
                        answers=['Ok'],
                        icon='error',
                    )
                    raise LicenseException(
                        'Automatic send of email has failed: %s\n'
                        'Please send an email to %s in order to use %s.' % (repr(_excp), self.email_dict['email_address'], self.codename)
                    )

                if eml.sent:
                    accept = True

            # show it
            else:
                accept = self.present_license()

        if not accept:
            dialog(
                title='Did not accept license',
                message='You must accept the license agreement to use %s' % self.codename,
                answers=['Ok'],
                icon='warning',
            )
            raise LicenseException('You must accept the license agreement to use %s' % self.codename)

        if 'email_list' in self.email_dict:
            dialog(title='Email List Info', message=self.email_dict['email_list'], answers=['Ok'], icon='info')

        with open(self.lic_fn, 'w') as f:
            f.write(self.license)

    def present_license(self):
        """
        Show the license as a read-only scrolled text

        :return: whether the user accepts the licence
        """
        import tkinter as tk

        self.accept_license = False

        top = tk.Toplevel(self.rootGUI)
        top.wm_title('License for %s' % self.codename)
        st = tk.ScrolledReadOnlyText(master=top, initial_text=self.license)
        st.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        ttk.Label(top, text='Do you accept the license?').pack(side=tk.LEFT, expand=tk.FALSE, fill=tk.NONE)

        def on_yes():
            self.accept_license = True
            top.destroy()

        def on_no():
            self.accept_license = False
            top.destroy()

        frm = ttk.Frame(top)
        frm.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.BOTH)
        ttk.Button(top, text='Yes', command=on_yes).pack(side=tk.LEFT, fill=tk.BOTH)
        ttk.Button(top, text='No', command=on_no).pack(side=tk.LEFT, fill=tk.BOTH)
        top.deiconify()
        top.wait_window(top)
        top.update_idletasks()

        return self.accept_license


# ---------------------
# geolocation
# ---------------------
def getIP_lat_lon(ip, verbose=True, access_key='9bf65b672b3903d324044f1efc4abbd1'):
    """
    Connect to the ipstack web service to get geolocation info from a list of IP addresses.

    :param ip: single IP string, list of IPs, or dictionary with IPs as keys

    :param verbose: print info to screen as it gets fetched

    :param access_key: https://ipstack.com acecss key

    :return: dictionary with IPs as string with location information
    """
    if isinstance(ip, dict):
        ip_list = list(ip.keys())
        results = ip
    else:
        ip_list = tolist(ip)
        results = {}

    if verbose and len(ip_list) > 1:
        print("Processing {} IPs...".format(len(ip_list)))

    for ip in ip_list:
        if ip in results and results[ip] is not None:
            continue

        data = '{}'
        query = "http://api.ipstack.com/%s?access_key=%s" % (ip, access_key)
        try:
            import requests

            data = requests.get(query, timeout=1).text
        except Exception as _excp:
            printe(query)
            printe(repr(_excp))

        json_response = json.loads(data)

        if 'location' in json_response:
            del json_response['location']

        if verbose:
            print(pprint(json_response))

        results[ip] = json_response

    return results


def generate_map(lats=[], lons=[], wesn=None, s=100, **kw):
    r"""
    Using the basemap matplotlib toolkit, this function generates a map and
    puts a markers at the location of every latitude and longitude found in the list

    :param lats: list of latitude floats

    :param lons: list of longitude floats

    :param wesn: list of 4 floats to clip map west, east, south, north

    :param s: size of the markers

    :param \**kw: other arguments passed to the scatter plot

    :return: mpl_toolkits.basemap.Basemap object
    """
    # make use of basemap robust when used within CONDA environment
    if 'PROJ_LIB' not in os.environ:
        os.environ["PROJ_LIB"] = os.sep.join(sys.executable.split(os.sep)[:-2] + ['share', 'proj'])

    from mpl_toolkits.basemap import Basemap

    if wesn:
        wesn = [float(i) for i in wesn.split('/')]
        m = Basemap(projection='cyl', resolution='l', llcrnrlon=wesn[0], llcrnrlat=wesn[2], urcrnrlon=wesn[1], urcrnrlat=wesn[3])
    else:
        m = Basemap(projection='cyl', resolution='l')
    m.bluemarble()
    x, y = m(lons, lats)
    kw.setdefault('marker', 'o')
    kw.setdefault('edgecolor', 'r')
    kw.setdefault('facecolor', 'none')
    m.scatter(x, y, s=s, **kw)
    return m


# ---------------------
# Documentation
# ---------------------
@_available_to_user_util
def clean_docstring_for_help(string_or_function_in, remove_params=True, remove_deep_indentation=True):
    """
    Processes a function docstring so it can be used as the help tooltip for a GUI element without looking awkward.
    Protip: you can test this function on its own docstring.

    Example usage::

        def my_function():
            '''
            This docstring would look weird as a help tooltip if used directly (as in help=my_function.__doc__).
            The line breaks and indentation after line breaks will not be appropriate.
            Also, a long line like this will be broken automatically when put into a help tooltip, but it won't be indented.
            However, putting it through clean_docstring_for_help() will solve all these problems and the re-formatted text
            will look better.
            '''
            print('ran my_function')
            return 0
        OMFITx.Button("Run my_function", my_function, help=clean_docstring_for_help(my_function))

    :param string_or_function_in: The string to process, expected to be either the string stored in function.__doc__
        or just the function itself (from which .__doc__ will be read). Also works with OMFITpythonTask, OMFITpythonGUI,
        and OMFITpythonPlot instances as input.

    :param remove_params: T/F: Only keep the docstring up to the first instance of "    :param " or "    :return " as
        extended information about parameters might not fit well in a help tooltip.

    :param remove_deep_indentation: T/F: True: Remove all of the spaces between a line break and the next non-space
        character and replace with a single space. False: Remove exactly n spaces after a line break, where n is the
        indentation of the first line (standard dedent behavior).

    :return: Cleaned up string without spacing or line breaks that might look awkward in a GUI tooltip.
    """

    if type(string_or_function_in).__name__ in ['OMFITpythonTask', 'OMFITpythonGUI', 'OMFITpythonPlot', 'OMFITpythonTest']:
        try:
            # Solution from https://stackoverflow.com/a/43522304/6605826
            with open(string_or_function_in.filename, 'r') as f:
                tree = ast.parse(f.read())
            string_in = str(ast.get_docstring(tree))
        except SyntaxError:
            string_in = 'Error reading docstring from {}'.format(string_or_function_in)
    elif callable(string_or_function_in):
        string_in = string_or_function_in.__doc__
    else:
        string_in = string_or_function_in

    import textwrap

    string_in = textwrap.dedent(string_in)  # Remove standard indentation (if present) after line break.

    preserver = '`doublelinebreak`'
    param_preserver = '`param`'
    return_preserver = '`return`'

    string_out = string_in.replace('\n\n', preserver)  # Save double line breaks because they must be intentional
    if remove_params:
        string_out = string_out.split(':param ')[0].split(':return ')[0]  # Do return also in case no params.
    else:
        string_out = string_out.replace('\n:param', param_preserver).replace('\n:return', return_preserver)
    if remove_deep_indentation:
        string_out = re.sub(r'\n\s+', ' ', string_out)  # Remove all indentation after line break.
    string_out = string_out.replace('\n', ' ')  # Remove any left over line breaks
    string_out = string_out.replace(preserver, '\n\n')  # Put double line break back in
    if not remove_params:
        # Replace line breaks in front of params
        string_out = string_out.replace(param_preserver, '\n:param').replace(return_preserver, '\n:return')

    string_out = string_out.strip()  # Remove leading & trailing whitespace

    return string_out


def numeric_type_subclasser(binary_function='__binary_op__', unary_function='__unary_op__'):
    """
    This is a utility function to list the methods that need to be defined
    for a class to behave like a numeric type in python 3. This used to be
    done by the `__coerce__` method in Python 2, but that's no more available.

    :param binary_function: string to be used for binary operations

    :param unary_function: string to be used for unary operations
    """
    if binary_function is not None:
        print('# Binary operations')

        for attr in [
            'lt',
            'le',
            'eq',
            'ne',
            'ge',
            'gt',
            '__lt__',
            '__le__',
            '__eq__',
            '__ne__',
            '__ge__',
            '__gt__',
            'is_',
            'is_not',
            'add',
            '__add__',
            '__radd__',
            'and_',
            '__and__',
            '__rand__',
            'floordiv',
            '__floordiv__',
            '__rfloordiv__',
            'index',
            '__index__',
            'lshift',
            '__lshift__',
            '__rlshift__',
            'mod',
            '__mod__',
            '__rmod__',
            'mul',
            '__mul__',
            '__rmul__',
            'matmul',
            '__matmul__',
            'or_',
            '__or__',
            '__ror__',
            'pow',
            '__pow__',
            '__rpow__',
            'rshift',
            '__rshift__',
            '__rrshift__',
            'sub',
            '__sub__',
            '__rsub__',
            'truediv',
            '__truediv__',
            '__rtruediv__',
            '__divmod__',
            '__rdivmod__',
            'xor',
            '__xor__',
            '__rxor__',
        ]:
            print(
                '''
def %s(self, other):
    return self.%s(other,'%s')'''
                % (attr, binary_function, attr)
            )

    if unary_function is not None:
        print('# Unary operations')

        for attr in [
            'bool',
            '__bool__',
            '__nonzero__',
            'real',
            'imag',
            'not_',
            '__not__',
            'truth',
            'abs',
            '__abs__',
            'inv',
            'invert',
            '__inv__',
            '__invert__',
            'neg',
            '__neg__',
            'pos',
            '__pos__',
            '__float__',
            '__complex__',
            '__oct__',
            '__hex__',
            '__trunc__',
        ]:
            print(
                '''
def %s(self):
    return self.%s('%s')'''
                % (attr, unary_function, attr)
            )


# ============================

if __name__ == '__main__':
    repo = OMFITgit(os.path.split(os.path.abspath(__file__))[0] + '/../')
    t1 = time.time()
    repo.get_module_params(path='modules')
    print(time.time() - t1)
    t1 = time.time()
    print(repo.get_remotes())
    print(time.time() - t1)
    t1 = time.time()
    th = repo.tag_hashes()
    print(th)
    print(time.time() - t1)
    t1 = time.time()
    gvc = repo.get_visible_commits()
    print(gvc)
    print(time.time() - t1)
