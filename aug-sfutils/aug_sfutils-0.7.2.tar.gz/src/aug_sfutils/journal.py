#-------------------------------------------------------------------------------
# journal: Module to query the AUG journal
#
# History:
#
#    30.11.2016 jcf
#    15.10.2021 git   made py3 compatible, few auxiliary modules
#-----------------------------------------------------------------------------

import os, logging, datetime
import ctypes as ct
from aug_sfutils import str_byt, getlastshot, sfread

logger = logging.getLogger('aug_sfutils.journal')

# Select the correct library

libjouso = '/afs/ipp/aug-ads/diags/@sys/lib64/libjournal.so'
if not os.path.isfile(libjouso):
    libjouso = '/afs/ipp-garching.mpg.de/aug/ads-diags/amd64_sles15/lib64/libjournal.so'
libjournal   = ct.cdll.LoadLibrary(libjouso)

date_fmt = '%Y-%m-%d'


def getdict(struct):
    return dict((field, getattr(struct, field)) for field, _ in struct._fields_)


def anyshot():

    nshot = getlastshot.getlastshot()
    date_fmt = '%d%b%Y'
    today = datetime.datetime.now().strftime(date_fmt)
    date_last = 'No date'
    jou = sfread.SFREAD(nshot, 'JOU')
    if jou.status:
        date_last = jou.time.strftime(date_fmt)
    logger.info('Today is %s', today) 
    logger.info('Last shot %d on %s', nshot, date_last) 

    return(today == date_last)


class jouEntry(ct.Structure):
    """
    Class defining the ctypes structure for a full journal entry
    """
    _fields_ = [\
        ("shotno",    ct.c_int),
        ("program",   ct.c_char_p),
        ("clearance", ct.c_char_p),
        ("datum",     ct.c_char_p),
        ("time",      ct.c_char_p),
        ("leader",    ct.c_char_p),
        ("konf_il",   ct.c_char_p),
        ("konf_al",   ct.c_char_p),
        ("konf_snu",  ct.c_char_p),
        ("konf_sno",  ct.c_char_p),
        ("konf_dn",   ct.c_char_p),
        ("typ",       ct.c_char_p),
        ("useful",    ct.c_char_p),
        ("b_hmod",    ct.c_char_p),
        ("b_lmod",    ct.c_char_p),
        ("b_imprh",   ct.c_char_p),
        ("b_itb",     ct.c_char_p),
        ("b_blim",    ct.c_char_p),
        ("b_dlim",    ct.c_char_p),
        ("b_disb",    ct.c_char_p),
        ("b_disr",    ct.c_char_p),
        ("b_dise",    ct.c_char_p),
        ("b_vdeo",    ct.c_char_p),
        ("b_vdeu",    ct.c_char_p),
        ("b_nobd",    ct.c_char_p),
        ("b_res",     ct.c_char_p),
        ("b_fail",    ct.c_char_p),
        ("b_stable",  ct.c_char_p),
        ("b_sweep",   ct.c_char_p),
        ("b_cdh",     ct.c_char_p),
        ("b_run",     ct.c_char_p),
        ("vessel",    ct.c_char_p),
        ("coat",      ct.c_char_p),
        ("coatdate",  ct.c_char_p),
        ("proposal",  ct.c_char_p),
        ("yag",       ct.c_char_p),
        ("lagereg",   ct.c_char_p),
        ("lagecom1",  ct.c_char_p),
        ("lagecom2",  ct.c_char_p),
        ("formreg",   ct.c_char_p),
        ("formcom1",  ct.c_char_p),
        ("formcom2",  ct.c_char_p),
        ("remarks",   ct.c_char_p),
        ("flatb",     ct.c_double),
        ("flate",     ct.c_double),
        ("flatm",     ct.c_char_p),
        ("ip",        ct.c_double),
        ("ne",        ct.c_double),
        ("nediag",    ct.c_char_p),
        ("bt",        ct.c_double),
        ("q95",       ct.c_double),
        ("kappa",     ct.c_double),
        ("delrob",    ct.c_double),
        ("delrunt",   ct.c_double),
        ("disr",      ct.c_double),
        ("killergas", ct.c_char_p),
        ("impspez",   ct.c_char_p),
        ("imptime",   ct.c_double),
        ("neutr",     ct.c_double),
        ("kryop",     ct.c_char_p),
        ("glowtime",  ct.c_double),
        ("ioh",       ct.c_double),
        ("roh",       ct.c_double),
        ("gas_h",     ct.c_char_p),
        ("gas_d",     ct.c_char_p),
        ("gas_he",    ct.c_char_p),
        ("gas_ne",    ct.c_char_p),
        ("gas_ar",    ct.c_char_p),
        ("gas_n2",    ct.c_char_p),
        ("gas_kr",    ct.c_char_p),
        ("gas_xe",    ct.c_char_p),
        ("gas_cd4",   ct.c_char_p),
        ("gas_other", ct.c_char_p),
        ("valve_1",   ct.c_char_p),
        ("valve_2",   ct.c_char_p),
        ("valve_3",   ct.c_char_p),
        ("valve_4",   ct.c_char_p),
        ("valve_5",   ct.c_char_p),
        ("valve_6",   ct.c_char_p),
        ("valve_7",   ct.c_char_p),
        ("valve_8",   ct.c_char_p),
        ("valve_9",   ct.c_char_p),
        ("valve_10",  ct.c_char_p),
        ("valve_11",  ct.c_char_p),
        ("valve_12",  ct.c_char_p),
        ("valve_13",  ct.c_char_p),
        ("valve_14",  ct.c_char_p),
        ("valve_15",  ct.c_char_p),
        ("valve_16",  ct.c_char_p),
        ("valve_17",  ct.c_char_p),
        ("valve_18",  ct.c_char_p),
        ("valve_19",  ct.c_char_p),
        ("valve_20",  ct.c_char_p),
        ("valve_21",  ct.c_char_p),
        ("valve_22",  ct.c_char_p),
        ("erstfh",    ct.c_double),
        ("erstfb",    ct.c_double),
        ("erstfg",    ct.c_char_p),
        ("gasvalv",   ct.c_char_p),
        ("nbi1l",     ct.c_double),
        ("nbi1sp",    ct.c_double),
        ("nbi1g",     ct.c_char_p),
        ("nbi1b",     ct.c_double),
        ("nbi1e",     ct.c_double),
        ("nbi2l",     ct.c_double),
        ("nbi2sp",    ct.c_double),
        ("nbi2g",     ct.c_char_p),
        ("nbi2b",     ct.c_double),
        ("nbi2e",     ct.c_double),
        ("nbi3l",     ct.c_double),
        ("nbi3sp",    ct.c_double),
        ("nbi3g",     ct.c_char_p),
        ("nbi3b",     ct.c_double),
        ("nbi3e",     ct.c_double),
        ("nbi4l",     ct.c_double),
        ("nbi4sp",    ct.c_double),
        ("nbi4g",     ct.c_char_p),
        ("nbi4b",     ct.c_double),
        ("nbi4e",     ct.c_double),
        ("nbi5l",     ct.c_double),
        ("nbi5sp",    ct.c_double),
        ("nbi5g",     ct.c_char_p),
        ("nbi5b",     ct.c_double),
        ("nbi5e",     ct.c_double),
        ("nbi6l",     ct.c_double),
        ("nbi6sp",    ct.c_double),
        ("nbi6g",     ct.c_char_p),
        ("nbi6b",     ct.c_double),
        ("nbi6e",     ct.c_double),
        ("nbi7l",     ct.c_double),
        ("nbi7sp",    ct.c_double),
        ("nbi7g",     ct.c_char_p),
        ("nbi7b",     ct.c_double),
        ("nbi7e",     ct.c_double),
        ("nbi8l",     ct.c_double),
        ("nbi8sp",    ct.c_double),
        ("nbi8g",     ct.c_char_p),
        ("nbi8b",     ct.c_double),
        ("nbi8e",     ct.c_double),
        ("ecrh1l",    ct.c_double),
        ("ecrh1f",    ct.c_double),
        ("e1m",       ct.c_char_p),
        ("ecrh1b",    ct.c_double),
        ("ecrh1e",    ct.c_double),
        ("ecrh2l",    ct.c_double),
        ("ecrh2f",    ct.c_double),
        ("e2m",       ct.c_char_p),
        ("ecrh2b",    ct.c_double),
        ("ecrh2e",    ct.c_double),
        ("ecrh3l",    ct.c_double),
        ("ecrh3f",    ct.c_double),
        ("e3m",       ct.c_char_p),
        ("ecrh3b",    ct.c_double),
        ("ecrh3e",    ct.c_double),
        ("ecrh4l",    ct.c_double),
        ("ecrh4f",    ct.c_double),
        ("e4m",       ct.c_char_p),
        ("ecrh4b",    ct.c_double),
        ("ecrh4e",    ct.c_double),
        ("ecrh5l",    ct.c_double),
        ("ecrh5f",    ct.c_double),
        ("e5m",       ct.c_char_p),
        ("ecrh5b",    ct.c_double),
        ("ecrh5e",    ct.c_double),
        ("ecrh6l",    ct.c_double),
        ("ecrh6f",    ct.c_double),
        ("e6m",       ct.c_char_p),
        ("ecrh6b",    ct.c_double),
        ("ecrh6e",    ct.c_double),
        ("ecrh7l",    ct.c_double),
        ("ecrh7f",    ct.c_double),
        ("e7m",       ct.c_char_p),
        ("ecrh7b",    ct.c_double),
        ("ecrh7e",    ct.c_double),
        ("ecrh8l",    ct.c_double),
        ("ecrh8f",    ct.c_double),
        ("e8m",       ct.c_char_p),
        ("ecrh8b",    ct.c_double),
        ("ecrh8e",    ct.c_double),
        ("icrh1l",    ct.c_double),
        ("icrh1f",    ct.c_double),
        ("i1m",       ct.c_char_p),
        ("icrh1b",    ct.c_double),
        ("icrh1e",    ct.c_double),
        ("icrh2l",    ct.c_double),
        ("icrh2f",    ct.c_double),
        ("i2m",       ct.c_char_p),
        ("icrh2b",    ct.c_double),
        ("icrh2e",    ct.c_double),
        ("icrh3l",    ct.c_double),
        ("icrh3f",    ct.c_double),
        ("i3m",       ct.c_char_p),
        ("icrh3b",    ct.c_double),
        ("icrh3e",    ct.c_double),
        ("icrh4l",    ct.c_double),
        ("icrh4f",    ct.c_double),
        ("i4m",       ct.c_char_p),
        ("icrh4b",    ct.c_double),
        ("icrh4e",    ct.c_double),
        ("nbi4m",     ct.c_double),
        ("icrh4m",    ct.c_double),
        ("ecrh4m",    ct.c_double),
        ("nbb1b",     ct.c_double),
        ("nbb1e",     ct.c_double),
        ("pheattot",  ct.c_double),
        ("status",    ct.c_char_p),
        ("notice",    ct.c_char_p),
        ("upddate",   ct.c_char_p),
        ("cryoreg",   ct.c_char_p),
        ("programdir",ct.c_char_p),
        ("crossval",  ct.c_char_p),
        ("crosstyp",  ct.c_char_p),
        ("recipe",    ct.c_char_p),
        ("saddlecr",  ct.c_int),
        ("saddleip",  ct.c_double),
        ("saddleci",  ct.c_double),
           ]


def journalSearch(SQLquery, onlyUseful=1, shotRange= [0, 0]):
    """Search entries in the logbook

    Syntax:

    sf.journalSearch(SQLquery, [Options])

    Arguments and Options:
       SQLquery               string    Query in SQL syntax (required)
       onlyUseful=0|1         int       Flag, if only useful plasmashots ar te be searched (default: yes)
       shotRange=[low, high]  [int,int] Only search within this shot range

    Returns:
           array of dictionary of shot entries (or None)
    """

# Check Arguments

    assert isinstance(SQLquery, str),  'SQLquery: string expected'

    if onlyUseful is not None:
        assert isinstance(onlyUseful, int), 'onlyUseful: int expected'
        libjournal.jouSetOnlyUseful(ct.c_int(onlyUseful))

    if shotRange is not None:
        libjournal.jouSetShotRange(shotRange[0], shotRange[1])

# Search

    nResults = ct.c_int(0)
    rc = libjournal.jouSearch(SQLquery, ct.byref(nResults))
    if rc or nResults == 0:
        return

    entries = (jouEntry * nResults.value)()
    rc = libjournal.jouFetchEntries(ct.byref(entries))

    pyEntries = [getdict(entries[i]) for i in range(nResults.value)]
    return pyEntries


def setShotRange(shot1, shot2):
    """Set the shot range for the following searches

    Syntax:

    sf.setShotRange(shot1, shot2)

    Arguments:
    shot1    int  lower bound (0 means unset)
    shot2    int  upper bound (0 means unset)

    Returns:
    nothing
    """

# Check arguments

    assert isinstance(shot1, int), 'shot1: int expected'
    assert isinstance(shot2, int), 'shot1: int expected'

# Set

    libjournal.jouSetShotRange(shot1, shot2)


def setOnlyUseful(flag):
    """Set the flag, if only useful plasma discharges should be searched for

    Syntax:

    sf.setOnlyUseful(flag)

    Arguments:
    flag    int  (0 or 1)

    Returns:
    nothing
    """

# Check arguments

    assert isinstance(flag, int), 'flag: int expected'

# Set

    libjournal.jouSetOnlyUseful(flag)


def getNResults():
    """Get the number of results from the previous search

    Syntax:

    sf.getNResults

    Returns:
    number of results
    """

    n = libjournal.jouGetNResults()
    return n


def getEntryForShot(shot):
    """Get the parameters for one shot

    Syntax:

    sf.getEntryForShot(shot)

    Returns:
    Directory with parameters
    """

# Check arguments

    assert isinstance(shot, int), 'shot: int expected'

# Get 

    entry = (jouEntry)()
    rc = libjournal.jouGetEntryForShot(shot, ct.byref(entry))

    return getdict(entry)


def searchSession(date=None, fmt=None, onlyUseful=1):
    """Get parameters for one session

    Syntax:

    sf.searchSession( date='', [OPTIONS] )

    Arguments and Options:

    date            str   Date of the session
    fmt=format      str   Format of the date string (default: YYYY-MM-DD)
    onlyUseful=0|1  int   Flag, if only useful plasmashots ar te be searched (default: yes)

    Returns:
        array of dictionary of shot entries (or None)
    """

# Check arguments

    date, fmt = checkDateFmt(date, fmt)

    if onlyUseful is not None:
        assert isinstance(onlyUseful, int), 'onlyUseful: int expected'
        libjournal.jouSetOnlyUseful(ct.c_int(onlyUseful))

# Get 

    rc = libjournal.jouSearchSession(date, fmt)
    if rc:
        return None

    nResults = libjournal.jouGetNResults()
    if nResults == 0:
        return None

    entries = (jouEntry * nResults)();
    rc = libjournal.jouFetchEntries(ct.byref(entries));

    pyEntries = [getdict(entries[i]) for i in range(nResults)]
    return pyEntries


def getSession(date=None, fmt=None, next=True):
    """Get next or previous session by date.

    Syntax:
        sf.getSession(date='', fmt='', next=True)

    Input:
        date=date  str  Date (default: today)
        fmt=fmt    str  Format of the date string (default: 'YYYY-MM-DD')
        next=True  bool If True, takes following date, else previous
    Output:
        Date (string) of next/previous session
    """

    date, fmt = checkDateFmt(date, fmt)
    if date is None:
        return None

# Get 

    closeDate = date
    if next:
        rc = libjournal.jouGetNextSession(date, closeDate, fmt)
    else:
        rc = libjournal.jouGetPrevSession(date, closeDate, fmt)
    if rc:
        return None

    return closeDate[:-1]


def getPrevSession(*args, **kwargs):
    """Get the date of the session preceding date

    Syntax:
        sf.getPreviousSession(date='', fmt='')

    Input:
        date=date  str  Date (default: today)
        fmt=fmt    str  Format of the date string (default: 'YYYY-MM-DD')

    Output:
        Date (string) of previous session
    """

    kwargs['next'] = False
    return getSession(*args, **kwargs)


def getNextSession(*args, **kwargs):
    """Get the date of the session preceding date

    Syntax:
        sf.getNextSession(date='', fmt='')

    Input:
        date=date  str  Date (default: today)
        fmt=fmt    str  Format of the date string (default: 'YYYY-MM-DD')

    Output:
        Date (string) of following session
    """

    return getSession(*args, **kwargs)


def checkDateFmt(date=None, fmt=None):
    """Checks the format of the input date.
    Default date is today.
    """
    if date is None:
        today = datetime.date.today()
        date = today.strftime(date_fmt)

    try:
        date = str_byt.to_byt(date)
    except:
        logger.error('date must be strong or byte array')
        return None, None

    if fmt is None:
        fmt = b''
    else:
        try:
            fmt = str_byt.to_byt(fmt)
        except:
            logger.error('fmt must be string or byte array')
            return None, None

    date = ct.create_string_buffer(date)
    fmt  = ct.create_string_buffer(fmt)

    return date, fmt


def isExpDay(date=None, fmt=None):
    """
    Syntax:
        sf.isExpDay(date=..., fmt=...)

    Input:
        date (optional): str   Date in format fmt. If None, today is assumed
        fmt  (optinal): str    Date format
    Output:
        True if day=date is/was an experimental day, False otherwise
    """

    session = searchSession(date=date, fmt=fmt, onlyUseful=0) # Today
    return (session is not None)


def getLastShot(onlyUseful=0):
    """
    Syntax:
        sf.getLastShot(onlyUseful=...)

    Input:
        onlyUseful (optional) | int | Values: 0 (all shots, default), 1 (useful shots)
    Output:
        Last AUG shot  | int
    """

    today = datetime.date.today()
    today_sf = today.strftime(date_fmt)
    session = searchSession(onlyUseful=onlyUseful) # Today
    if session is None:
        date_last = getPrevSession()
        session = searchSession(date=date_last, onlyUseful=onlyUseful)
    return(session[-1]['shotno'])
