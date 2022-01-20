# -*- coding:utf-8 -*-
import imaplib
import email
import getpass

from transparentpath import TransparentPath
import chardet
import sys
import traceback
import socket
import atexit

from time import sleep, time
from pathlib import Path
import numpy as np
from typing import Union, List, Dict, Optional
from datetime import datetime, date as ddate
from multiprocessing.pool import ThreadPool
import logging

from .mailsender import MailSender

logger = logging.getLogger(__name__)


def login(username, password, server, port):
    mail = imaplib.IMAP4_SSL(server, port)
    mail.login(username, password)
    mail.select()
    return mail


class MailException(Exception):
    """Any kind of mail error"""

    def __init__(self, msg: str = None):
        self.message = msg or "There is a problem with the mails..."
        super().__init__(self.message)

    def __str__(self):
        return self.message


def get_datetime_now(fmt: str = "%d%m%Y %H:%M:%S") -> str:
    """

    Parameters
    ----------
    fmt: str
         The date format to use (Default value = "%d%m%Y %H:%M:%S")

    Returns
    -------
    str

    """

    d = datetime.now()
    return d.strftime(fmt)


# noinspection PyBroadException, PyUnresolvedReferences
def persist_file(filepath: "TransparentPath", part) -> None:
    """

    Parameters
    ----------
    filepath: TransparentPath

    part:


    Returns
    -------
    None

    """
    data = part.get_payload(decode=True)
    filepath.write_bytes(data)
    logger.info(f"SAVING FILE to : {filepath}.")


# noinspection PyUnresolvedReferences
def rename_file(
    filename, to_path: Union[str, Path, "TransparentPath"], overwrite: bool = True
) -> Union[Path, "TransparentPath"]:
    """

    Parameters
    ----------
    filename: str

    to_path: Union[str, Path, "TransparentPath"]

    overwrite: bool
        If True, will overwrite any file with the same name. Else rename it
        appending to now's datetime.


    Returns
    -------
    Union[str, Path, "TransparentPath"]

    """
    date_ref = datetime.today()

    try:
        filepath = to_path / filename
    except TypeError:
        to_path = Path(to_path)
        filepath = to_path / filename
    ext = filepath.suffix
    if filepath.is_file() and overwrite is False:
        filepath = type(to_path)(f"{to_path / filepath.stem}_{date_ref}{ext}")
    return filepath


# noinspection PyUnresolvedReferences
def save_attachment(part, to_path: Union["TransparentPath", Path, str], overwrite: bool = True) -> None:
    """

    Parameters
    ----------
    part:

    to_path: Union[TransparentPath, Path, str]
        The directory to save the file in

    overwrite: bool
        If True, will overwrite any file with the same name. Else rename it
        appending to now's datetime.


    Returns
    -------
    None

    """
    if part.get("Content-Disposition") is None:
        return

    if part.get_content_maintype() != "multipart":
        name = part.get_filename()
        if not name:
            raise ValueError(f"No file name in part {part}!")
        name = name.replace("\r", "").replace("\n", "")
        filepath = rename_file(name, to_path, overwrite)
        persist_file(filepath, part)


def split_spec_char(s):
    trimmed_s = s.encode("ascii", errors="ignore").decode("ascii")
    spec_chars = set([c for c in s if c not in trimmed_s])
    out = [""]
    for c in s:
        if c not in spec_chars:
            out[-1] += c
        else:
            out.append("")
    return [o for o in out if o != ""]


class MailMonitor(object):
    """Class allowing to monitor a mailbox to save attachments to a
    directory using conditions on sender and subjet.

    If two-factor auth is activated, you will need to
    provide  an app password instead of your regular password. If you do not
    have one or do not remember it, make a new one by following the
    instructions here (only valid for office365 acconuts):
    https://docs.microsoft.com/fr-fr/azure/active-directory/user-help/
    multi-factor-authentication-end-user-app-passwords

    The relevant security page to set the app passwords :
    https://account.activedirectory.windowsazure.com/Proofup.aspx

    MailMonitor will use threading to allow for the monitoring of
    different conditions and saving to different paths.

    For a basic usage (monitoring one set of conditions and saving to one
    location) :

    >>> from mailutility import MailMonitor  # doctest: +SKIP
    >>> mail = MailMonitor("username")  # doctest: +SKIP
    >>> mail.monitor(  # doctest: +SKIP
    >>>     conditions={"subject": "test",  # doctest: +SKIP
    >>>                 "sender": "cottephi@gmail.com"},  # doctest: +SKIP
    >>>     to_path="/home/username/Bureau",  # doctest: +SKIP
    >>>     time_to_sleep=5  # doctest: +SKIP
    >>> )  # doctest: +SKIP

    To monitor several sources and save to different paths, use :

    >>> mail.monitor(  # doctest: +SKIP
    >>>     conditions=[{"sender": "a@b.c", "subject": "g"}, {"sender": "d@e.f", "subject": "h"}],  # doctest: +SKIP
    >>>     to_path=["/home/username/Desktop", "/home/username/Documents"],  # doctest: +SKIP
    >>>     time_to_sleep=5,  # doctest: +SKIP
    >>> )

    You can decide to save to GCS by using TransparentPath:

    >>> # noinspection PyShadowingNames, PyUnresolvedReferences
    >>> from transparentpath import TransparentPath as Path  # doctest: +SKIP
    >>> Path.set_global_fs("gcs", bucket="my_bucket", project="my_project")  # doctest: +SKIP
    >>> mail = MailMonitor("tomonitor@mailbox.com")  # doctest: +SKIP
    >>> mail.monitor(  # doctest: +SKIP
    >>>     conditions={"subject": "test",  # doctest: +SKIP
    >>>                 "sender": "chient@chat.com"},  # doctest: +SKIP
    >>>     to_path=Path("attachment"),   # doctest: +SKIP
    >>>     time_to_sleep=5  # doctest: +SKIP
    >>> )  # doctest: +SKIP

    If conditions is an empty dict, will save attachments of all incoming
    mails.

    Any email triggering the monitor will be marked as SEEN.

    Notes and warnings:

        1. Even though multiprocessing is used, any code written after the
        call to mail.monitor will not be executed until the monitoring ends.

        2. The file saving system tends to see mail signature as attachments,
        you will have to delete the files yourself, or ignore them in your
        analysis.
    """

    accepted_conditions = ["sender", "subject", "subject_exact"]
    instances = []
    default_mail = ""

    def __init__(
        self,
        username: str = None,
        token: str = None,
        port: int = 993,
        hostname: str = "outlook.office365.com",
        connect: bool = False,
        overwrite: bool = True,
        max_threads: int = None,
        send_errors_to: str = None

    ):

        if username is None:
            username = input("User name:\n")
        if token is None:
            token = getpass.getpass(f"Password for {username}:")
        if "@" not in username:
            username = f"{username}@{MailMonitor.default_mail}"

        self.send_errors_to = send_errors_to
        self.username = username
        self.token = token
        self.port = port
        self.hostname = hostname
        self.mailbox = None
        self.exit = False
        self.overwrite = overwrite
        self.max_threads = max_threads
        self.pool = None
        if connect:
            self.open_connection()
        MailMonitor.instances.append(self)

    def open_connection(self):
        """ """
        # Connection to the server
        talk = False
        if self.mailbox is None:
            logger.info(f"Connecting to {self.hostname} as {self.username}...")
            talk = True
        attempts = 0
        while True:
            attempts += 1
            try:
                self.mailbox = login(self.username, self.token, self.hostname, self.port)
                if talk:
                    logger.info("...successful")
                break
            except socket.gaierror as e:
                logger.info(f"Failed more than {attempts} times. Raising the exception.")
                if attempts > 60:
                    raise e
                else:
                    logger.info(f"Failed. Retrying for the {attempts}th time...")
                    sleep(1)

    @staticmethod
    def configure_date(d: Union[str, datetime]) -> str:
        """
        Converts datetime format to mail date format

        > https://datatracker.ietf.org/doc/html/rfc3501 page 84/85

        Parameters
        ----------
        d : Union[str, datetime]
            date to convert

        Returns
        -------
        str
            converted date
        """
        if isinstance(d, str):
            d = datetime.strptime(d, "%Y-%m-%d")
        m_dict = {
            "01": "Jan",
            "02": "Feb",
            "03": "Mar",
            "04": "Apr",
            "05": "May",
            "06": "Jun",
            "07": "Jul",
            "08": "Aug",
            "09": "Sep",
            "10": "Oct",
            "11": "Nov",
            "12": "Dec",
        }
        if len(str(d.month)) == 1:
            m = "0" + str(d.month)
        else:
            m = str(d.month)
        mv = m_dict[m]
        return str(d.day) + "-" + mv + "-" + str(d.year)

    @staticmethod
    def read_date(d: str) -> datetime.date:
        """
        convert date from mail format for datetime

        > https://datatracker.ietf.org/doc/html/rfc3501 page 84/85

        Parameters
        ----------
        d : str
            mail format

        Returns
        -------
        datetime.date
        """
        m_dict = {
            "01": "Jan",
            "02": "Feb",
            "03": "Mar",
            "04": "Apr",
            "05": "May",
            "06": "Jun",
            "07": "Jul",
            "08": "Aug",
            "09": "Sep",
            "10": "Oct",
            "11": "Nov",
            "12": "Dec",
        }
        day = d[:2]
        m_dict = {i: j for i, j in zip(m_dict.values(), m_dict.keys())}
        month = m_dict[d[3:6]]
        year = d[7:11]
        d = datetime.strptime(year + "-" + month + "-" + day, "%Y-%m-%d")
        return d.date()

    # noinspection PyUnresolvedReferences
    def monitor(
        self,
        conditions: Union[dict, List[dict]],
        to_path: Union[Union[TransparentPath, Path, str], List[Union[TransparentPath, Path, str]]],
        time_to_sleep: Union[int, List[int]] = 60,
        mailbox: Union[str, List[str]] = "INBOX",
        overwrite: Union[bool, List[bool]] = None,
        timeout: int = None,
    ) -> None:
        """

        Parameters
        ----------
        conditions: Union[dict, List[dict]]
            The list of patterns to match for the mail to trigger. The keys
            for the dicts are:

                1: subject : a substring that must be containd in the email
                subject.

                2: subject_exact : the exact expected subject.

                3: sender : the sender email adress.

        to_path: Union[Union[TransparentPath, Path, str], List[Union[TransparentPath, Path, str]]]
            Where to save the attatchment. If is not a list, will use the
            same path for all monitoring conditions.

        time_to_sleep: Union[int, List[int]]
            The time between two mailbox checks (Default value = 60). If is
            not a list, will use the same time for all monitoring conditions.

        mailbox: Union[str, List[str]]
            The mailbox to check. If is not a list, will use the same
            mailbox for all monitoring conditions. (Default value = "INBOX")

        overwrite: Union[bool, List[bool]]
            If True, will overwrite any file with the same name. Else rename it
            appending to now's datetime. (Default value = self.overwrite)

        timeout: int
            Time in seconds the monitor must remain up. None for infinite time (Default value = None)

        Returns
        -------
        None

        """

        if overwrite is None:
            overwrite = self.overwrite

        if not isinstance(conditions, list):
            conditions = [conditions]
        if not isinstance(to_path, list):
            to_path = [to_path] * len(conditions)
        if not isinstance(time_to_sleep, list):
            time_to_sleep = [time_to_sleep] * len(conditions)
        if not isinstance(mailbox, list):
            mailbox = [mailbox] * len(conditions)
        if not isinstance(overwrite, list):
            overwrite = [overwrite] * len(conditions)

        if not len(conditions) == len(to_path):
            raise ValueError("to_path and conditions must have same length")
        if not len(conditions) == len(time_to_sleep):
            raise ValueError("time_to_sleep and conditions must have same length")
        if not len(conditions) == len(mailbox):
            raise ValueError("mailbox and conditions must have same length")
        theargs = []
        for i in range(len(conditions)):
            theargs.append((conditions[i], to_path[i], time_to_sleep[i], mailbox[i], overwrite[i], timeout))

        logger.info("Will start monitoring for new emails. You can stop the monitoring at any moment by pressing "
                    "'CTRL+C'.")
        if timeout is not None:
            logger.info(f"Monitoring will remain up for {timeout} seconds then will shut down.")

        if self.pool is None:
            self.pool = ThreadPool(self.max_threads)
        self.pool.starmap(self._monitor, theargs)

    def stop_monitoring(self):
        if self.pool is None:
            return
        self.pool.close()
        self.pool.terminate()

    def fetch_one_mail(
        self,
        save_dir: Union[str, Path, TransparentPath],
        state: Optional[str] = "ALL",
        subject: Optional[str] = None,
        sender: Optional[str] = None,
        body: Optional[str] = None,
        date: Union[str, datetime, ddate, None] = None,
        mailbox: Union[str, List[str]] = "INBOX",
        modes: Dict[str, str] = None,
        expected_attachments: Union[int, bool] = True
    ) -> Union[bool, tuple]:
        if modes is None:
            modes = {"start": "exact", "end": "exact"}
        return self.fetch_mails(
            save_dir=save_dir,
            state=state,
            subject=subject,
            sender=sender,
            body=body,
            start_date=date,
            end_date=date,
            mailbox=mailbox,
            modes=modes,
            expected_attachments=expected_attachments
        )

    def fetch_attachment(self, uid: str) -> dict:
        """
        will fetch attachments for one mail

        Parameters
        ----------
        uid: str
            uid of mail

        Returns
        -------
        dict of file name : data as bytes
        """
        ret = {}
        for part in email.message_from_string(
            self.mailbox.uid("FETCH", uid, "(BODY.PEEK[])")[1][0][1].decode("ascii")
        ).walk():
            if part.get_content_maintype() != "multipart":
                name = part.get_filename()
                if name:
                    name = name.replace("\r", "").replace("\n", "")
                    data = part.get_payload(decode=True)
                    ret[name] = data
        return ret

    def fetch_mails(
        self,
        save_dir: Union[str, Path, TransparentPath],
        state: Optional[str] = "ALL",
        subject: Optional[str] = None,
        sender: Optional[str] = None,
        body: Optional[str] = None,
        start_date: Union[str, datetime, None] = None,
        end_date: Union[str, datetime, None] = None,
        mailbox: Union[str, List[str]] = "INBOX",
        modes: Dict[str, str] = None,
        duplicated: str = "last",
        expected_attachments: Union[int, bool] = True
    ):
        """
        Will fetch to attachments of mails based on the dates on arrival and the select modes

        Parameters
        ----------
        save_dir : Union[Union["TransparentPath", Path, str], List[Union["TransparentPath", Path, str]]]
        state : str = "ALL" (SEEN, UNSEEN, ALL)
        subject : Optional[str]
        sender : Optional[str]
        body : Optional[str]
        start_date : Optional[str, datetime]
        end_date : Optional[str, datetime]
        mailbox : Union[str, List[str]] = "INBOX"
        modes : Dict[str, str] = {"start": "exact", "end": "exact"}
            keys are 'start' and 'end', values can be 'exact', 'nearest', 'next', 'last'
        duplicated : str = "last" ("first", "last", "all")
            What to do if there are several mails the same day
        expected_attachments: Union[int, bool]
            Can be True to tell the function that it should raise an error if no attachment is found in the mail. Can
            also be an integer to tell the exact number of expected attachments (Default value = False)

        Returns
        -------
        tuple
            True and mails dates if successful else False, None
        """
        if modes is None:
            modes = {"start": "exact", "end": "exact"}
        modes = {k: modes[k] for k in modes if k in ("start", "end")}
        if "start" not in modes:
            modes["start"] = "exact"
        if "end" not in modes:
            modes["end"] = "exact"
        self.open_connection()
        self.mailbox.select(mailbox)
        base_req = ""
        if subject is not None:
            for i in split_spec_char(subject):
                base_req += f'SUBJECT "{i}" '
        if sender is not None:
            base_req += f"FROM {sender} "
        if body is not None:
            base_req += f"BODY {body} "
        if state != "ALL":
            base_req += f"({state}) "
        if start_date is None and end_date is None:
            base_req += f"ON {self.configure_date(datetime.now())} "
        elif start_date is not None and end_date is not None:
            start_date_s = self.configure_date(start_date)
            end_date_s = self.configure_date(end_date)
            if end_date_s == start_date_s:
                base_req += f"ON {start_date_s} "
            else:
                base_req += f"SINCE {start_date_s} "
                base_req += f"BEFORE {end_date_s} "
        elif start_date is not None:
            base_req += f"SINCE {self.configure_date(start_date)} "
        elif end_date is not None:
            base_req += f"BEFORE {self.configure_date(end_date)} "
        if base_req.endswith(" "):
            base_req = base_req[:-1]
        uids = self.mailbox.uid("SEARCH", None, base_req)[1]
        uids = list(map(lambda x: str(x)[2:-1], uids))
        uids = uids[0].split(" ")
        if uids[0] == "":
            return False, None
        dict_date = self.list_dates(uids, invert=True)
        dates = list(dict_date.keys())

        def get_date(d_, m_, default):
            if m_ == "exact" and d_ is not None:
                selected_ = dict_date.get(d_, None)
                if selected_ is None:
                    return False, None
                else:
                    selected_ = d_
            # TODO (Aducourthial): add time sensitivity
            elif m_ == "next" and d_ is not None:
                selected_ = (lambda x, y: min(x, key=lambda d: abs(d - y) if d < y else np.inf))(dates, d_)
            elif m_ == "last" and d_ is not None:
                selected_ = (lambda x, y: min(x, key=lambda d: abs(d - y) if d > y else np.inf))(dates, d_)
            elif m_ == "nearest" and d_ is not None:
                selected_ = (lambda x, y: min(x, key=lambda d: abs(d - y)))(dates, d_)
            elif d_ is not None:
                raise ValueError(f"Invalid mode {m_}")
            else:
                selected_ = dict_date.get(default, None)
                if selected_ is None:
                    return False, None
                else:
                    selected_ = d_
            return selected_

        best_start_date = get_date(start_date, modes["start"], dates[-1])
        best_end_date = get_date(end_date, modes["end"], dates[0])
        good_dates = [d for d in dates if (d >= best_start_date) and (d <= best_end_date)]
        good_dates.sort()

        if not isinstance(save_dir, TransparentPath):
            bp = TransparentPath(save_dir)
        else:
            bp = save_dir
        if not bp.exists():
            bp.mkdir()

        def save_one(path, uid_):
            if not path.exists():
                path.mkdir()
            attachments = 0
            for i_, j_ in self.fetch_attachment(uid_).items():
                (path / i_).write_bytes(j_)
                attachments += 1

            if isinstance(expected_attachments, bool):
                if expected_attachments is True and attachments == 0:
                    logger.warning("Expected attachments in the mail, but found none.")
                    return False, None
            elif isinstance(expected_attachments, int) and attachments != expected_attachments:
                logger.warning(f"Expected {expected_attachments} attachments in the mail, but found {attachments}.")
                return False, None

        for d in good_dates:
            if len(dict_date[d]) > 1:
                if duplicated == "last":
                    uid = [dict_date[d][-1]]
                elif duplicated == "first":
                    uid = [dict_date[d][0]]
                else:
                    uid = [dict_date[d]]
            else:
                uid = [dict_date[d][0]]

            bps = bp
            if len(good_dates) > 1:
                logger.info(f"Found {len(uid)} mail(s) on {d}")
                bps = bp / d.strftime('%Y-%m-%d')
            if len(uid) > 1:
                for i in range(len(uid)):
                    save_one(bps.append(f"_{i}"), uid[i])
            else:
                save_one(bps, uid[0])
        return True, good_dates

    def list_dates(self, uids: list, invert: bool = False):
        """
        fetch intenal dates of list of uid
        base > {uid : date}
        inverted > {date : uids}

        Parameters
        ----------
        uids: list
        invert : bool
                invert dict

        Returns
        -------
        dict
        """

        if not isinstance(uids, list):
            uids = [uids]

        ret = {}
        for uid in uids:
            msg = self.mailbox.uid("FETCH", uid, "INTERNALDATE")
            ret[uid] = self.read_date(msg[1][0].decode().split('"')[-2][:11])
        if invert:
            bi = ret.copy()
            ret = {}
            for i, j in bi.items():
                if j not in ret.keys():
                    ret[j] = [i]
                else:
                    ret[j].append(i)
        return ret

    # noinspection PyUnresolvedReferences
    def _monitor(
        self,
        conditions: dict,
        to_path: Union["TransparentPath", Path, str],
        time_to_sleep: int = 60,
        mailbox: str = "INBOX",
        overwrite: bool = None,
        timeout: int = None,
    ) -> None:
        """

        Parameters
        ----------
        conditions: dict
            The patterns to match for the mail to trigger. The keys are:

                1: subject : a substring that must be containd in the email
                subject.

                2: subject_exact : the exact expected subject.

                3: sender : the sender email adress.

        to_path: Union[TransparentPath, Path, str]

        time_to_sleep: int
             The time between two mailbox checks (Default value = 60)

        mailbox: str
             The mailbox to check (Default value = "INBOX")

        timeout: int
            Time in seconds the monitor must remain up. None for infinite time (Default value = None)

        Returns
        -------
        None

        """

        if overwrite is None:
            overwrite = self.overwrite

        s = (
            f"Checking {mailbox} of {self.username} each {time_to_sleep} "
            f"seconds for new emails matching the conditions:\n"
        )
        for condition in conditions:
            if condition not in MailMonitor.accepted_conditions:
                raise KeyError(f"Condition {condition} not valid")
            s += f"  - '{condition}' = {conditions[condition]}\n"
        s += f"Will save the attachment in {to_path}"
        logger.info(s)

        def the_while(shelf: MailMonitor, t: int):
            t0 = time()
            while True:
                if shelf.exit:
                    break
                shelf.open_connection()
                shelf.mailbox.select(mailbox)
                cond = ""
                if "subject" in conditions:
                    matches = split_spec_char(conditions["subject"])
                    for m in matches:
                        cond = f'{cond}SUBJECT "{m}" '
                if "sender" in conditions:
                    cond = f'{cond}FROM "{conditions["sender"]}" '
                if len(cond) == 0:
                    raise ValueError("No filtering conditions specified")

                cond = f"{cond}(UNSEEN)"
                uids = shelf.mailbox.uid("SEARCH", None, cond)[1][0].split()
                for uid in uids:
                    try:
                        typ, msg_data = shelf.mailbox.uid("FETCH", uid, "(BODY.PEEK[])")
                    except ConnectionResetError:
                        break
                    if typ == "NO":
                        raise MailException(msg_data[0])
                    email_body = ""
                    if msg_data[0] is not None:
                        # noinspection PyUnresolvedReferences
                        email_body = msg_data[0][1]
                    else:
                        logger.warning("Triggered on an empty mail?!")
                    encoding = chardet.detect(email_body)["encoding"]
                    email_body = email_body.decode(encoding)
                    mail = email.message_from_string(email_body)

                    logger.info(
                        f"Triggered at {get_datetime_now()} on mail "
                        f"subject '{mail['Subject']}'"
                        f" from '{mail['From']}'"
                    )
                    for part in mail.walk():
                        save_attachment(part, to_path, overwrite)
                    _, _ = shelf.mailbox.uid("FETCH", uid, "(RFC822)")
                    logger.info("Finished reading the mail")
                if not shelf.mailbox.state == "LOGOUT":
                    shelf.mailbox.select()
                    shelf.mailbox.close()
                    shelf.mailbox.logout()
                # Verification toutes les x secondes
                sleep(time_to_sleep)
                if t is not None and time() - t0 > t:
                    logger.info(f"Requested run time of {t} completed. Exiting...")
                    break

        the_while(self, timeout)

    def send(self, msg, to: str = None):
        attempts = 0
        while attempts < 2:
            # noinspection PyBroadException
            try:
                mailsender = MailSender(sender=self.username, passwd=self.token)
                if to is None:
                    mailsender.send_mail(
                        adresses=self.username, subject="MailMonitoring ended with Exception", text=msg
                    )
                    logger.info(f"Sent warning message to {self.username}")
                else:
                    mailsender.send_mail(adresses=to, subject="MailMonitoring ended with Exception", text=msg)
                    logger.info(f"Sent warning message to {to}")
                break
            except self.mailbox.abort:
                logger.warning("imaplib.abort exception raised. Attempting to reconnect.")
                self.mailbox = login(self.username, self.token, self.hostname, self.port)
                attempts += 1


_excepthook = getattr(sys, "excepthook")


# noinspection PyBroadException
@atexit.register
def clean():
    for mm in MailMonitor.instances:
        try:
            if mm.mailbox is not None and not mm.mailbox.state == "LOGOUT":
                mm.mailbox.select()
                mm.mailbox.close()
                mm.mailbox.logout()
        except Exception as e:
            logger.warning("Failed to close the mailbox:")
            logger.warning(e)
        mm.stop_monitoring()
    del MailMonitor.instances


def overload_raise(ex, val, tb):
    if ex != KeyboardInterrupt:
        li = traceback.format_exception(ex, val, tb)
        to_send = "".join(li)
        for mm in MailMonitor.instances:
            mm.send(to_send, to=mm.send_errors_to)
        _excepthook(ex, val, tb)
    else:
        sys.exit(0)


setattr(sys, "excepthook", overload_raise)
