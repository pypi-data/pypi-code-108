"""
Successor to sync; this is advanced synchronization & caching for Flask
apps, using Redis.

storage.py
"""

# Attempts at 2/3 dual compatibility:
from __future__ import print_function

__version__ = "0.2"

import sys, os, shutil, subprocess, threading, copy
import time, datetime
import base64, csv
import shlex

from flask import json

import flask, redis, bs4

import potluck.time_utils, potluck.html_tools, potluck.render

# Python 2/3 dual compatibility
if sys.version_info[0] < 3:
    reload(sys) # noqa F821
    sys.setdefaultencoding('utf-8')
    import socket
    ConnectionRefusedError = socket.error
    IOError_or_FileNotFoundError = IOError
    OSError_or_FileNotFoundError = OSError
else:
    IOError_or_FileNotFoundError = FileNotFoundError
    OSError_or_FileNotFoundError = FileNotFoundError

#-----------#
# Constants #
#-----------#

SCHEMA_VERSION = "1"
"""
The version for the schema used to organize information under keys in
Redis. If this changes, all Redis keys will change.
"""


#-----------#
# Utilities #
#-----------#

def ensure_directory(target):
    """
    makedirs 2/3 shim.
    """
    if sys.version_info[0] < 3:
        try:
            os.makedirs(target)
        except OSError:
            pass
    else:
        os.makedirs(target, exist_ok=True)


#--------------------#
# Filename functions #
#--------------------#

def unused_filename(target):
    """
    Checks whether the target already exists, and if it does, appends _N
    before the file extension, where N is the smallest positive integer
    such that the returned filename is not the name of an existing file.
    If the target does not exists, returns it.
    """
    n = 1
    backup = target
    base, ext = os.path.splitext(target)
    while os.path.exists(backup):
        backup = base + "_" + str(n) + ext
        n += 1

    return backup


def make_way_for(target):
    """
    Given that we're about to overwrite the given file, this function
    moves any existing file to a backup first, numbering backups starting
    with _1. The most-recent backup will have the largest backup number.

    After calling this function, the given target file will not exist,
    and so new material can be safely written there.
    """
    backup = unused_filename(target)
    if backup != target:
        shutil.move(target, backup)


def evaluation_directory(course, semester):
    """
    The evaluation directory for a particular class/semester.
    """
    return os.path.join(
        _EVAL_BASE,
        course,
        semester
    )


def logs_folder(course, semester, username):
    """
    The logs folder for a class/semester/user.
    """
    return flask.safe_join(
        evaluation_directory(course, semester),
        "logs",
        username
    )


def reports_folder(course, semester, username):
    """
    The reports folder for a class/semester/user.
    """
    return flask.safe_join(
        evaluation_directory(course, semester),
        "reports",
        username
    )


def submissions_folder(course, semester):
    """
    The submissions folder for a class/semester.
    """
    return os.path.join(
        evaluation_directory(course, semester),
        "submissions"
    )


def admin_info_file(course, semester):
    """
    The admin info file for a class/semester.
    """
    return os.path.join(
        evaluation_directory(course, semester),
        _CONFIG["ADMIN_INFO_FILE"]
    )


def task_info_file(course, semester):
    """
    The task info file for a class/semester.
    """
    return os.path.join(
        evaluation_directory(course, semester),
        _CONFIG["TASK_INFO_FILE"]
    )


def roster_file(course, semester):
    """
    The roster file for a class/semester.
    """
    return os.path.join(
        evaluation_directory(course, semester),
        _CONFIG["ROSTER_FILE"]
    )


def student_info_file(course, semester):
    """
    The student info file for a class/semester.
    """
    return os.path.join(
        evaluation_directory(course, semester),
        _CONFIG["STUDENT_INFO_FILE"]
    )


#---------------------#
# Redis key functions #
#---------------------#

def redis_key(suffix):
    """
    Given a key suffix, returns a full Redis key which includes
    "potluck:<version>" where version is the schema version (see
    `SCHEMA_VERSION`).
    """
    return "potluck:" + SCHEMA_VERSION + ":" + suffix


def redis_key_suffix(key):
    """
    Returns the part of a Redis key that wasn't added by the `redis_key`
    function.
    """
    return key[len(redis_key("")):]


def inflight_key(course, semester, username, pset, task, phase):
    """
    The in-flight key for a class/semester/user/pset/task/phase.
    """
    return redis_key(
        ':'.join(
            [
                course,
                semester,
                "inflight",
                username,
                pset,
                task,
                phase
            ]
        )
    )


def extension_key(course, semester, username, pset, phase):
    """
    The Redis key for the extension for a
    class/semester/user/pset/phase.
    """
    return redis_key(
        ':'.join([course, semester, "ext", username, pset, phase])
    )


def time_spent_key(course, semester, username, pset, phase, task):
    """
    The Redis key for the time-spent info for a
    class/semester/user/pset/phase/task.
    """
    return redis_key(
        ':'.join(
            [course, semester, "spent", username, pset, phase, task]
        )
    )


def evaluation_key(course, semester, username, pset, phase, task):
    """
    The Redis key for the custom evaluation info for a
    class/semester/user/pset/phase/task.
    """
    return redis_key(
        ':'.join(
            [course, semester, "eval", username, pset, phase, task]
        )
    )


#----------------#
# Roster loading #
#----------------#

def load_roster_from_stream(iterable_of_strings):
    """
    Implements the roster-loading logic given an iterable of strings,
    like an open file or a list of strings. See `AsRoster`.
    """
    reader = csv.reader(iterable_of_strings)

    students = {}
    # [2018/09/16, lyn] Change to handle roster with titles
    # [2019/09/13, Peter] Change to use standard Registrar roster columns
    # by default
    titles = next(reader) # Read first title line of roster
    titles = [x.lower() for x in titles] # convert columns to lower-case
    emailIndex = titles.index('email')

    if 'student name' in titles:
        nameIndex = titles.index('student name')

        def get_name(row):
            return row[nameIndex]

    else:
        firstIndex = titles.index('first')
        lastIndex = titles.index('last')

        def get_name(row):
            return "{} {}".format(row[firstIndex], row[lastIndex])

    if 'section' in titles:
        lecIndex = titles.index('section')
    elif 'lec' in titles:
        lecIndex = titles.index('lec')
    else:
        lecIndex = titles.index('course title')

    if "sort name" in titles:
        sortnameIndex = titles.index('sort name')
    elif "sortname" in titles:
        sortnameIndex = titles.index('sortname')
    else:
        sortnameIndex = None

    for row in reader:
        username = row[emailIndex].split('@')[0]
        if 0 < len(username):
            name = get_name(row)
            namebits = name.split()
            if sortnameIndex is not None:
                sort_by = row[sortnameIndex]
            else:
                sort_by = ' '.join(
                    [row[lecIndex], namebits[-1]]
                    + namebits[:-1]
                )
            students[username] = {
                'username': username,
                'fullname': get_name(row),
                'sortname': sort_by,
                'course_section': row[lecIndex]
            }
        pass
    pass
    return students


#-------------------------#
# Info fetching functions #
#-------------------------#

def get_task_info(course, semester):
    """
    Loads the task info from the JSON file (or returns a cached version
    if the file hasn't been modified since we last loaded it). Needs the
    course and semester to load info for.

    Returns None if the file doesn't exist or can't be parsed.

    Pset and task URLs are added to the information loaded.
    """
    filename = task_info_file(course, semester)
    try:
        result = load_or_get_cached(
            filename,
            assume_fresh=_CONFIG.get("ASSUME_FRESH", 1)
        )
    except Exception:
        flask.flash("Failed to read task info file!")
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to read task info file:\n" + tb,
            file=sys.stderr
        )
        result = None

    if result is None:
        return None

    # Augment task info
    psfmt = _CONFIG.get("PSET_URLS", {}).get(course, "#")
    taskfmt = _CONFIG.get("TASK_URLS", {}).get(course, "#")
    for pset in result["psets"]:
        pset["url"] = psfmt.format(
            semester=semester,
            pset=pset["id"]
        )
        for task in pset["tasks"]:
            task["url"] = taskfmt.format(
                semester=semester,
                pset=pset["id"],
                task=task["id"]
            )
            # Graft static task info into pset task entry
            task.update(result["tasks"][task["id"]])

    return result


def get_admin_info(course, semester):
    """
    Reads the admin info file to get information about which users are
    administrators and various other settings.
    """
    filename = admin_info_file(course, semester)
    try:
        result = load_or_get_cached(
            filename,
            assume_fresh=_CONFIG.get("assume_fresh", 1)
        )
    except Exception:
        flask.flash("Failed to read admin info file '{}'!".format(filename))
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to read admin info file:\n" + tb,
            file=sys.stderr
        )
        result = None

    return result # might be None


def get_roster(course, semester):
    """
    Loads and returns the roster file. Returns None if the file is
    missing.
    """
    return load_or_get_cached(
        roster_file(course, semester),
        view=AsRoster,
        missing=None,
        assume_fresh=_CONFIG.get("ASSUME_FRESH", 1)
    )


def get_student_info(course, semester):
    """
    Loads and returns the student info file. Returns None if the file is
    missing.
    """
    return load_or_get_cached(
        student_info_file(course, semester),
        view=AsStudentInfo,
        missing=None,
        assume_fresh=_CONFIG.get("ASSUME_FRESH", 1)
    )


def get_extension(course, semester, username, pset, phase):
    """
    Gets the extension value (as an integer number in hours) for a user
    on a given phase of a given problem set. Returns 0 if there is no
    extension info for that user. Returns None if there's an error
    reading the value.
    """
    key = extension_key(course, semester, username, pset, phase)
    try:
        result = _REDIS.get(key)
    except Exception:
        flask.flash(
            "Failed to read extension info at '{}'!".format(key)
        )
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to read extension info at '{}':\n{}".format(
                key,
                tb
            ),
            file=sys.stderr
        )
        return None

    if result is None:
        result = 0
    else:
        result = int(result)

    return result


def set_extension(
    course,
    semester,
    username,
    psid,
    phase,
    duration=True,
    only_from=None
):
    """
    Sets an extension value for the given user on the given phase of the
    given pset (in the given course/semester). May be an integer number
    of hours, or just True (the default) for the standard extension
    (whatever is listed in tasks.json). Set to False to remove any
    previously granted extension.

    If only_from is provided, the operation will fail when the extension
    value being updated isn't set to that value (may be a number of
    hours, or True for the standared extension, or False for unset). In
    that case, this function will return False if it fails. Set
    only_from to None to unconditionally update the extension.
    """
    key = extension_key(course, semester, username, psid, phase)
    task_info = get_task_info(course, semester)
    ext_hours = task_info.get("extension_hours", 24)

    if duration is True:
        duration = ext_hours
    elif duration is False:
        duration = 0
    elif not isinstance(duration, (int, bool)):
        raise ValueError(
            (
                "Extension duration must be an integer number of hours,"
                " or a boolean (got {})."
            ).format(repr(duration))
        )

    if only_from is True:
        only_from = ext_hours
    elif (
        only_from not in (False, None)
    and not isinstance(only_from, int)
    ):
        raise ValueError(
            (
                "Only-from must be None, a boolean, or an integer (got"
                " {})."
            ).format(repr(only_from))
        )

    with _REDIS.pipeline() as pipe:
        # Make sure we back off if there's a WatchError
        try:
            pipe.watch(key)
            # Check current value
            current = _REDIS.get(key)
            if current is not None:
                current = int(current) # convert from string

            if duration == current:
                # No need to update!
                return True

            if only_from is not None and (
                (only_from is False and current not in (None, 0))
             or (only_from is not False and current != only_from)
            ):
                # Abort operation because of pre-op change
                flask.flash(
                    (
                        "Failed to write extension info at '{}' (slow"
                        " change)!"
                    ).format(key)
                )
                return False

            # Go ahead and update the value
            pipe.multi()
            pipe.set(key, str(duration))
            pipe.execute()
        except redis.exceptions.WatchError:
            # Update didn't go through
            flask.flash(
                (
                    "Failed to write extension info at '{}' (fast"
                    " change)!"
                ).format(key)
            )
            return False
        except Exception:
            # Some other issue
            flask.flash(
                (
                    "Failed to write extension info at '{}' (unknown)!"
                ).format(key)
            )
            tb = potluck.html_tools.string_traceback()
            print(
                "Failed to write extension info at '{}':\n{}".format(
                    key,
                    tb
                ),
                file=sys.stderr
            )
            return False

    return True


def get_inflight(
    course,
    semester,
    username,
    phase,
    psid,
    taskid
):
    """
    Returns a quadruple containing the timestamp at which processing for
    the given user/phase/pset/task was started, the filename of the log
    file for that evaluation run, the filename of the report file that
    will be generated when it's done, and a string indicating the status
    of the run. Reads that log file to check whether the process has
    completed, and updates in-flight state accordingly. Returns (None,
    None, None, None) if no attempts to grade the given task have been
    made yet.

    The status string will be one of:

    - "initial" - evaluation hasn't started yet.
    - "in_progress" - evaluation is running.
    - "error" - evaluation noted an error in the log.
    - "expired" - We didn't hear back from evaluation, but it's been so
         long that we've given up hope.
    - "completed" - evaluation finished.

    When status is "error", "expired", or "completed", it's appropriate
    to initiate a new evaluation run for that file, but in other cases,
    the existing run should be allowed to terminate first.

    In rare cases, when an exception is encountered trying to read the
    file even after a second attempt, the timestamp will be set to
    "error" with status and filename values of None.
    """
    key = inflight_key(course, semester, username, phase, psid, taskid)

    try:
        response = _REDIS.lrange(key, 0, -1)
    except Exception:
        flask.flash(
            "Failed to fetch in-flight info at '{}'!".format(key)
        )
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to fetch in-flight info at '{}':\n{}".format(
                key,
                tb
            ),
            file=sys.stderr
        )
        return ("error", None, None, None)

    # If the key didn't exist
    if response is None or len(response) == 0:
        return (None, None, None, None)

    # Unpack the response
    timestring, log_filename, report_filename, status = response

    if status in ("error", "expired", "completed"):
        # No need to check the log text again
        return (timestring, log_filename, report_filename, status)

    # Figure out what the new status should be...
    new_status = status

    # Read the log file to see if evaluation has finished yet
    if os.path.isfile(log_filename):
        try:
            with open(log_filename, 'r') as fin:
                log_text = fin.read()
        except Exception:
            flask.flash("Failed to read evaluation log file!")
            tb = potluck.html_tools.string_traceback()
            print(
                "Failed to read evaluation log file:\n" + tb,
                file=sys.stderr
            )
            # Treat as a missing file
            log_text = ""
    else:
        # No log file
        log_text = ""

    # If anything has been written to the log file, we're in progress...
    if status == "initial" and log_text != "":
        new_status = "in_progress"

    # Check for an error
    if potluck.render.ERROR_MSG in log_text:
        new_status = "error"

    # Check for completion message (ignored if there's an error)
    if (
        status in ("initial", "in_progress")
    and new_status != "error"
    and log_text.endswith(potluck.render.DONE_MSG + '\n')
    ):
        new_status = "completed"

    # Check absolute timeout (only if we DIDN'T see a done message)
    if new_status not in ("error", "completed"):
        elapsed = (
            potluck.time_utils.now()
          - potluck.time_utils.time_from_timestring(timestring)
        )
        allowed = datetime.timedelta(
            seconds=_CONFIG["FINAL_EVAL_TIMEOUT"]
        )
        if elapsed > allowed:
            new_status = "expired"

    # Now we've got our result
    result = (timestring, log_filename, report_filename, new_status)

    # Write new status if it has changed
    if new_status != status:
        try:
            with _REDIS.pipeline() as pipe:
                pipe.delete(key) # clear the list
                pipe.rpush(key, *result) # add our new info
                pipe.execute()
        except Exception:
            flask.flash(
                (
                    "Error trying to update in-flight info at '{}'."
                ).format(key)
            )
            tb = potluck.html_tools.string_traceback()
            print(
                "Failed to update in-flight info at '{}':\n{}".format(
                    key,
                    tb
                ),
                file=sys.stderr
            )
            return ("error", None, None, None)

    # Return our result
    return result


def put_inflight(course, semester, username, phase, psid, taskid):
    """
    Picks new log and report filenames for the given user/phase/pset/task
    and returns a quad containing a string timestamp, the new log
    filename, the new report filename, and the status string "initial",
    while also writing that information into the inflight data for that
    user so that get_inflight will return it until evaluation is
    finished.

    Returns (None, None, None, None) if there is already an in-flight
    log file for this user/pset/task that has a status other than
    "error", "expired", or "completed".

    Returns ("error", None, None, None) if it encounters a situation
    where the inflight key is changed during the update operation,
    presumably by another simultaneous call to put_inflight. This
    ensures that only one simultaneous call can succeed, and protects
    against race conditions on the log and report filenames.
    """
    # The Redis key for inflight info
    key = inflight_key(course, semester, username, phase, psid, taskid)

    with _REDIS.pipeline() as pipe:
        try:
            pipe.watch(key)
            response = pipe.lrange(key, 0, -1)
            if response is not None and len(response) != 0:
                # key already exists, so we need to check status
                prev_ts, prev_log, prev_result, prev_status = response
                if prev_status in ("initial", "in_progress"):
                    # Another evaluation is in-flight; indicate that to
                    # our caller and refuse to re-initiate evaluation
                    return (None, None, None, None)

            # Generate a timestamp for the log file
            timestamp = potluck.time_utils.timestring()

            # Get unused log and report filenames
            istring = "{phase}-{psid}-{taskid}-{timestamp}".format(
                phase=phase,
                psid=psid,
                taskid=taskid,
                timestamp=timestamp
            )

            # Note: unused_filename has a race condition if two
            # put_inflight calls occur simultaneously. However, due to
            # our use of watch, only one of the two calls can make it
            # out of this block without triggering a WatchError, meaning
            # that only the one that makes it out first will make use of
            # a potentially-conflicting filename. That said, *any* other
            # process which might create files with names like the log
            # and report filenames we select would be bad.

            # Select an unused log filename
            log_folder = logs_folder(course, semester, username)
            ensure_directory(log_folder)
            logfile = unused_filename(
                flask.safe_join(log_folder, istring + ".log")
            )

            # Select an unused report filename
            report_folder = reports_folder(course, semester, username)
            ensure_directory(report_folder)
            reportfile = unused_filename(
                flask.safe_join(report_folder, istring + ".json")
            )

            # Gather the info into a tuple
            ifinfo = (
                timestamp,
                logfile,
                reportfile,
                "initial"
            )

            # Rewrite the key
            pipe.multi()
            pipe.delete(key)
            pipe.rpush(key, *ifinfo)
            pipe.execute()
        except redis.exceptions.WatchError:
            flask.flash(
                (
                    "Unable to put task evaluation in-flight: key '{}'"
                    " was changed."
                ).format(key)
            )
            return ("error", None, None, None)
        except Exception:
            flask.flash(
                (
                    "Error trying to write in-flight info at '{}'."
                ).format(key)
            )
            tb = potluck.html_tools.string_traceback()
            print(
                "Failed to write in-flight info at '{}':\n{}".format(
                    key,
                    tb
                ),
                file=sys.stderr
            )
            return ("error", None, None, None)

    # Return the timestamp, filenames, and status that we recorded
    return ifinfo


def fetch_time_spent(course, semester, username, phase, psid, taskid):
    """
    Returns a time-spent record for the given user/phase/pset/task. It
    has the following keys:

    - "phase": The phase (a string).
    - "psid": The problem-set ID (a string).
    - "taskid": The task ID (a string).
    - "updated_at": A timestring (see `potluck.time_utils.timestring`)
        indicating when the information was last updated.
    - "time_spent": A floating-point number (as a string) or just a
        string describing the user's description of the time they spent
        on the task.
    - "prev_update": If present, indicates that the time_spent value
        came from a previous entry and was preserved when a newer entry
        would have been empty. Shows the time at which the previous
        entry was entered.
        TODO: preserve across multiple empty entries?

    Returns None if there is no information for that user/pset/task yet,
    or if an error is encountered while trying to access that
    information.
    """
    # Redis key to use
    key = time_spent_key(
        course,
        semester,
        username,
        psid,
        phase,
        taskid
    )

    try:
        response = _REDIS.hmget(
            key,
            "updated_at",
            "time_spent",
            "prev_update"
        )
    except Exception:
        flask.flash("Error fetching time-spent info.")
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to fetch time spent info at '{}':\n{}".format(
                key,
                tb
            ),
            file=sys.stderr
        )
        return None

    # Some kind of non-exception error during access, or key is missing
    if response is None or len(response) != 3 or response[0] is None:
        return None

    try:
        spent = float(response[1])
    except ValueError:
        spent = response[1]

    result = {
        "phase": phase,
        "psid": psid,
        "taskid": taskid,
        "updated_at": response[0],
        "time_spent": spent
    }

    if response[2] is not None:
        result["prev_update"] = response[2]

    return result


def record_time_spent(
    course,
    semester,
    username,
    phase,
    psid,
    taskid,
    time_spent
):
    """
    Inserts a time spent entry into the given user's time spent info.

    If called multiple times, the last call will override the
    information set by any previous ones. If called multiple times
    simultaneously, one of the calls will overwrite the other, but it
    may not be able to pull the other call's info to replace a default
    value (which is fine...).
    """
    # Redis key to use
    key = time_spent_key(
        course,
        semester,
        username,
        psid,
        phase,
        taskid
    )

    # Generate a timestamp for the info
    timestring = potluck.time_utils.timestring()

    # Convert to a number if we can
    try:
        time_spent = float(time_spent)
    except Exception:
        pass

    # Here's the info we store
    info = {
        "updated_at": timestring,
        "time_spent": time_spent
    }

    # Check for old info if the new info is missing
    if time_spent == "":
        try:
            response = _REDIS.hmget(
                key,
                "updated_at",
                "time_spent",
                "prev_update"
            )
            if (
                response is None
             or len(response) != 2
            ):
                raise ValueError(
                    "Unable to retrieve previous data from time spent"
                    " info."
                )
            # check for missing key, or no previous info
            if response[0] is not None and response[1] != '':
                if response[2] is None:
                    prev = response[0]
                else:
                    prev = response[2]

                info["prev_update"] = prev
                info["time_spent"] = response[1]
            # else leave info as-is

        except Exception:
            flask.flash("Failed to fetch time spent info!")
            tb = potluck.html_tools.string_traceback()
            print(
                "Failed to fetch time spent info at '{}':\n{}".format(
                    key,
                    tb
                ),
                file=sys.stderr
            )
            # we'll keep going to update new info though

    try:
        success = _REDIS.hmset(key, info)
        if success is not True:
            raise ValueError("Redis result indicated failure.")
    except Exception:
        flask.flash("Failed to write time-spent info!")
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to write time spent info at '{}':\n{}".format(
                key,
                tb
            ),
            file=sys.stderr
        )


def fetch_evaluation(course, semester, username, phase, psid, taskid):
    """
    Fetches the manual evaluation information for the given
    user/phase/pset/task. The result will be a dictionary with the
    following keys:

    - "phase": The phase (a string).
    - "psid": The problem-set ID (a string).
    - "taskid": The task ID (a string).
    - "updated_at": A timestring (see `potluck.time_utils.timestring`)
        indicating when the information was last updated.
    - "notes": The markdown source string for custom notes.
    - "override": A numerical score that overrides the automatic
        evaluation. Will be an empty string if there is no override to
        apply.

    Returns None instead of a dictionary if there is no information for
    that user/pset/task yet, or if an error is encountered while trying
    to access that information.
    """
    # Redis key to use
    key = evaluation_key(
        course,
        semester,
        username,
        psid,
        phase,
        taskid
    )

    try:
        response = _REDIS.hmget(
            key,
            "updated_at",
            "notes",
            "override"
        )
    except Exception:
        flask.flash("Error fetching evaluation info.")
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to fetch evaluation info at '{}':\n{}".format(
                key,
                tb
            ),
            file=sys.stderr
        )
        return None

    # Some kind of non-exception error during access, or key is missing
    if response is None or len(response) != 3 or response[0] is None:
        return None

    try:
        override = float(response[2])
    except ValueError:
        override = response[2]

    result = {
        "phase": phase,
        "psid": psid,
        "taskid": taskid,
        "updated_at": response[0],
        "notes": response[1],
        "override": override,
    }

    return result


def set_evaluation(
    course,
    semester,
    username,
    phase,
    psid,
    taskid,
    notes,
    override=""
):
    """
    Updates the custom evaluation info for a particular task submitted by
    a particular use for a certain phase of a specific pset (in a
    course/semester).

    Completely erases the previous custom evaluation info.

    The notes argument must be a string, and will be treated as Markdown
    and converted to HTML when being displayed to the user. It will be
    displayed on a feedback page and it can thus link to rubric items or
    snippets by their IDs if you want to get fancy.

    The override argument defaults to an empty string, which is how to
    indicate that no override should be applied. Otherwise, it should be
    a floating-point number or integer between 0 and 100; it will be
    stored as a float if convertible.

    Returns True if it succeeds or False if it encounters some sort of
    error.
    """
    # Redis key to use
    key = evaluation_key(
        course,
        semester,
        username,
        psid,
        phase,
        taskid
    )

    # Generate a timestamp for the info
    timestring = potluck.time_utils.timestring()

    # Convert to a number if we can
    if override != "":
        try:
            override = float(override)
            if 0 < override < 1:
                flask.flash(
                    (
                        "Warning: you entered '{}' as the grade"
                        " override, but scores should be specified out"
                        " of 100, not out of 1! The override has been"
                        " set as-given but you may want to update it."
                    ).format(override)
                )
        except Exception:
            flask.flash(
                (
                    "Warning: you entered '{}' as the grade override,"
                    " but grade overrides should be numbers between 0"
                    " and 100. The override has been set as-given, but"
                    " you may want to update it."
                ).format(override)
            )

    # Here's the info we store
    info = {
        "updated_at": timestring,
        "notes": notes,
        "override": override
    }

    try:
        success = _REDIS.hmset(key, info)
        if success is not True:
            raise ValueError("Redis result indicated failure.")
    except Exception:
        flask.flash("Failed to write evaluation info!")
        tb = potluck.html_tools.string_traceback()
        print(
            "Failed to write evaluation info at '{}':\n{}".format(
                key,
                tb
            ),
            file=sys.stderr
        )
        return False

    return True


def default_feedback_summary():
    """
    Returns a default summary object. The summary is a pared-down version
    of the full feedback .json file that stores the result of
    `potluck.render.render_report`, which in turn comes mostly from
    `potluck.rubrics.Rubric.evaluate`.
    """
    return {
        "submitted": False, # We didn't find any feedback file!
        "timestamp": "(not evaluated)",
        "partner_username": None,
        "evaluation": "not evaluated",
        "warnings": [ "We found no submission for this task." ],
        "is_default": True
    }


def get_feedback_summary(
    course,
    semester,
    task_info,
    username,
    phase,
    psid,
    taskid
):
    """
    This retrieves just the feedback summary information that appears on
    the dashboard for a given user/phase/pset/task. That much info is
    light enough to cache, so we do cache it to prevent hitting the disk
    a lot for each dashboard view.
    """
    ts, log_file, report_file, status = get_inflight(
        course,
        semester,
        username,
        phase,
        psid,
        taskid
    )
    fallback = default_feedback_summary()
    if ts in (None, "error"):
        return fallback
    try:
        return load_or_get_cached(
            report_file,
            view=AsFeedbackSummary,
            missing=fallback,
            assume_fresh=_CONFIG.get("ASSUME_FRESH", 1)
        )
    except Exception:
        flask.flash("Failed to summarize feedback file.")
        return fallback


def get_feedback(
    course,
    semester,
    task_info,
    username,
    phase,
    psid,
    taskid
):
    """
    Gets feedback for the user's latest pre-deadline submission for the
    given phase/pset/task. Instead of caching these values (which would
    be expensive memory-wise over time) we hit the disk every time.

    Returns a dictionary with at least a 'status' entry. This will be
    'ok' if the report was read successfully, or 'missing' if the report
    file could not be read or did not exist. If the status is
    'missing', a 'log' entry will be present with the contents of the
    associated log file, or the string 'missing' if that log file could
    also not be read.

    Weird stuff could happen if the file is being written as we make the
    request. Typically a second attempt should not re-encounter such an
    error.
    """
    result = { "status": "unknown" }
    ts, log_file, report_file, status = get_inflight(
        course,
        semester,
        username,
        phase,
        psid,
        taskid
    )
    if ts is None: # No submission
        result["status"] = "missing"
    elif ts == "error": # Failed to read inflight file
        flask.flash(
            "Failed to fetch in-flight info; please refresh the page."
        )
        result["status"] = "missing"

    if result["status"] != "missing":
        try:
            if not os.path.exists(report_file):
                result["status"] = "missing"
            else:
                with open(report_file, 'r') as fin:
                    result = json.load(fin)
                    result["status"] = "ok"
        except Exception:
            flask.flash("Failed to read feedback file.")
            tb = potluck.html_tools.string_traceback()
            print(
                "Failed to read feedback file '{}':\n{}".format(
                    report_file,
                    tb
                ),
                file=sys.stderr
            )
            result["status"] = "missing"

    if result["status"] == "ok":
        # Polish up warnings/evaluation a tiny bit
        warnings = result.get("warnings", [])
        evaluation = result.get("evaluation", "not evaluated")
        if evaluation == "incomplete" and len(warnings) == 0:
            warnings.append(
                "Your submission is incomplete"
              + " (it did not satisfy even half of the core goals)."
            )
        result["evaluation"] = evaluation
        result["warnings"] = warnings
        result["submitted"] = True

    # Try to read log file if we couldn't get a report
    if result["status"] == "missing":
        if log_file is None:
            result["log"] = "no submission was made"
        else:
            try:
                if not os.path.exists(log_file):
                    result["log"] = "missing"
                else:
                    with open(log_file, 'r') as fin:
                        result["log"] = fin.read()
            except Exception:
                flask.flash("Error reading log file.")
                tb = potluck.html_tools.string_traceback()
                print(
                    "Failed to read log file '{}':\n{}".format(log_file, tb),
                    file=sys.stderr
                )
                result["log"] = "missing"

    return result


def get_feedback_html(
    course,
    semester,
    task_info,
    username,
    phase,
    psid,
    taskid
):
    """
    Gets feedback for the user's latest pre-deadline submission for the
    given phase/pset/task, as html instead of as json (see
    `get_feedback`). Instead of caching these values (which would be
    expensive memory-wise over time) we hit the disk every time.

    Returns the string "missing" if the relevant feedback file does not
    exist, or if some kind of error occurs trying to access the file.

    Might encounter an error if the file is being written as we try to
    read it.
    """
    result = None
    ts, log_file, report_file, status = get_inflight(
        course,
        semester,
        username,
        phase,
        psid,
        taskid
    )
    if ts is None: # No submission
        result = "missing"
    elif ts == "error": # Failed to read inflight file
        flask.flash(
            "Failed to read in-flight info; please refresh the page."
        )
        result = "missing"

    if result != "missing":
        html_file = report_file[:-5] + ".html"
        try:
            if os.path.exists(html_file):
                # These include student code, instructions, etc., so it
                # would be expensive to cache them.
                with open(html_file, 'r') as fin:
                    result = fin.read()
                result = AsFeedbackHTML.decode(result)
            else:
                result = "missing"
        except Exception:
            flask.flash("Failed to read feedback report.")
            tb = potluck.html_tools.string_traceback()
            print(
                "Failed to read feedback report '{}':\n{}".format(
                    html_file,
                    tb
                ),
                file=sys.stderr
            )
            result = "missing"

    return result


#-------#
# Views #
#-------#

class View:
    """
    Abstract View class to organize decoding/encoding of views. Each View
    must define encode and decode class methods which are each others'
    inverse. The class name is used as part of the cache key. For
    read-only views, a exception (e.g., NotImplementedError) should be
    raised in the encode method.

    Note that the decode method may be given None as a parameter in
    situations where a file doesn't exist, and in most cases should
    simply pass that value through.
    """
    @staticmethod
    def encode(obj):
        """
        The encode function of a View must return a string (to be written
        to a file).
        """
        raise NotImplementedError("Don't use the base View class.")

    @staticmethod
    def decode(string):
        """
        The encode function of a View must accept a string, and if given
        a string produced by encode, should return an equivalent object.
        """
        raise NotImplementedError("Don't use the base View class.")


class AsIs(View):
    """
    A pass-through view that returns strings unaltered.
    """
    @staticmethod
    def encode(obj):
        """Returns the object it is given unaltered."""
        return obj

    @staticmethod
    def decode(string):
        """Returns the string it is given unaltered."""
        return string


class AsJSON(View):
    """
    A view that converts objects to JSON for file storage and back on
    access. It passes through None.
    """
    @staticmethod
    def encode(obj):
        """Returns the JSON encoding of the object."""
        return json.dumps(obj)

    @staticmethod
    def decode(string):
        """
        Returns a JSON object parsed from the string.
        Returns None if it gets None.
        """
        if string is None:
            return None
        return json.loads(string)


def build_view(name, encoder, decoder, pass_none=True):
    """
    Function for building a view given a name, an encoding function, and
    a decoding function. Unless pass_none is given as False, the decoder
    will be skipped if the decode argument is None and the None will pass
    through, in which case the decoder will *always* get a string as an
    argument.
    """
    class SyntheticView(View):
        """
        View class created using build_view.
        """
        @staticmethod
        def encode(obj):
            return encoder(obj)

        @staticmethod
        def decode(string):
            if pass_none and string is None:
                return None
            return decoder(string)

    SyntheticView.__name__ = name
    SyntheticView.__doc__ = (
        "View that uses '{}' for encoding and '{}' for decoding."
    ).format(encoder.__name__, decoder.__name__)
    SyntheticView.encode.__doc__ = encoder.__doc__
    SyntheticView.decode.__doc__ = decoder.__doc__

    return SyntheticView


class AsStudentInfo(View):
    """
    Encoding and decoding for TSV student info files, which are cached.
    The student info structure is a dictionary mapping usernames to
    additional student info.
    """
    @staticmethod
    def encode(obj):
        """
        Student info *cannot* be encoded, because we are not interested
        in writing it to a file.
        TODO: Student info editing in-app?
        """
        raise NotImplementedError(
            "Cannot encode student info: student info is read-only."
        )

    @staticmethod
    def decode(string):
        """
        Extra student info is read from a student info file by extracting
        the text, loading it as Excel-TSV data, and turning it into a
        dictionary where each student ID maps to a dictionary containing
        the columns as keys with values from that column as values.
        """
        reader = csv.DictReader(
            (line for line in string.strip().split('\n')),
            dialect="excel-tab"
        )
        result = {}
        for row in reader:
            entry = {}
            for key in _CONFIG["REMAP_STUDENT_INFO"]:
                entry[_CONFIG["REMAP_STUDENT_INFO"][key]] = row.get(key)
            entry["username"] = entry["email"].split('@')[0]
            result[entry['username']] = entry
        return result


class AsRoster(View):
    """
    Encoding and decoding for CSV rosters, which are cached. The roster
    structure is a dictionary mapping usernames to student info.
    """
    @staticmethod
    def encode(obj):
        """
        A roster *cannot* be encoded, because we are not interested in
        writing it to a file.
        TODO: Roster editing in-app?
        """
        raise NotImplementedError(
            "Cannot encode a roster: rosters are read-only."
        )

    @staticmethod
    def decode(string):
        """
        A roster is read from a roaster file by extracting the text and
        running it through `load_roster_from_stream`.
        """
        lines = string.strip().split('\n')
        return load_roster_from_stream(lines)


class AsFeedbackHTML(View):
    """
    Encoding and decoding for feedback HTML files (we extract the body
    contents).
    """
    @staticmethod
    def encode(obj):
        """
        Feedback HTML *cannot* be encoded, because we want it to be
        read-only: it's produced by running potluck_eval, and the server
        won't edit it.
        """
        raise NotImplementedError(
            "Cannot encode feedback HTML: feedback is read-only."
        )

    @staticmethod
    def decode(string):
        """
        Feedback HTML is read from the raw HTML file by extracting the
        innerHTML of the body tag using Beautiful Soup. Returns a default
        string if the file wasn't found.
        """
        if string is None: # happens when the target file doesn't exist
            return "no feedback available"
        soup = bs4.BeautifulSoup(string, "html.parser")
        body = soup.find("body")
        return str(body)


class AsFeedbackSummary(View):
    """
    Encoding and decoding for feedback summaries, which are cached.
    """
    @staticmethod
    def encode(obj):
        """
        A feedback summary *cannot* be encoded, because it cannot be
        written to a file. Feedback summaries are only read from full
        feedback files, never written.
        """
        raise NotImplementedError(
            "Cannot encode a feedback summary: summaries are read-only."
        )

    @staticmethod
    def decode(string):
        """
        A feedback summary is read from a feedback file by extracting the
        full JSON feedback and then paring it down to just the essential
        information for the dashboard view.
        """
        if string is None: # happens when the target file doesn't exist
            return default_feedback_summary()
        # Note taskid is nonlocal here
        raw_report = json.loads(string)
        warnings = raw_report.get("warnings", [])
        evaluation = raw_report.get("evaluation", "not evaluated")
        if evaluation == "incomplete" and len(warnings) == 0:
            warnings.append(
                "Your submission is incomplete"
              + " (it did not satisfy even half of the core goals)."
            )
        return {
            "submitted": True,
            "partner_username": raw_report.get("partner_username"),
            "timestamp": raw_report.get("timestamp"),
            "evaluation": evaluation,
            "warnings": warnings,
            "is_default": False
            # report summary, files, table, and contexts omitted
        }


#------------------------#
# Read-only file caching #
#------------------------#

# Note: by using a threading.RLock and a global variable here, we are not
# process-safe, which is fine, because this is just a cache: each process
# in a multi-process environment can safely maintain its own cache which
# will waste a bit of memory but not lead to corruption. As a corollary,
# load_or_get_cached should be treated as read-only, otherwise one
# process might write to a file that's being read leading to excessively
# interesting behavior.

# TODO: We should probably have some kind of upper limit on the cache
# size, and maintain staleness so we can get rid of stale items...
_CACHE_LOCK = threading.RLock() # Make this reentrant just in case...
_CACHE = {}
"""
Cache of objects returned by view functions on cache keys.
"""


_FRESH_AT = {}
"""
Mapping from cache keys to the most recent time at which they were found
to be fresh.
"""


def build_file_freshness_checker(
    missing=Exception,
    assume_fresh=0,
    cache={}
):
    """
    Builds a freshness checker that checks the mtime of a filename, but
    if that file doesn't exist, it returns AbortGeneration with the given
    missing value (unless missing is left as the default of Exception, in
    which case it lets the exception bubble out).

    If assume_fresh is set to a positive number, and less than that many
    seconds have elapsed since the most recent mtime check, the mtime
    check is skipped and the file is assumed to be fresh.
    """
    ck = (id(missing), assume_fresh)
    if ck in cache:
        return cache[ck]

    def check_file_is_changed(cache_key, ts):
        """
        Checks whether a file has been modified more recently than the given
        timestamp.
        """
        global _FRESH_AT
        now = time.time()
        if (
            cache_key in _FRESH_AT
        and now - _FRESH_AT[cache_key] < assume_fresh
        ):
            return True

        filename = cache_key_filename(cache_key)
        try:
            mtime = os.path.getmtime(filename)
        except OSError_or_FileNotFoundError:
            if missing == Exception:
                raise
            else:
                return AbortGeneration(missing)

        # File is changed if the mtime is after the given cache
        # timestamp, or if the timestamp is None
        result = ts is None or mtime >= ts
        if result:
            _FRESH_AT[cache_key] = now

        return result

    cache[ck] = check_file_is_changed
    return check_file_is_changed


def build_file_reader(view=AsJSON):
    """
    Builds a file reader function which returns the result of the given
    view on the file contents.
    """
    def read_file(cache_key):
        """
        Reads a file and returns the result of calling a view's decode
        function on the file contents. Returns None if there's an error,
        and prints the error unless it's a FileNotFoundError.
        """
        filename = cache_key_filename(cache_key)
        try:
            with open(filename, 'r') as fin:
                return view.decode(fin.read())
        except IOError_or_FileNotFoundError:
            return None
        except Exception as e:
            sys.stderr.write(
                "[sync module] Exception viewing file:\n" + str(e) + '\n'
            )
            return None

    return read_file


#--------------------#
# File I/O functions #
#--------------------#

def cache_key_for(target, view):
    """
    Builds a hybrid cache key value with a certain target and view. The
    target filename must not include '::'.
    """
    if '::' in target:
        raise ValueError(
            "Cannot use a filename with a '::' in it as the target"
            " file."
        )
    return target + '::' + view.__name__


def cache_key_filename(cache_key):
    """
    Returns just the filename given a cache key.
    """
    filename = None
    for i in range(len(cache_key) - 1):
        if cache_key[i:i + 2] == '::':
            filename = cache_key[:i]
            break
    if filename is None:
        raise ValueError("Value '{}' is not a cache key!".format(cache_key))

    return filename


def load_or_get_cached(
    filename,
    view=AsJSON,
    missing=Exception,
    assume_fresh=0
):
    """
    Reads the given file, returning its contents as a string. Doesn't
    actually do that most of the time. Instead, it will return a cached
    value. And instead of returning the contents of the file as a
    string, it returns the result of running the given view function on
    the file's contents (decoded as a string). And actually, it caches
    the view result, not the file contents, to save time reapplying the
    view. The default view is AsJSON, which loads the file contents as
    JSON and creates a Python object.

    The __name__ of the view class will be used to compute a cache key
    for that view; avoid view name collisions.

    If the file on disk is newer than the cache, re-reads and re-caches
    the file. If assume_fresh is set to a positive number, then the file
    time on disk isn't even checked if the most recent check was
    performed less than that many seconds ago.

    If the file is missing, an exception would normally be raised, but
    if the `missing` value is provided as something other than
    `Exception`, a deep copy of that value will be returned instead.

    Note: On a cache hit, a deep copy of the cached value is returned, so
    modifying that value should not affect what is stored in the cache.
    """

    # Figure out our view object (& cache key):
    if view is None:
        view = AsIs

    cache_key = cache_key_for(filename, view)

    # Build functions for checking freshness and reading the file
    check_mtime = build_file_freshness_checker(missing, assume_fresh)
    read_file = build_file_reader(view)

    return _gen_or_get_cached(
        _CACHE_LOCK,
        _CACHE,
        cache_key,
        check_mtime,
        read_file
    )


#----------------------#
# Core caching routine #
#----------------------#

class AbortGeneration:
    """
    Class to signal that generation of a cached item should not proceed.
    Holds a default value to return instead.
    """
    def __init__(self, replacement):
        self.replacement = replacement


class NotInCache:
    """
    Placeholder for recognizing that a value is not in the cache (when
    e.g., None might be a valid cache value).
    """
    pass


def _gen_or_get_cached(
    lock,
    cache,
    cache_key,
    check_dirty,
    result_generator
):
    """
    Common functionality that uses a reentrant lock and a cache
    dictionary to return a cached value if the cached value is fresh. The
    value from the cache is deep-copied before being returned, so that
    any modifications to the returned value shouldn't alter the cache.
    Parameters are:

        lock: Specifies the lock to use. Should be a threading.RLock.
        cache: The cache dictionary.
        cache_key: String key for this cache item.
        check_dirty: Function which will be given the cache_key and a
            timestamp and must return True if the cached value (created
            at that instant) is dirty (needs to be updated) and False
            otherwise. May also return an AbortGeneration instance with a
            default value inside to be returned directly. If there is no
            cached value, check_dirty will be given a timestamp of None.
        result_generator: Function to call to build a new result if the
            cached value is stale. This new result will be cached. It
            will be given the cache_key as a parameter.
    """
    with lock:
        # We need to read the file contents and return them.
        cache_ts, cached = cache.get(cache_key, (None, NotInCache))
        safe_cached = copy.deepcopy(cached)

    # Use the provided function to check if this cache key is dirty.
    # No point in story the missing value we return since the dirty
    # check would presumably still come up True in the future.
    is_dirty = check_dirty(cache_key, cache_ts)
    if isinstance(is_dirty, AbortGeneration):
        # check_fresh calls for an abort: return replacement value
        return is_dirty.replacement
    elif not is_dirty and cached != NotInCache:
        # Cache is fresh: return cached value
        return safe_cached
    else:
        # Cache is stale

        # Get timestamp before we even start generating value:
        ts = time.time()

        # Generate reuslt:
        result = result_generator(cache_key)

        # Safely store new result value + timestamp in cache:
        with lock:
            cache[cache_key] = (ts, result)
            # Don't allow outside code to mess with internals of
            # cached value (JSON results could be mutable):
            safe_result = copy.deepcopy(result)

        # Return fresh deep copy of cached value:
        return safe_result


#-----------------#
# Setup functions #
#-----------------#

_REDIS = None
"""
The connection to the REDIS server.
"""

_CONFIG = None
"""
The flask app's configuration object.
"""


def init(config, key=None):
    """
    `init` should be called once per process, ideally early in the life of
    the process, like right after importing the module. Calling
    some functions before `init` will fail. A file named 'redis-pw.conf'
    should exist unless a key is given (should be a byte-string). If
    'redis-pw.conf' doesn't exist, it will be created.
    """
    global _REDIS, _CONFIG, _EVAL_BASE

    # Store config object
    _CONFIG = config

    # Compute evaluation base directory based on init-time CWD
    _EVAL_BASE = os.path.join(os.getcwd(), _CONFIG["EVALUATION_BASE"])

    # Grab port from config
    port = config.get("STORAGE_PORT", 51723)

    # Redis configuration filenames
    rconf_file = "potluck-redis.conf"
    ruser_file = "potluck-redis-user.acl"
    rport_file = "potluck-redis-port.conf"
    rpid_file = "potluck-redis.pid"
    rlog_file = "potluck-redis.log"

    # Check for redis config file
    if not os.path.exists(rconf_file):
        raise IOError_or_FileNotFoundError(
            "Unable to find Redis configuration file '{}'.".format(
                rconf_file
            )
        )

    # Check that conf file contains required stuff
    # TODO: More flexibility about these things?
    with open(rconf_file, 'r') as fin:
        rconf = fin.read()
        adir = 'aclfile "{}"'.format(ruser_file)
        if adir not in rconf:
            raise ValueError(
                (
                    "Redis configuration file '{}' is missing an ACL"
                    " file directive for the ACL file. It needs to use"
                    " '{}'."
                ).format(rconf_file, adir)
            )

        incl = "include {}".format(rport_file)
        if incl not in rconf:
            raise ValueError(
                (
                    "Redis configuration file '{}' is missing an include"
                    " for the port file. It needs to use '{}'."
                ).format(rconf_file, incl)
            )

        pdecl = 'pidfile "{}"'.format(rpid_file)
        if pdecl not in rconf:
            raise ValueError(
                (
                    "Redis configuration file '{}' is missing the"
                    " correct PID file directive '{}'."
                ).format(rconf_file, pdecl)
            )

        ldecl = 'logfile "{}"'.format(rlog_file)
        if ldecl not in rconf:
            raise ValueError(
                (
                    "Redis configuration file '{}' is missing the"
                    " correct log file directive '{}'."
                ).format(rconf_file, ldecl)
            )

    # Get storage key:
    if key is None:
        try:
            if os.path.exists(ruser_file):
                with open(ruser_file, 'r') as fin:
                    key = fin.read().strip().split()[-1][1:]
            else:
                print(
                    "Creating new Redis user file '{}'.".format(
                        ruser_file
                    )
                )
                # b32encode here makes it more readable
                key = base64.b32encode(os.urandom(64)).decode("ascii")
                udecl = "user default on +@all ~* >{}".format(key)
                with open(ruser_file, 'w') as fout:
                    fout.write(udecl)
        except Exception:
            raise IOError_or_FileNotFoundError(
                "Unable to access user file '{}'.".format(ruser_file)
            )

    # Double-check port, or write port conf file
    if os.path.exists(rport_file):
        with open(rport_file, 'r') as fin:
            portstr = fin.read().strip().split()[1]
        try:
            portconf = int(portstr)
        except Exception:
            portconf = portstr

        if portconf != port:
            raise ValueError(
                (
                    "Port was specified as {}, but port conf file"
                    " already exists and says port should be {}."
                    " Delete the port conf file '{}' to re-write it."
                ).format(repr(port), repr(portconf), rport_file)
            )
    else:
        # We need to write the port into the config file
        with open(rport_file, 'w') as fout:
            fout.write("port " + str(port))

    _REDIS = redis.Redis(
        'localhost',
        port,
        password=key,
        decode_responses=True
    )
    # Attempt to connect; if that fails, attempt to start a new Redis
    # server and attempt to connect again. Abort if we couldn't start
    # the server.
    print("Attempting to connect to Redis server...")
    try:
        _REDIS.exists('test') # We just want to not trigger an error
        print("...connected successfully.")
    except redis.exceptions.ConnectionError: # nobody to connect to
        _REDIS = None
    except redis.exceptions.ResponseError: # bad password
        raise ValueError(
            "Your authentication key is not correct. Make sure"
            " you're not sharing the port you chose with another"
            " process!"
        )

    if _REDIS is None:
        print("...failed to connect...")
        if os.path.exists(rpid_file):
            print(
                (
                    "...a Redis PID file already exists at '{}', but we"
                    " can't connect. Please shut down the old Redis"
                    " server first, or clean up the PID file if it"
                    " crashed."
                ).format(rpid_file)
            )
            raise ValueError(
                "Aborting server startup due to existing PID file."
            )

        # Try to start a new redis server...
        print("...starting Redis...")
        try:
            subprocess.Popen(["redis-server", rconf_file])
        except OSError:
            # If running through e.g. Apache and this command fails, you
            # can try to start it manually, so we point that out
            if len(shlex.split(rconf_file)) > 1:
                rconf_arg = "'" + rconf_file.replace("'", r"\'") + "'"
            else:
                rconf_arg = rconf_file
            sys.stdout.write(
                (
                    "Note: Failed to start redis-server with an"
                    " OSError.\nYou could try to manually launch the"
                    " server by running:\nredis-server {}"
                ).format(rconf_arg)
            )
            raise
        time.sleep(0.2) # try to connect pretty quickly
        print("...we hope Redis is up now...")

        if not os.path.exists(rpid_file):
            print(
                (
                    "...looks like Redis failed to launch; check '{}'..."
                ).format(rlog_file)
            )

        # We'll try a second time to connect
        _REDIS = redis.Redis(
            'localhost',
            port,
            password=key,
            decode_responses=True
        )
        print("Reattempting connection to Redis server...")
        try:
            _REDIS.exists('test') # We just want to not get an error
            print("...connected successfully.")
        except redis.exceptions.ConnectionError: # Not ready yet
            print("...not ready on first attempt...")
            _REDIS = None
        except redis.exceptions.ResponseError: # bad password
            raise ValueError(
                "Your authentication key is not correct. Make sure"
                " you're not sharing the port you chose with another"
                " process!"
            )

        # We'll make one final attempt
        if _REDIS is None:
            time.sleep(2) # Give it plenty of time

            # Check for PID file
            if not os.path.exists(rpid_file):
                print(
                    (
                        "...looks like Redis is still not running;"
                        " check '{}'..."
                    ).format(rlog_file)
                )

            # Set up connection object
            _REDIS = redis.Redis(
                'localhost',
                port,
                password=key,
                decode_responses=True
            )
            # Attempt to connect
            print(
                "Reattempting connection to Redis server (last"
                " chance)..."
            )
            try:
                _REDIS.exists('test') # We just want to not get an error
                print("...connected successfully.")
            except redis.exceptions.ResponseError: # bad password
                raise ValueError(
                    "Your authentication key is not correct. Make sure"
                    " you're not sharing the port you chose with another"
                    " process!"
                )
            # This time, we'll let a connection error bubble out

    # At this point, _REDIS is a working connection.
