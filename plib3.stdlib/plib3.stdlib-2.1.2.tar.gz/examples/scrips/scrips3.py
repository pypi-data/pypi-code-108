#!/usr/bin/env python3
"""
SCRIPS.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

Script to keep track of prescription refill dates
and send e-mail notifications. Intended to be run
stand-alone as a daily cron job, or to be imported
by scrips-edit.py for editing of the scrips.dat file.
"""

import os
import ast
import datetime

from plib.stdlib.ini import PIniFile
from plib.stdlib.coll import typed_namedsequence
from plib.stdlib.strings import strtodate, strtobool

scrips_dirname = ".scrips"
scrips_dat_name = "scrips.dat"


# This is dynamic so changing the above globals will change the
# file name retrieved at run time

def scrips_dat_file():
    # First make sure the directory exists (this will allow the
    # file to be created if it doesn't exist)
    dirname = os.path.realpath(os.path.expanduser(os.path.join(
        "~", scrips_dirname
    )))
    if not os.path.isdir(dirname):
        os.mkdir(dirname)
    return os.path.join(dirname, scrips_dat_name)


TMPL = "Rx #{} for {}: last filled on {} for {} days, {} refills remaining{}."


def smart_date(s):
    if isinstance(s, str):
        return strtodate(s)
    if not isinstance(s, datetime.date):
        raise TypeError("Object cannot be converted to datetime: {}".format(repr(s)))
    return s


def smart_bool(s):
    if isinstance(s, str):
        return strtobool(s)
    return bool(s)


_ScripBase = typed_namedsequence('_ScripBase', [
    ('name', str),
    ('rxnum', str),
    ('filldate', smart_date),
    ('days', int),
    ('refills', int),
    ('submitted', smart_bool)
])


class Scrip(_ScripBase):
    
    turnaround = 5  # lead time for normal refills
    leadtime = 5  # additional time if scrip must be renewed
    
    def duedate(self):
        d = self.days - self.turnaround
        if self.refills < 1:
            d = d - self.leadtime
        return (self.filldate + datetime.timedelta(d))
    
    def due(self):
        return (self.filldate.today() >= self.duedate())
    
    def _duestr(self):
        if self.due():
            if self.submitted:
                return "; Submitted for refill"
            else:
                return "; DUE FOR REFILL"
        else:
            return ""
    
    def __str__(self, tmpl=TMPL):
        return tmpl.format(
            self.rxnum, self.name,
            str(self.filldate), str(self.days), str(self.refills),
            self._duestr()
        )


def scriplist(scripclass=Scrip):
    result = []
    fname = scrips_dat_file()
    if os.path.isfile(fname):
        with open(fname, 'r') as f:
            for line in f:
                if line[0] != '#':
                    result.append(scripclass(*line.split()))
    return result


username = os.getenv('USER')
if not username:
    username = os.getenv('USERNAME')
useraddr = "{}@localhost".format(username)

inifile = PIniFile("scrips", [
    ("email", [
        ('fromaddr', useraddr),
        ('toaddr', useraddr),
        ('typestr', "text/plain"),
        ('charsetstr', "us-ascii"),
        ('serverstr', "localhost"),
        ('portnum', 25),
        ('username', ""),
        ('password', "")
    ]),
    ("headers", [("dict", str, "{}")]),
    ("pharmacy", [("name", str, "Pharmacy")])
])


if __name__ == "__main__":
    from plib.stdlib.options import parse_options
    
    optlist = (
        ("-d", "--display-only", {
            'action': "store_true",
            'dest': "silent", 'default': False,
            'help': "just display scrip status (overrides --notify)"
        }),
        ("-n", "--notify", {
            'action': "store_true",
            'dest': "notify", 'default': False,
            'help': "send notification e-mail if scrip is due (default)"
        }),
        ("-q", "--quiet", {
            'action': "store_false",
            'dest': "verbose", 'default': True,
            'help': "suppress verbose output"
        }),
        ("-t", "--test", {
            'action': "store_true",
            'dest': "testmode",
            'help': "send a test e-mail to verify settings"
        })
    )
    opts, args = parse_options(optlist)
    
    if opts.silent:
        
        if opts.testmode:
            print("To test email settings, don't use the --silent option!")
        
        else:
            print("Display-only mode; will not send notification e-mail.")
            
            
            def do_scrip(s):
                print(s)
    
    
    else:
        from plib.stdlib.mail import sendmail
        
        def scripsmail(subj, msg):
            sendmail(
                inifile.email_fromaddr,
                inifile.email_toaddr,
                subj,
                msg,
                # Use literal_eval here for safety
                headers=ast.literal_eval(inifile.headers_dict),
                mimetype=inifile.email_typestr,
                charset=inifile.email_charsetstr,
                server=inifile.email_serverstr,
                portnum=int(inifile.email_portnum),
                username=inifile.email_username,
                password=inifile.email_password,
                verbose=opts.verbose
            )
        
        if opts.testmode:
            if opts.notify:
                print("To test email settings, don't use the --notify option!")
            
            else:
                scripsmail(
                    "scrips test email",
                    "Test email to verify scrips mail settings."
                )
        
        else:
            def mailstr(s):
                return (
                    "Rx #{} for {} is due for refill as of {} from {}.".format(
                    s.rxnum, s.name, str(s.duedate()), inifile.pharmacy_name)
                )
            
            def mailsubjstr(s):
                return "Rx reminder for {}".format(s.name)
            
            def do_scrip(s):
                print(s)
                if s.due() and not s.submitted:
                    scripsmail(
                        mailsubjstr(s),
                        mailstr(s)
                    )
    
    if not opts.testmode:
        for s in scriplist():
            do_scrip(s)
