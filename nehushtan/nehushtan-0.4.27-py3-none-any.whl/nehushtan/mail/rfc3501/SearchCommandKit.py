import time


class SearchCommandKit:
    """
    See https://datatracker.ietf.org/doc/html/rfc3501#section-6.4.4

    Since 0.4.6
    """

    def __init__(self, charset: str = None):
        self.__charset = charset
        self.__arguments = []
        if self.__charset is not None:
            self.__arguments.append('CHARSET')
            self.__arguments.append(self.__charset)

        self.__conditions = []

        self.__last_literal = None

    def get_charset(self):
        return self.__charset

    @staticmethod
    def formatted_date_from_time(x: float):
        """
        `x` might be get by `time.time()` and along with operations
        result would be `1-Jul-2021` alike
        """
        return time.strftime("%d-%b-%Y", time.localtime(x))

    def append_all(self):
        """
        All messages in the mailbox; the default initial key for ANDing.
        """
        self.__conditions.append('ALL')
        return self

    def append_answered(self):
        """
        Messages with the `\Answered` flag set.
        """
        self.__conditions.append('ANSWERED')
        return self

    def append_deleted(self):
        """
        Messages with the `\DELETED` flag set.
        """
        self.__conditions.append('DELETED')
        return self

    def append_draft(self):
        """
        Messages with the `\DRAFT` flag set.
        """
        self.__conditions.append('DRAFT')
        return self

    def append_flagged(self):
        """
        Messages with the `\FLAGGED` flag set.
        """
        self.__conditions.append('FLAGGED')
        return self

    def append_recent(self):
        """
        Messages with the `\RECENT` flag set.
        """
        self.__conditions.append('RECENT')
        return self

    def append_seen(self):
        """
        Messages with the `\SEEN` flag set.
        """
        self.__conditions.append('SEEN')
        return self

    def append_unanswered(self):
        """
        Messages that do not have the \Answered flag set.
        """
        self.__conditions.append('UNANSWERED')
        return self

    def append_undeleted(self):
        """
        Messages that do not have the \Deleted flag set.
        """
        self.__conditions.append('UNDELETED')
        return self

    def append_undraft(self):
        """
        Messages that do not have the \Draft flag set.
        """
        self.__conditions.append('UNDRAFT')
        return self

    def append_unflagged(self):
        """
        Messages that do not have the \Flagged flag set.
        """
        self.__conditions.append('UNFLAGGED')
        return self

    def append_unseen(self):
        """
        Messages that do not have the \Seen flag set.
        """
        self.__conditions.append('UNSEEN')
        return self

    def append_bcc(self, value: str):
        """
        Messages that contain the specified string in the envelope structure's BCC field.
        """
        self.__conditions.append(['BCC', value])
        return self

    def append_cc(self, value: str):
        """
        Messages that contain the specified string in the envelope structure's CC field.
        """
        self.__conditions.append(['CC', value])
        return self

    def append_from(self, value: str):
        """
        Messages that contain the specified string in the envelope structure's FROM field.
        """
        self.__conditions.append(['FROM', value])
        return self

    def append_to(self, value: str):
        """
        Messages that contain the specified string in the envelope structure's TO field.
        """
        self.__conditions.append(['TO', value])
        return self

    def append_before(self, before_date: str):
        """
        Messages whose internal date (disregarding time and timezone) is earlier than the specified date.
        """
        self.__conditions.append(['BEFORE', before_date])
        return self

    def append_on(self, on_date: str):
        """
        Messages whose internal date (disregarding time and timezone) is within the specified date.
        """
        self.__conditions.append(['ON', on_date])
        return self

    def append_since(self, since_date: str):
        """
        Messages whose internal date (disregarding time and timezone) is within or later than the specified date.
        """
        self.__conditions.append(['SINCE', since_date])
        return self

    def append_sent_before(self, before_date: str):
        """
        Messages whose [RFC-2822] Date: header (disregarding time and timezone) is earlier than the specified date.
        """
        self.__conditions.append(['SENTBEFORE', before_date])
        return self

    def append_sent_on(self, on_date: str):
        """
        Messages whose [RFC-2822] Date: header (disregarding time and timezone) is within the specified date.
        """
        self.__conditions.append(['SENTON', on_date])
        return self

    def append_sent_since(self, since_date: str):
        """
        Messages whose [RFC-2822] Date: header (disregarding time and timezone) is within the specified date.
        """
        self.__conditions.append(['SENTSINCE', since_date])
        return self

    def append_body_keyword(self, keyword: str):
        """
        Messages that contain the specified string in the body of the message.
        """
        self.__conditions.append(['BODY', keyword])
        return self

    def append_header_key_value(self, name: str, keyword: str):
        """
        Messages that have a header with the specified field-name (as defined in [RFC-2822])
            and that contains the specified string in the text of the header (what comes after the colon).
        If the string to search is zero-length,
            this matches all messages
            that have a header line with the specified field-name regardless of the contents.
        """
        self.__conditions.append(['HEADER', name, keyword])
        return self

    def append_flag_keyword(self, flag: str):
        """
        Messages with the specified keyword flag set.
        """
        self.__conditions.append(['KEYWORD', flag])
        return self

    def append_no_flag_keyword(self, flag: str):
        """
        Messages that do not have the specified keyword flag set.
        """
        self.__conditions.append(['UNKEYWORD', flag])
        return self

    def append_larger(self, octet_size: int):
        """
        Messages with an [RFC-2822] size larger than the specified number of octets.
        """
        self.__conditions.append(['LARGER', f'{octet_size}'])
        return self

    def append_smaller(self, octet_size: int):
        """
        Messages with an [RFC-2822] size smaller than the specified number of octets.
        """
        self.__conditions.append(['SMALLER', f'{octet_size}'])
        return self

    def append_new(self):
        """
        Messages that have the \Recent flag set but not the \Seen flag.
        This is functionally equivalent to "(RECENT UNSEEN)".
        """
        self.__conditions.append('NEW')
        return self

    def append_not_key(self, keyword: str):
        """
        Messages that do not match the specified search key.
        """
        self.__conditions.append(['NOT', keyword])
        return self

    def append_old(self):
        """
        Messages that do not have the \Recent flag set.
        This is functionally equivalent to "NOT RECENT" (as opposed to "NOT NEW").
        """
        self.__conditions.append('OLD')
        return self

    def append_or(self, v1: str, v2: str):
        """
        Messages that match either search key.
        """
        self.__conditions.append(['OR', v1, v2])
        return self

    def append_subject(self, keyword: str):
        """
        Messages that contain the specified string in the envelope structure's SUBJECT field.
        """
        self.__conditions.append(['SUBJECT', keyword])
        return self

    def append_text(self, keyword: str):
        """
        Messages that contain the specified string in the header or body of the message.
        """
        self.__conditions.append(['TEXT', keyword])
        return self

    def append_uid(self, uid: str):
        """
        Messages with unique identifiers corresponding to the specified unique identifier set.
        Sequence set ranges are permitted.
        """
        self.__conditions.append(['UID', uid])
        return self

    def build(self):
        t = []
        for x in self.__arguments:
            t.append(x)
        for condition in self.__conditions:
            if type(condition) is str:
                t.append(condition)
            elif type(condition) is list:
                for c in condition:
                    t.append(c)
                if condition[0] == 'SUBJECT' or condition[0] == 'TEXT':
                    self.__last_literal = condition[-1]
                    if self.__charset is not None:
                        self.__last_literal = self.__last_literal.encode(self.__charset)
                    t = t[:-1]
        return 'SEARCH', t, self.__last_literal
