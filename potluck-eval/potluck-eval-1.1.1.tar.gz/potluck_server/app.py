#!/usr/local/bin/python
# -*- coding: UTF-8 -*-
"""
Flask WSGI web app for managing student submissions & grading them w/
potluck. Fork of Ocean server for Codder. Withholds feedback until after
the deadline, so the display of feedback is detached a bit from the
generation of feedback.

potluck_server/app.py

To run the server, the current directory must contain `ps_config.py` or
`ps_config.py.example` which will be copied to create `ps_config.py`. The
additional `secret` and `syntauth` files will be created automatically
using `os.urandom` if necessary; see `rundir` in the package directory
for an example.

Note that the `potluck` package must be installed, along with `flask`,
`jinja2`, and `flask_cas`. Additionally, `flask_talisman` and/or
`flask_seasurf` may be installed, and if present they will be used to
provide additional layers of security. Finally, if `pyopenssl` is
installed alongside `flask_talisman`, even when running in debug mode
HTTPS and the content-security-policy will be enabled, which helps spot
errors earlier at the cost of having to click through a security warning
from your browser about the self-signed certificate.

Students log in using CAS, select a pset, and submit one file per task
(where the filename is checked against a configurable list), and can view
their most recent submission, see any warnings on it, or even submit a
revision. Once the deadline + review period has passed (modulo
extensions), the full report from each student's last on-time submission
is made available. Main routes:

/ (route_index):
    Checks for CAS authentication and redirects to login page or to
    dashboard.

/dashboard (route_default_dash):
    Auto-redirects to the dashboard for the "current" course/semester
    based on configuration.

/**$course**/**$semester**/dashboard (route_dash):
    Main interface w/ rows for each pset. Each row has sub-rows for each
    task w/ upload button to submit the task and link to latest feedback
    for that task.

/**$course**/**$semester**/feedback/**$username**/**$phase**/**$pset**/
  **$task**
(route_feedback):
    Displays latest feedback for a given user/phase/pset/task.
    Pre-deadline this just shows any warnings.
    TODO: Add submit/resubmit mechanism to this page!

/**$course**/**$semester**/evaluate/**$username**/**$phase**/**$pset**/
  **$task**
(route_evaluate):
    Admin-only route that shows feedback for a given
    user/phase/pset/task, and allows the admin to enter a custom note
    that the student will see, and also to override the grade that will
    be entered on the gradesheet for that task. Note that grade overrides
    for revisions are still subject to the normal revision score cap in
    terms of their contributions to a final grade. Feedback for a
    non-submitted task may be overridden however.

/**$course**/**$semester**/submit/**$username**/**$pset**/**$task**
(route_submit):
    Form target for submissions; accepts valid submissions and redirects
    back to feedback page.

/**$course**/**$semester**/extension/**$pset** (route_extension):
    Request an extension for a pset (automatically grants the default
    extension; the extension always applies only to the initial deadline,
    not to revisions; and the extension applies to the whole problem set,
    not per-task).
    # TODO: Allow students to revoke requested extensions if they haven't
    # started using them yet.

/**$course**/**$semester**/solution/**$pset**/**$task** (route_solution):
    View the solution code for a particular task. Only available once a
    task is finalized (on a per-student basis to deal with extensions).

/**$course**/**$semester**/gradesheet/**$pset** (route_gradesheet):
    An overview of all grades for a specific problem set, visible only to
    admins.
    # TODO: Make this faster!
"""

# Attempts at 2/3 dual compatibility:
from __future__ import print_function

__version__ = "1.1.1"

import sys

# IF we're not in pyhton3:
if sys.version_info[0] < 3:
    reload(sys) # noqa F821
    # Set explicit default encoding
    sys.setdefaultencoding('utf-8')
    # Rename raw_input
    input = raw_input # noqa F821
    ModuleNotFound_or_Import_Error = ImportError
else:
    ModuleNotFound_or_Import_Error = ModuleNotFoundError


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


# Main imports
import os, subprocess, shutil # noqa E402
import datetime, time, random, copy, csv, re # noqa E402
import zipfile # noqa E402

import flask # noqa E402
import flask_cas # noqa E402
import jinja2 # noqa E402
import bs4 # noqa E402

from flask import json # noqa E402

from . import storage # noqa E402

# Load potluck modules:
import potluck.render # noqa: E402
import potluck.html_tools # noqa: E402
import potluck.time_utils # noqa: E402


#-------------#
# Setup setup #
#-------------#

class InitApp(flask.Flask):
    """
    A Flask app subclass which runs initialization functions right
    before app startup.
    """
    def __init__(self, *args, **kwargs):
        """
        Arguments are passed through to flask.Flask.__init__.
        """
        self.actions = []
        # Note: we don't use super() here since 2/3 compatibility is
        # too hard to figure out
        flask.Flask.__init__(self, *args, **kwargs)

    def init(self, action):
        """
        Registers an init action (a function which will be given the app
        object as its only argument). These functions will each be
        called, in order of registration, right before the app starts,
        withe the app_context active. Returns the action function
        provided, so that it can be used as a decorator, like so:

        ```py
        @app.init
        def setup_some_stuff(app):
            ...
        ```
        """
        self.actions.append(action)
        return action

    def setup(self):
        """
        Runs all registered initialization actions. If you're not running
        a debugging setup via the `run` method, you'll need to call this
        method yourself (e.g., in a .wsgi file).
        """
        with self.app_context():
            for action in self.actions:
                action(self)

    def run(self, *args, **kwargs):
        """
        Overridden run method runs our custom init actions with the app
        context first.
        """
        self.setup()
        # Note: we don't use super() here since 2/3 compatibility is
        # too hard to figure out
        flask.Flask.run(self, *args, **kwargs)


#-------#
# Setup #
#-------#

# Create our app object:
app = InitApp("potluck_server")


# Default configuration values if we really can't find a config file
DEFAULT_CONFIG = {
    "EVALUATION_BASE": '.',
    "POTLUCK_EVAL_PYTHON": None,
    "POTLUCK_EVAL_SCRIPT": None,
    "POTLUCK_EVAL_IMPORT_FROM": None,
    "COURSE_NAMES": { 'test_course': 'TEST COURSE' },
    "DEFAULT_COURSE": 'test_course',
    "DEFAULT_SEMESTER": 'fall2021',
    "SUPPORT_EMAIL": 'username@example.com',
    "SUPPORT_LINK": '<a href="mailto:username@example.com">User Name</a>',
    "NO_DEBUG_SSL": False,
    "CAS_SERVER": 'https://login.example.com:443',
    "CAS_AFTER_LOGIN": 'dashboard',
    "CAS_LOGIN_ROUTE": '/module.php/casserver/cas.php/login',
    "CAS_LOGOUT_ROUTE": '/module.php/casserver/cas.php/logout',
    "CAS_AFTER_LOGOUT": 'https://example.com/potluck',
    "CAS_VALIDATE_ROUTE": '/module.php/casserver/serviceValidate.php',
    "_ARCHIVE_BASE":
    '',
    "PSET_URLS": {
        'test_course': (
            'https://example.com/archive/test_course_{semester}/'
            'public_html/psets/{pset}'
        )
    },
    "TASK_URLS": {
        'test_course': (
            'https://example.com/archive/test_course_{semester}/'
            'public_html/psets/{pset}/{task}'
        )
    },
    "TASK_INFO_FILE": 'tasks.json',
    "ADMIN_INFO_FILE": 'potluck-admin.json',
    "ROSTER_FILE": 'roster.csv',
    "STUDENT_INFO_FILE": 'student-info.tsv',
    "SYNC_PORT": 51723,
    "FINAL_EVAL_TIMEOUT": 60,
    "USE_XVFB": False,
    "XVFB_SERVER_ARGS": "-screen 0 1024x768x24",
    "REMAP_STUDENT_INFO": {},
    "SCORE_BASIS": 100,
    "ROUND_SCORES_TO": 0,
    "EVALUATION_SCORES": {
        "excellent": 100,
        "complete": 95,
        "almost complete": 85,
        "partially complete": 75,
        "incomplete": 0,
        "__other__": None
    },
    "REVISION_MAX_SCORE": 95,
    "GRADE_THRESHOLDS": {
        "low": 75,
        "mid": 90
    }
}

# Loads configuration from file `ps_config.py`. If that file isn't
# present but `ps_config.py.example` is, copies the latter as the former
# first. Note that this CANNOT be run as an initialization pass, since
# the route definitions below require a working configuration.
try:
    sys.path.append('.')
    app.config.from_object('ps_config')
except Exception as e: # try copying the .example file?
    if os.path.exists('ps_config.py.example'):
        print("Creating new 'ps_config.py' from 'ps_config.py.example'.")
        shutil.copyfile('ps_config.py.example', 'ps_config.py')
        app.config.from_object('ps_config')
    else:
        print(
            "Neither 'ps_config.py' nor 'ps_config.py.example' is"
            " available, or there was an error in parsing them, so"
            " default configuration will be used."
        )
        print("CWD is:", os.getcwd())
        print("Error loading 'ps_config.py' was:", str(e))
        app.config.from_mapping(DEFAULT_CONFIG)
finally:
    sys.path.pop() # no longer need '.' on path...


@app.init
def setup_jinja_loader(app):
    """
    Set up templating with a custom loader that loads templates from the
    potluck package if it can't find them in this package. This is how
    we share the report template between potluck_server and potluck.
    """
    app.jinja_loader = jinja2.ChoiceLoader([
        jinja2.PackageLoader("potluck_server", "templates"),
        jinja2.PackageLoader("potluck", "templates")
    ])


@app.init
def enable_CAS(app):
    """
    Enable authentication via a Central Authentication Server.
    """
    global cas
    cas = flask_cas.CAS(app)


@app.init
def setup_potluck_reporting(app):
    """
    Setup for the potluck.render module (uses defaults).
    """
    potluck.render.setup()


@app.init
def create_secret_key(app):
    """
    Set secret key from secret file, or create a new secret key and
    write it into the secret file.
    """
    if os.path.exists("secret"):
        with open("secret", 'rb') as fin:
            app.secret_key = fin.read()
    else:
        print("Creating new secret key file 'secret'.")
        app.secret_key = os.urandom(16)
        with open("secret", 'wb') as fout:
            fout.write(app.secret_key)


@app.init
def initialize_storage_module(app):
    """
    Initialize file access and storage system.
    """
    storage.init(app.config)


@app.init
def ensure_required_folders(app):
    """
    Ensures required folders for the default course/semester.
    TODO: What about non-default courses/semesters? If they're fine, is
    this even necessary?
    """
    this_course = app.config.get("DEFAULT_COURSE", 'unknown')
    this_semester = app.config.get("DEFAULT_SEMESTER", 'unknown')
    storage.ensure_directory(
        storage.evaluation_directory(this_course, this_semester)
    )
    storage.ensure_directory(
        storage.submissions_folder(this_course, this_semester)
    )


#----------------#
# Security setup #
#----------------#

NOAUTH = False
USE_TALISMAN = True
if __name__ == "__main__":
    print("WARNING: Running in debug mode WITHOUT AUTHENTICATION!")
    input("Press enter to continue in debug mode.")
    # Disable login_required
    flask_cas.login_required = lambda f: f
    # Set up username workaround
    NOAUTH = True

    # If OpenSSL is available, we can use talisman even if running in
    # local debugging mode; otherwise we need to disable talisman.
    try:
        import OpenSSL
    except ModuleNotFound_or_Import_Error:
        USE_TALISMAN = False

    # Config may disable talisman
    if app.config.get('NO_DEBUG_SSL'):
        USE_TALISMAN = False


@app.init
def enable_talisman(app):
    """
    Enable talisman forced-HTTPS and other security headers if
    `flask_talisman` is available and it won't interfere with debugging.
    """
    talisman_enabled = False
    if USE_TALISMAN:
        try:
            import flask_talisman
            # Content-security policy settings
            csp = {
                'default-src': "'self'",
                'script-src': "'self' 'report-sample'",
                'style-src': "'self'",
                'img-src': "'self' data:"
            }
            flask_talisman.Talisman(
                app,
                content_security_policy=csp,
                content_security_policy_nonce_in=[
                    'script-src',
                    'style-src'
                ]
            )
            talisman_enabled = True
        except ModuleNotFound_or_Import_Error:
            print(
                "Warning: module flask_talisman is not available;"
                " security headers will not be set."
            )

    if talisman_enabled:
        print("Talisman is enabled.")
    else:
        print("Talisman is NOT enabled.")
        # Add csp_nonce global dummy since flask_talisman didn't
        app.add_template_global(
            lambda: "-nonce-disabled-",
            name='csp_nonce'
        )


@app.init
def setup_seasurf(app):
    """
    Sets up `flask_seasurf` to combat cross-site request forgery, if
    that module is available.
    """
    try:
        import flask_seasurf
        csrf = flask_seasurf.SeaSurf(app) # noqa F841
    except ModuleNotFound_or_Import_Error:
        print(
            "Warning: module flask_seasurf is not available; CSRF"
            " protection will not be enabled."
        )
        # Add csrf_token global dummy since flask_seasurf isn't available
        app.add_template_global(lambda: "-disabled-", name='csrf_token')


#---------#
# Helpers #
#---------#

def augment_arguments(route_function):
    """
    A decorator that modifies a route function to supply `username`,
    `is_admin`, `masquerade_as`, `effective_user`, and `task_info`
    keyword arguments along with the other arguments the route receives.
    Must be applied before app.route, and the first two parameters to the
    function must be the course and semester.

    Because flask/werkzeug routing requires function signatures to be
    preserved, we do some dirty work with compile and eval... As a
    result, this function can only safely be used to decorate functions
    that don't have any keyword arguments. Furthermore, the 5 augmented
    arguments must be the last 5 arguments that the function accepts.
    """
    def with_extra_arguments(*args, **kwargs):
        """
        A decorated route function which will be supplied with username,
        is_admin, masquerade_as, effective_user, and task_info parameters
        as keyword arguments after other arguments have been supplied.
        """
        # Get username
        if NOAUTH:
            username = "test"
        else:
            username = cas.username

        # Grab course + semester values
        course = kwargs.get('course', args[0] if len(args) > 0 else None)
        semester = kwargs.get(
            'semester',
            args[1 if 'course' not in kwargs else 0]
                if len(args) > 0 else None
        )

        if course is None or semester is None:
            flask.flash(
                (
                    "Error: Unable to get course and/or semester. Course"
                    " is {} and semester is {}."
                ).format(repr(course), repr(semester))
            )
            return error_response(
                course,
                semester,
                username,
                (
                    "Failed to access <code>course</code> and/or"
                    " <code>semester</code> values."
                )
            )

        # Get admin info
        admin_info = storage.get_admin_info(course, semester)
        if admin_info is None:
            flask.flash("Error loading admin info!")
            admin_info = {}

        # Check user privileges
        is_admin, masquerade_as = check_user_privileges(admin_info, username)

        # Effective username
        effective_user = masquerade_as or username

        # Get basic info on all psets/tasks
        task_info = storage.get_task_info(course, semester)
        if task_info is None: # error loading task info
            flask.flash("Error loading task info!")
            return error_response(
                course,
                semester,
                username,
                "Failed to load <code>tasks.json</code>."
            )

        # Set pause time for the task info
        set_pause_time(admin_info, task_info, username, masquerade_as)

        # Update the kwargs
        kwargs["username"] = username
        kwargs["is_admin"] = is_admin
        kwargs["masquerade_as"] = masquerade_as
        kwargs["effective_user"] = effective_user
        kwargs["task_info"] = task_info

        # Call the decorated function w/ the extra parameters we've
        # deduced.
        return route_function(*args, **kwargs)

    # Grab info on original function signature
    fname = route_function.__name__
    nargs = route_function.__code__.co_argcount
    argnames = route_function.__code__.co_varnames[:nargs - 5]

    # Create a function with the same signature:
    code = """\
def {name}({args}):
    return with_extra_arguments({args})
""".format(name=fname, args=', '.join(argnames))
    env = {"with_extra_arguments": with_extra_arguments}
    # 2/3 compatibility attempt...
    if sys.version_info[0] < 3:
        exec(code) in env, env
    else:
        exec(code, env, env) in env, env
    result = env[fname]

    # Preserve docstring
    result.__doc__ = route_function.__doc__

    # Return our synthetic function...
    return result


def goback(course, semester):
    """
    Returns a flask redirect aimed at either the page that the user came
    from, or the dashboard if that information isn't available.
    """
    if flask.request.referrer:
        # If we know where you came from, send you back there
        return flask.redirect(flask.request.referrer)
    else:
        # Otherwise back to the dashboard
        return flask.redirect(
            flask.url_for('route_dash', course=course, semester=semester)
        )


#-----------------#
# Route functions #
#-----------------#

@app.route('/')
def route_index():
    """
    Checks authentication and redirects to login page or to dashboard.
    """
    if NOAUTH or cas.username:
        return flask.redirect(flask.url_for('route_default_dash'))
    else:
        return flask.redirect(flask.url_for('cas.login'))


@app.route('/dashboard')
@flask_cas.login_required
def route_default_dash():
    """
    Redirects to dashboard w/ default class/semester.
    """
    return flask.redirect(
        flask.url_for(
            'route_dash',
            course=app.config.get("DEFAULT_COURSE", "unknown"),
            semester=app.config.get("DEFAULT_SEMESTER", "unknown")
        )
    )


@app.route('/<course>/<semester>/dashboard')
@flask_cas.login_required
@augment_arguments
def route_dash(
    course,
    semester,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Displays dashboard w/ links for submitting each pset/task & summary
    information of task grades.
    """

    # Add pset status and task feedback summaries to task info
    amend_task_info(course, semester, task_info, effective_user)

    # Render dashboard template
    return flask.render_template(
        'dashboard.j2',
        course_name=app.config.get("COURSE_NAMES", {}).get(course, course),
        course=course,
        semester=semester,
        username=username,
        is_admin=is_admin,
        masquerade_as=masquerade_as,
        effective_user=effective_user,
        task_info=task_info
    )


@app.route(
    '/<course>/<semester>/feedback/<target_user>/<phase>/<psid>/<taskid>'
)
@flask_cas.login_required
@augment_arguments
def route_feedback(
    course,
    semester,
    target_user,
    phase,
    psid,
    taskid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Displays feedback on a particular task of a particular problem set,
    for either the 'initial' or 'revision' phase.
    """
    if target_user != effective_user and not is_admin:
        return error_response(
            course,
            semester,
            username,
            "You are not allowed to view feedback for {}.".format(target_user)
        )
    elif target_user != effective_user:
        flask.flash("Viewing feedback for {}.".format(target_user))

    # From here on we treat the effective user as the target user
    effective_user = target_user

    # Check roster and flash a warning if we're viewing feedback for a
    # user who is not on the roster...
    try:
        roster = storage.get_roster(course, semester)
    except Exception as e:
        flask.flash(str(e))
        roster = None

    if roster is None:
        flask.flash(
            "Warning: could not fetch roster to check if this user is on"
            " it."
        )
    elif effective_user not in roster:
        flask.flash("Warning: this user is not on the roster!")

    # Get full feedback-ready pset and task objects
    ps_and_task = get_feedback_ps_and_task(
        task_info,
        course,
        semester,
        target_user,
        phase,
        psid,
        taskid
    )
    if isinstance(ps_and_task, ValueError):
        flask.flash(str(ps_and_task))
        return goback(course, semester)
    else:
        ps, task = ps_and_task

    if task["eval_status"] not in (
        None,
        "unknown",
        "initial",
        "in_progress",
        "error",
        "expired",
        "completed"
    ):
        msg = "Invalid evaluation status <code>{}</code>.".format(
            task["eval_status"]
        )
        flask.flash(msg)
        return error_response(course, semester, username, msg)

    # Set auto-refresh based on evaluation status
    if task["eval_status"] in ("unknown", "in_progress", "error"):
        refresh = 20
        flask.flash("""\
This page should refresh itself {refresh} seconds after loading
<span
 role="timer"
 aria-live="off"
 class="timer"
 data-time="{refresh}"
>
  {refresh}
</span>.""".format(refresh=refresh))
    else:
        refresh = None

    return flask.render_template(
        'feedback.j2',
        course_name=app.config.get("COURSE_NAMES", {}).get(course, course),
        course=course,
        semester=semester,
        username=username,
        is_admin=is_admin,
        masquerade_as=masquerade_as,
        effective_user=effective_user,
        target_user=target_user,
        phase=phase,
        ps=ps,
        task=task,
        task_info=task_info,
        fb_css=potluck.render.get_css(),
        fb_js=potluck.render.get_js(),
        support_link=app.config["SUPPORT_LINK"],
        refresh=refresh
    )


@app.route(
    '/<course>/<semester>/submit/<psid>/<taskid>',
    methods=['POST']
)
@flask_cas.login_required
@augment_arguments
def route_submit(
    course,
    semester,
    psid,
    taskid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Accepts a file submission for a task and initiates an evaluation
    process for that file. Figures out submission phase automatically
    based on task info, and assumes that the submission belongs to the
    authenticated user. However, if the authenticated user is an admin,
    the "phase" and "target_user" form values can override these
    assumptions. Redirects to the feedback page for the submitted task,
    or to the evaluation page if the user is an admin and is not the
    target user.

    Note: there are probably some nasty race conditions if the same user
    submits the same task simultaneously via multiple requests. We simply
    hope that that does not happen.
    """
    try:
        ps = get_ps_obj(task_info, psid)
    except ValueError as e:
        flask.flash(str(e))
        return goback(course, semester)

    try:
        task = get_task_obj(task_info, ps, taskid)
    except ValueError as e:
        flask.flash(str(e))
        return goback(course, semester)

    # Add status & time remaining info to pset
    amend_pset(course, semester, task_info, ps, effective_user)

    # Check for phase and/or target_user overrides in the form data if
    # the authenticated user is an admin
    target_user = effective_user
    phase = None
    destination_route = 'route_feedback'
    if is_admin:
        target_from_form = flask.request.form.get("target_user")
        if target_from_form not in ("", "auto"):
            target_user = target_from_form
        phase_from_form = flask.request.form.get("phase")
        if phase_from_form != "auto":
            phase = phase_from_form

        # Send admins to 'route_evaluate' instead of 'route_feedback' if
        # the target user is not the same as the actual user, whether
        # because of a masquerade or because of an explicit target user.
        if target_user != username:
            destination_route = 'route_evaluate'

    # Determine the phase from the pset state if we need to
    if phase is None:
        ps_state = ps['status']['state']
        if ps_state == "unknown":
            msg = "{} has no deadline.".format(psid)
            flask.flash(msg)
            return error_response(course, semester, username, msg)
        elif ps_state in ("unreleased", "released"):
            phase = "initial"
        elif ps_state in ("under_review", "revisable"):
            phase = "revision"
            if ps_state == "under_review":
                flask.flash(
                    "You should probably wait until the review period is"
                  + " over and view feedback on your initial submission"
                  + " before submitting a revision."
                )
        elif ps_state == "final":
            flask.flash(
                "We are no longer accepting new submissions for {}.".format(
                    psid
                )
            )
            phase = "belated"

    # There are no provisions for displaying feedback on late files, so
    # we redirect to the latest revision in that case.
    # TODO: Actually generate feedback for belated files, and allow
    # admins to bump that feedback over to the revision category? What
    # about solution permissions in this case though?
    destination_phase = phase
    if destination_phase == "belated":
        destination_phase = "revision"

    # Ensure that there's a file being submitted
    files = flask.request.files
    if ('upload' not in files or files['upload'].filename == ''):
        flask.flash("You must choose a file to submit.")
        return goback(course, semester)
    else:
        uploaded = files['upload']

        # Check for an in-flight grading process for this task
        ts, _, _, status = storage.get_inflight(
            course,
            semester,
            effective_user,
            phase,
            psid,
            taskid
        )

        # If the submission is already being evaluated, or if we couldn't
        # figure out whether that was the case, we can't start another
        # evaluation process!
        if ts == "error":
            flask.flash(
                (
                    "ERROR: Failed to check evaluation status. Try"
                  + " refreshing this page, and if the problem persists,"
                  + " contact {}."
                ).format(app.config["SUPPORT_LINK"])
            )
            return flask.redirect(
                flask.url_for(
                    destination_route,
                    course=course,
                    semester=semester,
                    target_user=effective_user,
                    phase=destination_phase,
                    psid=psid,
                    taskid=taskid
                )
            )
        elif status in ("initial", "in_progress"):
            flask.flash(
                (
                    "ERROR: Task {taskid} for pset {psid} is currently being"
                  + " evaluated. You must wait until that process is"
                  + " complete before uploading a revised submission. This"
                  + " should take no longer than"
                  + " {timeout} seconds."
                ).format(
                    taskid=taskid,
                    psid=psid,
                    timeout=app.config['FINAL_EVAL_TIMEOUT']
                )
            )
            return flask.redirect(
                flask.url_for(
                    destination_route,
                    course=course,
                    semester=semester,
                    target_user=effective_user,
                    phase=destination_phase,
                    psid=psid,
                    taskid=taskid
                )
            )
        # else we assume the status is some final status or None meaning
        # this is the first submission

        # Record the time spent value
        if (
            'time_spent' not in flask.request.form
         or flask.request.form["time_spent"] == ""
        ):
            flask.flash(
                "You did not give us an estimate of how much time this"
              + " task took you. Please re-submit and enter a time spent"
              + " value so that we can help advise future students about"
              + " how long this task will take them."
            )
            time_spent = ""
        else:
            time_spent = flask.request.form["time_spent"]

        storage.record_time_spent(
            course,
            semester,
            target_user,
            phase,
            psid,
            taskid,
            time_spent
        )

        # Save the file with the correct filename, ignoring the name that
        # the user uploaded.
        target = get_submission_filename(
            course,
            semester,
            task_info,
            target_user,
            phase,
            psid,
            taskid
        )
        destdir, _ = os.path.split(target)
        storage.ensure_directory(destdir)
        storage.make_way_for(target)
        uploaded.save(target)
        # TODO: Flash categories
        if phase == "belated":
            flask.flash(
                (
                    "Uploaded LATE '{filename}' for {psid} {taskid}."
                  + " This submission will not be evaluated."
                ).format(
                    filename=uploaded.filename,
                    psid=psid,
                    taskid=taskid
                )
            )
        else:
            flask.flash(
                (
                    "Successfully uploaded {phase} submission"
                  + " '{filename}' for {psid} {taskid}."
                ).format(
                    phase=phase,
                    filename=uploaded.filename,
                    psid=psid,
                    taskid=taskid
                )
            )
        # Flash a warning if the uploaded filename seems wrong
        if uploaded.filename != task["target"]:
            flask.flash(
                (
                    "Warning: you uploaded a file named '{filename}',"
                  + " but {taskid} in {psid} requires a file named"
                  + " '{reqname}'. Are you sure you uploaded the"
                  + " correct file?"
                ).format(
                    filename=uploaded.filename,
                    psid=psid,
                    taskid=taskid,
                    reqname=task["target"]
                )
            )

        # Log setup
        ts, logfile, reportfile, _ = storage.put_inflight(
            course,
            semester,
            target_user,
            phase,
            psid,
            taskid
        )

        if ts == "error":
            flask.flash(
                (
                    "ERROR: Failed to check evaluation status. Try"
                  + " refreshing this page, and if the problem persists,"
                  + " contact {}."
                ).format(app.config["SUPPORT_LINK"])
            )
            return flask.redirect(
                flask.url_for(
                    destination_route,
                    course=course,
                    semester=semester,
                    target_user=target_user,
                    phase=destination_phase,
                    psid=psid,
                    taskid=taskid
                )
            )
        elif ts is None: # another grading process is already in-flight
            flask.flash(
                (
                    "ERROR: Task {taskid} for pset {psid} is currently being"
                  + " evaluated. You must wait until that process is"
                  + " complete before uploading another submission. This"
                  + " should take no longer than {timeout} seconds."
                ).format(
                    psid=psid,
                    taskid=taskid,
                    timeout=app.config['FINAL_EVAL_TIMEOUT']
                )
            )
            return flask.redirect(
                flask.url_for(
                    destination_route,
                    course=course,
                    semester=semester,
                    target_user=target_user,
                    phase=destination_phase,
                    psid=psid,
                    taskid=taskid
                )
            )

        # Start the evaluation process (we don't wait for it)
        launch_potluck(
            course,
            semester,
            target_user,
            taskid,
            target,
            logfile,
            reportfile
        )

    return flask.redirect(
        flask.url_for(
            destination_route,
            course=course,
            semester=semester,
            target_user=target_user,
            phase=destination_phase,
            psid=psid,
            taskid=taskid
        )
    )


def which_exe(target, cwd='.'):
    """
    shutil.which 2/3 shim. Prepends cwd to current PATH.
    """
    if sys.version_info[0] < 3:
        finder = subprocess.Popen(
            [ 'which', target ],
            cwd=cwd,
            stdout=subprocess.PIPE
        )
        out, err = finder.communicate()
        return out.strip()
    else:
        return shutil.which(
            "potluck_eval",
            path=cwd + ':' + os.getenv("PATH")
        )


def launch_potluck(
    course,
    semester,
    username,
    taskid,
    target_file,
    logfile,
    reportfile,
    wait=False
):
    """
    Launches the evaluation process. By default this is fire-and-forget;
    we'll look for the output file to determine whether it's finished or
    not. However, by passing wait=True you can have the function wait for
    the process to terminate before returning.
    """
    eval_dir = storage.evaluation_directory(course, semester)

    if app.config.get("POTLUCK_EVAL_PYTHON") is None:
        python = []
    else:
        python = [ app.config["POTLUCK_EVAL_PYTHON"] ]

    if app.config["POTLUCK_EVAL_SCRIPT"] is None:
        potluck_exe = which_exe("potluck_eval", eval_dir)
    else:
        potluck_exe = os.path.join(
            os.getcwd(),
            app.config["POTLUCK_EVAL_SCRIPT"]
        )

    potluck_args = [
        "--task", taskid,
        "--user", username,
        "--target", os.path.abspath(target_file),
        "--outfile", os.path.abspath(reportfile),
        "--clean",
    ]

    if app.config["POTLUCK_EVAL_IMPORT_FROM"] is not None:
        import_dir = os.path.join(
            os.getcwd(),
            app.config["POTLUCK_EVAL_IMPORT_FROM"]
        )
        potluck_args.extend(["--import-from", import_dir])
    with open(logfile, 'wb') as log:
        if app.config["USE_XVFB"]:
            # Virtualise frame buffer for programs with graphics, so
            # they don't need to create Xwindow windows
            # '--auto-servernum', # create a new server??
            # '--auto-display',
            # [2019/02/08] Peter: try this instead per comment in -h?
            xvfb_err_log = os.path.splitext(logfile)[0] + ".xvfb_errors.log"
            full_args = (
                [
                    'xvfb-run',
                    '-d',
                    # [2019/02/11] Lyn: --auto-display doesn't work but -d
                    # does (go figure, since they're supposed to be
                    # synonyms!)
                    '-e', # --error-file doesn't work
                    xvfb_err_log,
                    '--server-args',
                    app.config["XVFB_SERVER_ARGS"], # screen properties
                    '--',
                ] + python + [
                    potluck_exe,
                ]
              + potluck_args
            )
        else:
            # Raw potluck launch without XVFB
            full_args = python + [ potluck_exe ] + potluck_args

        log.write(
            ("Full args: " + repr(full_args) + '\n').encode("utf-8")
        )
        log.flush()

        p = subprocess.Popen(
            full_args,
            cwd=eval_dir,
            stdout=log,
            stderr=log,
        )

        if wait:
            p.wait()


@app.route('/<course>/<semester>/extension/<psid>', methods=['GET'])
@flask_cas.login_required
@augment_arguments
def route_extension(
    course,
    semester,
    psid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Requests (and automatically grants) the default extension on the
    given problem set. The extension is applied to the initial phase
    only. For now, nonstandard extensions and revision extensions must be
    applied by hand-editing JSON files in the `extensions/` directory.
    """
    try:
        ps = get_ps_obj(task_info, psid)
    except ValueError as e:
        flask.flash(str(e))
        return goback(course, semester)

    # Add status & time remaining info to pset
    amend_pset(course, semester, task_info, ps, effective_user)
    # TODO: triple-check the possibility of requesting an extension
    # during the period an extension would grant you but after the
    # initial deadline?

    # Grant the extension
    if (
        ps["status"]["state"] in ("unreleased", "released")
    and ps["status"]["initial_extension"] == 0
    ):
        succeeded = storage.set_extension(
            course,
            semester,
            effective_user,
            psid,
            "initial"
        )
        if succeeded:
            flask.flash("Extension granted for {}.".format(psid))
        else:
            flask.flash("Failed to grant extension for {}.".format(psid))
    elif ps["status"]["state"] not in ("unreleased", "released"):
        flask.flash(
            (
                "It is too late to request an extension for {}. You must"
                " request extensions before the deadline for each pset."
            ).format(psid)
        )
    elif ps["status"]["initial_extension"] != 0:
        flask.flash(
            "You have already been granted an extension on {}.".format(psid)
        )
    else:
        flask.flash(
            "You cannot take an extension on {}.".format(psid)
        )

    # Send them back to the dashboard or wherever they came from
    return goback(course, semester)


@app.route(
    '/<course>/<semester>/set_extensions/<target_user>/<psid>',
    methods=['POST']
)
@flask_cas.login_required
@augment_arguments
def route_set_extensions(
    course,
    semester,
    target_user,
    psid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Form target for editing extensions for a particular user/pset. Only
    admins can use this route. Can be used to set custom extension values
    for both initial and revised deadlines.
    """
    if not is_admin:
        flask.flash("Only admins can grant extensions.")
        return goback(course, semester)

    # Get initial/revision extension values from submitted form values
    try:
        initial = int(flask.request.form["initial"])
    except Exception:
        initial = None

    try:
        revision = int(flask.request.form["revision"])
    except Exception:
        revision = None

    # At least one or the other needs to be valid
    if initial is None and revision is None:
        flask.flash(
            (
                "To set extensions, you must specify either an initial"
                " or a revision value, and both values must be integers."
            )
        )
        return goback(course, semester)

    # Grant the extension(s)
    if initial is not None:
        # TODO: Use only_from here to help prevent race conditions on
        # loading the HTML page that displays the extension values
        succeeded = storage.set_extension(
            course,
            semester,
            target_user,
            psid,
            "initial",
            initial
        )
        if succeeded:
            flask.flash(
                "Set {}h initial extension for {} on {}.".format(
                    initial,
                    target_user,
                    psid
                )
            )
        else:
            flask.flash(
                "Failed to grant initial extension for {} on {} (try again?)."
                .format(target_user, psid)
            )

    if revision is not None:
        succeeded = storage.set_extension(
            course,
            semester,
            target_user,
            psid,
            "revision",
            revision
        )
        if succeeded:
            flask.flash(
                "Set {}h revision extension for {} on {}.".format(
                    revision,
                    target_user,
                    psid
                )
            )
        else:
            flask.flash(
                "Failed to grant revision extension for {} on {} (try again?)."
                .format(target_user, psid)
            )

    # Send them back to the dashboard or wherever they came from
    return goback(course, semester)


@app.route(
    '/<course>/<semester>/manage_extensions/<target_user>',
    methods=['GET']
)
@flask_cas.login_required
@augment_arguments
def route_manage_extensions(
    course,
    semester,
    target_user,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Admin-only route that displays a list of forms for each pset showing
    current extension values and allowing the user to edit them and press
    a button to update them.
    """
    if not is_admin:
        flask.flash("Only admins can grant extensions.")
        return goback(course, semester)

    # Get extensions info for the target user for all psets
    amend_task_info(course, semester, task_info, target_user)

    return flask.render_template(
        'extension_manager.j2',
        course_name=app.config.get("COURSE_NAMES", {}).get(course, course),
        course=course,
        semester=semester,
        username=username,
        is_admin=is_admin,
        masquerade_as=masquerade_as,
        task_info=task_info,
        target_user=target_user
    )


@app.route(
    '/<course>/<semester>/set_eval/<target_user>/<phase>/<psid>/<taskid>',
    methods=['POST']
)
@flask_cas.login_required
@augment_arguments
def route_set_evaluation(
    course,
    semester,
    target_user,
    phase,
    psid,
    taskid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Form target for editing custom evaluation info for a particular
    user/pset. Only admins can use this route. Can be used to set custom
    notes and/or a grade override for a particular user/phase/pset/task.
    """
    if not is_admin:
        # TODO: Grader role!
        flask.flash("Only admins can edit evaluations.")
        return goback(course, semester)

    # Get initial/revision extension values from submitted form values
    try:
        notes = flask.request.form["notes_md"]
    except Exception:
        notes = None

    try:
        override = flask.request.form["override"]
    except Exception:
        override = None

    # Attempt to convert to a number
    if override is not None:
        try:
            override = float(override)
        except Exception:
            pass

    # At least one or the other needs to be valid
    if notes is None and override is None:
        flask.flash(
            (
                "To set an evaluation, you must specify at least either"
                " a notes string or a grade override."
            )
        )
        return goback(course, semester)

    # Grant the extension(s)
    if notes is None:
        notes = ''

    # Override can be none and it will default properly to no override

    # TODO: Create and use an only_from mechanism here to help
    # prevent race conditions on loading the HTML page that displays
    # the old evaluation values?
    succeeded = storage.set_evaluation(
        course,
        semester,
        target_user,
        phase,
        psid,
        taskid,
        notes,
        override
    )
    if succeeded:
        flask.flash(
            "Updated evaluation for {} on {} {} {} submission.".format(
                target_user,
                psid,
                taskid,
                phase
            )
        )
    else:
        flask.flash(
            (
                "Failed to update evaluation for {} on {} {} {}"
                " submission."
            ).format(
                target_user,
                psid,
                taskid,
                phase
            )
        )

    # Send them to the evaluation-editing page
    return flask.redirect(
        flask.url_for(
            'route_evaluate',
            course=course,
            semester=semester,
            target_user=target_user,
            phase=phase,
            psid=psid,
            taskid=taskid
        )
    )


@app.route(
    '/<course>/<semester>/evaluate/<target_user>/<phase>/<psid>/<taskid>',
    methods=['GET']
)
@flask_cas.login_required
@augment_arguments
def route_evaluate(
    course,
    semester,
    target_user,
    phase,
    psid,
    taskid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Displays student feedback and also includes a form at the top for
    adding a custom note and/or overriding the grade.
    """
    if not is_admin:
        # TODO: Grader role!
        flask.flash("Only admins can evaluate submissions.")
        return goback(course, semester)

    # Check roster and flash a warning if we're viewing feedback for a
    # user who is not on the roster...
    try:
        roster = storage.get_roster(course, semester)
    except Exception as e:
        flask.flash(str(e))
        roster = None

    if roster is None:
        flask.flash(
            "Warning: could not fetch roster to check if this user is on"
            " it."
        )
    elif target_user not in roster:
        flask.flash("Warning: this user is not on the roster!")

    # Get full feedback info
    ps_and_task = get_feedback_ps_and_task(
        task_info,
        course,
        semester,
        target_user,
        phase,
        psid,
        taskid
    )
    if isinstance(ps_and_task, ValueError):
        flask.flash(str(ps_and_task))
        return goback(course, semester)
    else:
        ps, task = ps_and_task

    return flask.render_template(
        'evaluate.j2',
        course_name=app.config.get("COURSE_NAMES", {}).get(course, course),
        course=course,
        semester=semester,
        username=username,
        is_admin=is_admin,
        masquerade_as=masquerade_as,
        effective_user=effective_user,
        target_user=target_user,
        phase=phase,
        ps=ps,
        task=task,
        task_info=task_info,
        fb_css=potluck.render.get_css(),
        fb_js=potluck.render.get_js(),
        support_link=app.config["SUPPORT_LINK"]
    )


@app.route('/<course>/<semester>/solution/<psid>/<taskid>', methods=['GET'])
@flask_cas.login_required
@augment_arguments
def route_solution(
    course,
    semester,
    psid,
    taskid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Visible only once a task's status is final, accounting for all
    extensions, and if the active user has an evaluated submission for
    the task, or another task in the same pool (or if they're an admin).
    Shows the solution code for a particular task, including a formatted
    version and a link to download the .py file.
    """
    try:
        ps = get_ps_obj(task_info, psid)
    except ValueError as e:
        flask.flash("ValueError: " + str(e))
        return goback(course, semester)

    # Add status & time remaining info to pset and objects
    amend_pset(course, semester, task_info, ps, effective_user)

    # Grab task object for this task
    try:
        task = get_task_obj(task_info, ps, taskid)
    except ValueError as e:
        flask.flash("ValueError: " + str(e))
        return goback(course, semester)

    # Find tasks in the same pool as this one:
    if "pool" in task:
        tasks_in_pool = [
            tentry["id"]
            for tentry in ps["tasks"]
            if tentry.get("pool") == task["pool"]
        ]
    else:
        tasks_in_pool = [ task["id"] ]

    # Grab task objects for each task in our pool and amend them:
    submitted_to_pool = False
    for taskid in tasks_in_pool:
        try:
            tobj = get_task_obj(task_info, ps, taskid)
        except ValueError as e:
            flask.flash("ValueError: " + str(e))
            return goback(course, semester)

        initial = tobj
        revised = copy.deepcopy(tobj)

        amend_task(
            course,
            semester,
            task_info,
            psid,
            initial,
            effective_user,
            "initial"
        )
        if initial.get("submitted"):
            submitted_to_pool = True
            break

        amend_task(
            course,
            semester,
            task_info,
            psid,
            revised,
            effective_user,
            "revision"
        )
        if revised.get("submitted"):
            submitted_to_pool = True
            break

    # Check roster so that only students on the roster can view solutions
    # (we don't want future-semester students viewing previous-semester
    # solutions!).
    try:
        roster = storage.get_roster(course, semester)
    except Exception as e:
        flask.flash(str(e))
        roster = None

    if roster is None:
        msg = "Failed to load <code>roster.csv</code>."
        flask.flash(msg)
        return error_response(course, semester, username, msg)

    if ps["status"]["state"] != "final":
        if is_admin:
            flask.flash(
                "Viewing solution code as admin; solution is not"
              + " visible to students until revision period is over."
            )
        else:
            flask.flash(
                (
                    "You cannot view the solutions for {pset} {task}"
                  + " until the revision period is over."
                ).format(pset=psid, task=taskid)
            )
            return goback(course, semester)

    elif effective_user not in roster: # not on the roster
        if is_admin:
            flask.flash(
                (
                    "Viewing solution code as admin; solution is not"
                  + " visible to user {} as they are not on the roster"
                  + " for this course/semester."
                ).format(effective_user)
            )
        else:
            flask.flash(
                (
                    "You cannot view solutions for {course} {semester}"
                  + " because you are not on the roster for that class."
                ).format(course=course, semester=semester)
            )
            return goback(course, semester)

    elif not (
        app.config.get("DISPLAY_UNSUBMITTED_SOLUTIONS")
     or submitted_to_pool
    ):
        # This user hasn't submitted this task, so we'd like to make it
        # possible for them to get an extension later without worrying about
        # whether they've accessed solution code in the mean time.
        if is_admin:
            flask.flash(
                (
                    "Viewing solution code as admin; solution is not"
                  + " visible to user {} as they don't have a submission"
                  + " for this task or another task in this pool."
                ).format(effective_user)
            )
        else:
            flask.flash(
                (
                    "You cannot view the solution for {} {} becuase you"
                    " haven't submitted that task or any task in the"
                    " same pool."
                ).format(psid, taskid)
            )
            return goback(course, semester)

    # At this point, we've verified it's okay to display the solution:
    # the pset is finalized, and the user is an admin or at least on the
    # roster for this particular course/semester, and the user has a
    # submission for this task, or at least to another task in the same
    # pool.

    # We'd like the feedback CSS & JS because we're going to render code
    # as HTML using potluck.
    fb_css = potluck.render.get_css()
    fb_js = potluck.render.get_js()

    # TODO: This feels a bit hardcoded... can we do better?
    # TODO: Multi-file stuff!
    soln_filename = os.path.join(
        storage.evaluation_directory(course, semester),
        "specs",
        task["id"],
        "soln",
        task["target"]
    )

    with open(soln_filename, 'r') as fin:
        soln_code = fin.read()

    soln_code_html = potluck.render.render_code(
        taskid,
        soln_filename,
        soln_code
    )

    return flask.render_template(
        'solution.j2',
        course_name=app.config.get("COURSE_NAMES", {}).get(course, course),
        course=course,
        semester=semester,
        username=username,
        is_admin=is_admin,
        masquerade_as=masquerade_as,
        effective_user=effective_user,
        ps=ps,
        task=task,
        task_info=task_info,
        soln_code=soln_code,
        rendered_soln=soln_code_html,
        fb_css=fb_css,
        fb_js=fb_js,
        support_link=app.config["SUPPORT_LINK"]
    )


@app.route(
    '/<course>/<semester>/starter/<taskid>.zip',
    methods=['GET']
)
@flask_cas.login_required
def route_starter_zip(course, semester, taskid):
    # TODO: This feels a bit hardcoded... can we do better?
    # Compute filenames and directories
    starter_dir = os.path.join(
        storage.evaluation_directory(course, semester),
        "specs",
        taskid,
        "starter"
    )
    starter_files = os.listdir(starter_dir)
    starter_zip = os.path.join(
        storage.evaluation_directory(course, semester),
        "specs",
        taskid,
        taskid + ".zip"
    )

    # Compute most-recent-modification time for any starter file
    updated_at = None
    for file in starter_files:
        full_path = os.path.join(starter_dir, file)
        mtime = os.stat(full_path).st_mtime
        if updated_at is None or updated_at < mtime:
            updated_at = mtime

    # Check for freshness
    if (
        not os.path.exists(starter_zip)
     or os.stat(starter_zip).st_mtime < updated_at
    ):
        # Zip up all the starter files, erasing and overwriting the old
        # zip file if it was there before
        with zipfile.ZipFile(starter_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
            for file in starter_files:
                full_path = os.path.join(starter_dir, file)
                zout.write(full_path, taskid + '/' + file)

    with open(starter_zip, 'rb') as fin:
        raw_bytes = fin.read()

    return flask.Response(raw_bytes, mimetype='application/zip')


@app.route('/<course>/<semester>/gradesheet/<psid>', methods=['GET'])
@flask_cas.login_required
@augment_arguments
def route_gradesheet(
    course,
    semester,
    psid,
    # Augmented arguments
    username,
    is_admin,
    masquerade_as,
    effective_user,
    task_info
):
    """
    Visible by admins only, this route displays an overview of the status
    of every student on the roster, with links to the feedback views for
    each student/pset/phase/task.
    """
    if not is_admin:
        flask.flash("You do not have permission to view the gradesheet.")
        return goback(course, semester)

    # Create base task info from logged-in user's perspective
    base_task_info = copy.deepcopy(task_info)
    amend_task_info(course, semester, base_task_info, username)

    try:
        ps = get_ps_obj(base_task_info, psid)
    except ValueError as e:
        flask.flash(str(e))
        return goback(course, semester)

    # Get the roster
    try:
        roster = storage.get_roster(course, semester)
    except Exception as e:
        flask.flash(str(e))
        roster = None

    if roster is None:
        msg = "Failed to load <code>roster.csv</code>."
        flask.flash(msg)
        return error_response(course, semester, username, msg)

    initial_task_times = {}
    revision_task_times = {}
    rows = []
    for stid in sorted(
        roster,
        key=lambda stid: (
            roster[stid]["course_section"],
            roster[stid]["sortname"]
        )
    ):
        row = roster[stid]
        row_info = copy.deepcopy(task_info)
        row["task_info"] = row_info
        psobj = get_ps_obj(row_info, psid)
        row["this_pset"] = psobj

        amend_pset_and_tasks(
            course,
            semester,
            row_info,
            psobj,
            row["username"]
        )

        psobj["total_time"] = 0

        for taskobj in psobj["tasks"]:
            taskid = taskobj["id"]
            time_spent = taskobj["time_spent"]
            if time_spent is not None:
                time_val = time_spent["time_spent"]
                if taskid not in initial_task_times:
                    initial_task_times[taskid] = {}

                if isinstance(time_val, (float, int)):
                    initial_task_times[taskid][row["username"]] = time_val
                    taskobj["initial_time_val"] = time_val
                    if isinstance(psobj["total_time"], (int, float)):
                        psobj["total_time"] += time_val
                elif isinstance(time_val, str) and time_val != "":
                    taskobj["initial_time_val"] = time_val
                    psobj["total_time"] = "?"
                else: # empty string or None or the like
                    taskobj["initial_time_val"] = "?"
            else:
                taskobj["initial_time_val"] = 0

            rev_time_spent = taskobj.get("revision", {}).get("time_spent")
            if rev_time_spent is not None:
                rev_time_val = rev_time_spent["time_spent"]
                if taskid not in revision_task_times:
                    revision_task_times[taskid] = {}

                if isinstance(rev_time_val, (float, int)):
                    revision_task_times[taskid][row["username"]] = rev_time_val
                    taskobj["revision_time_val"] = rev_time_val
                    if isinstance(psobj["total_time"], (int, float)):
                        psobj["total_time"] += rev_time_val
                    if isinstance(taskobj["initial_time_val"], (int, float)):
                        taskobj["combined_time_val"] = (
                            taskobj["initial_time_val"]
                          + rev_time_val
                        )
                    elif ( # initial was a non-empty string
                        isinstance(taskobj["initial_time_val"], str)
                    and taskobj["initial_time_val"] not in ("", "?")
                    ):
                        taskobj["combined_time_val"] = "?"
                    else: # empty string or None or the like
                        taskobj["combined_time_val"] = rev_time_val

                elif isinstance(rev_time_val, str) and rev_time_val != "":
                    taskobj["revision_time_val"] = rev_time_val
                    psobj["total_time"] = "?"
                    taskobj["combined_time_val"] = "?"

                else: # empty string or None or the like
                    taskobj["revision_time_val"] = "?"
                    taskobj["combined_time_val"] = taskobj["initial_time_val"]

            else: # no rev time spent
                taskobj["revision_time_val"] = "?"
                taskobj["combined_time_val"] = taskobj["initial_time_val"]

        rows.append(row)

    aggregate_times = {
        phase: {
            "average": { "pset": 0 },
            "median": { "pset": 0 },
            "75th": { "pset": 0 },
        }
        for phase in ("initial", "revision")
    }
    aggregate_times["all"] = {}
    for phase, times_group in [
        ("initial", initial_task_times),
        ("revision", revision_task_times)
    ]:
        for taskid in times_group:
            times = list(times_group[taskid].values())
            if len(times) == 0:
                avg = None
                med = None
                qrt = None
            elif len(times) == 1:
                avg = times[0]
                med = times[0]
                qrt = times[0]
            else:
                avg = sum(times) / len(times)
                med = percentile(times, 50)
                qrt = percentile(times, 75)

            aggregate_times[phase]["average"][taskid] = avg
            aggregate_times[phase]["median"][taskid] = med
            aggregate_times[phase]["75th"][taskid] = qrt

            if avg is not None:
                aggregate_times[phase]["average"]["pset"] += avg
                aggregate_times[phase]["median"]["pset"] += med
                aggregate_times[phase]["75th"]["pset"] += qrt

    # Compute total times taking zero-revision-times into account
    total_timespent_values = []
    for student in [row["username"] for row in roster.values()]:
        total_timespent = 0
        for taskobj in psobj["tasks"]:
            taskid = taskobj["id"]
            this_task_initial_times = initial_task_times.get(taskid, {})
            this_task_revision_times = revision_task_times.get(taskid, {})
            if student in this_task_initial_times:
                total_timespent += this_task_initial_times[student]
            if student in this_task_revision_times:
                total_timespent += this_task_revision_times[student]
        if total_timespent > 0:
            total_timespent_values.append(total_timespent)

    if len(total_timespent_values) == 0:
        avg = 0
        med = 0
        qrt = 0
    elif len(total_timespent_values) == 1:
        avg = total_timespent_values[0]
        med = total_timespent_values[0]
        qrt = total_timespent_values[0]
    else:
        avg = sum(total_timespent_values) / len(total_timespent_values)
        med = percentile(total_timespent_values, 50)
        qrt = percentile(total_timespent_values, 75)

    aggregate_times["all"]["average"] = avg
    aggregate_times["all"]["median"] = med
    aggregate_times["all"]["75th"] = qrt

    # Get the student info
    try:
        student_info = storage.get_student_info(course, semester)
    except Exception as e:
        flask.flash(str(e))
        student_info = None

    return flask.render_template(
        'gradesheet.j2',
        course_name=app.config.get("COURSE_NAMES", {}).get(course, course),
        course=course,
        semester=semester,
        username=username,
        is_admin=is_admin,
        masquerade_as=masquerade_as,
        task_info=task_info,
        ps=ps,
        roster=rows,
        student_info=student_info,
        aggregate_times=aggregate_times
    )


#---------#
# Helpers #
#---------#

def error_response(course, semester, username, cause):
    """
    Shortcut for displaying major errors to the users so that they can
    bug the support line instead of just getting a pure 404.
    """
    return flask.render_template(
        'error.j2',
        course_name=app.config.get("COURSE_NAMES", {}).get(course, course),
        course=course,
        semester=semester,
        username=username,
        announcements="Piazza",
        support_link=app.config["SUPPORT_LINK"],
        error=cause,
        task_info={}
    )


def get_ps_obj(task_info, psid):
    """
    Gets the pset object with the given ID. Raises a ValueError if there
    is no such pset object, or if there are multiple matches.
    """
    psmatches = [ps for ps in task_info["psets"] if ps["id"] == psid]
    if len(psmatches) == 0:
        raise ValueError("Unknown problem set '{}'".format(psid))
    elif len(psmatches) > 1:
        raise ValueError("Multiple problem sets with ID '{}'!".format(psid))
    else:
        return psmatches[0]


def get_task_obj(task_info, ps_obj, taskid, redirect=Exception):
    """
    Extracts a task object with the given ID from the given task info and
    pset objects, merging pset-specific fields with universal task
    fields. Raises a ValueError if there is no matching task object or if
    there are multiple matches.
    """
    universal = task_info["tasks"].get(taskid, None)
    taskmatches = [task for task in ps_obj["tasks"] if task["id"] == taskid]
    if len(taskmatches) == 0:
        raise ValueError(
            "Problem set {} has no task '{}'".format(ps_obj["id"], taskid)
        )
    elif universal is None:
        raise ValueError(
            (
                "Problem set {} has a task '{}' but that task has no"
                " universal specification."
            ).format(ps_obj["id"], taskid)
        )
    elif len(taskmatches) > 1:
        raise ValueError(
            "Multiple tasks in problem set {} with ID '{}'!".format(
                ps_obj["id"],
                taskid
            )
        )
    else:
        result = {}
        result.update(universal)
        result.update(taskmatches[0])
        return result


def check_user_privileges(admin_info, username):
    """
    Returns a pair containing a boolean indicating whether a user is an
    admin or not, and either None, or a string indicating the username
    that the given user is masquerading as.

    Requires admin info as returned by get_admin_info.
    """
    admins = admin_info.get("admins", [])
    is_admin = username in admins

    masquerade_as = None
    # Only admins can possibly masquerade
    if is_admin:
        masquerade_as = admin_info.get("MASQUERADE", {}).get(username)
        # You cannot masquerade as an admin
        if masquerade_as in admins:
            flask.flash("Error: You cannot masquerade as another admin!")
            masquerade_as = None
    elif admin_info.get("MASQUERADE", {}).get(username):
        print(
            (
                "Warning: User '{}' cannot masquerade because they are"
              + "not an admin."
            ).format(username)
        )

    return (is_admin, masquerade_as)


def set_pause_time(admin_info, task_info, username, masquerade_as=None):
    """
    Sets the PAUSE_AT value in the given task_info object based on any
    PAUSE_USERS entries for either the given true username or the given
    masquerade username. The pause value for the username overrides the
    value for the masqueraded user, so that by setting PAUSE_AT for an
    admin account plus creating a masquerade entry, you can act as any
    user at any point in time.
    """
    pu = admin_info.get("PAUSE_USERS", {})
    if username in pu:
        task_info["PAUSE_AT"] = pu[username]
    elif masquerade_as in pu:
        task_info["PAUSE_AT"] = pu[masquerade_as]
    elif "PAUSE_AT" in admin_info:
        task_info["PAUSE_AT"] = admin_info["PAUSE_AT"]
    # else we don't set PAUSE_AT at all


def amend_task_info(course, semester, task_info, username):
    """
    Amends task info object with extra keys in each pset to indicate pset
    state. Also adds summary information to each task of the pset based
    on user feedback generated so far. Also checks potluck inflight
    status and adds a "submitted" key to each task where appropriate.
    Template code should be careful not to reveal feedback info not
    warranted by the current pset state.
    """
    for pset in task_info["psets"]:
        # Add status info to the pset object:
        amend_pset_and_tasks(course, semester, task_info, pset, username)


def amend_pset_and_tasks(
    course,
    semester,
    task_info,
    pset_obj,
    username
):
    """
    Calls amend_pset on the given pset object, and then amend_task on
    each task in it, adding "revision" entries to each task w/ amended
    revision info.
    """
    amend_pset(course, semester, task_info, pset_obj, username)
    # Add summary info to each task, and duplicate for revisions
    for task in pset_obj["tasks"]:
        rev_task = copy.deepcopy(task)
        amend_task(
            course,
            semester,
            task_info,
            pset_obj["id"],
            rev_task,
            username,
            "revision"
        )
        task["revision"] = rev_task
        amend_task(
            course,
            semester,
            task_info,
            pset_obj["id"],
            task,
            username,
            "initial"
        )


def amend_pset(course, semester, task_info, pset_obj, username):
    """
    Adds a "status" key to the given problem set object (which should be
    part of the given task info). The username is used to look up
    extension information.
    """
    initial_ext = storage.get_extension(
        course,
        semester,
        username,
        pset_obj["id"],
        "initial"
    )
    if initial_ext is None:
        flask.flash(
            "Error fetching initial extension info (treating as 0)."
        )
        initial_ext = 0

    revision_ext = storage.get_extension(
        course,
        semester,
        username,
        pset_obj["id"],
        "revision"
    )
    if revision_ext is None:
        flask.flash(
            "Error fetching revision extension info (treating as 0)."
        )
        revision_ext = 0

    pset_obj["status"] = pset_status_now(
        username,
        task_info,
        pset_obj,
        extensions=[initial_ext, revision_ext]
    )


def amend_task(course, semester, task_info, psid, task, username, phase):
    """
    Adds task-state-related keys to the given task object. The following
    keys are added:

    - "feedback_summary": A feedback summary object (see
        `get_feedback_summary`).
    - "time_spent": The time spent info that the user entered for time
        spent when submitting the task (see
        `potluck_app.storage.fetch_time_spent` for the format). Will be
        None if that info isn't available.
    - "submitted": True if the user has attempted submission (even if
        there were problems) or if we have feedback for them (regardless
        of anything else).
    - "submitted_at": A `datetime.datetime` object representing when
        the submission was received, or None if there is no recorded
        submission.
    - "eval_elapsed": A `datetime.timedelta` that represents the time
        elapsed since evaluation was started for the submission (in
        possibly fractional seconds).
    - "eval_timeout": A `datetime.timedelta` representing the number
        of seconds before the evaluation process should time out.
    - "eval_status": The status of the evaluation process (see
        `get_inflight`).
    - "submission_status": A string representing the status of the
        submission overall. One of:
        - "unsubmitted": no submission yet.
        - "inflight": has been submitted; still being evaluated.
        - "unprocessed": evaluated but there's an issue (evaluation
            crashed or elsehow failed to generate feedback).
        - "issue": evaluated but there's an issue (evaluation warning or
            'incomplete' evaluation result.)
        - "complete": Evaluated and there's no major issue (grade may or
            may not be perfect, but it better than "incomplete").
    - "submission_icon": A one-character string used to represent the
        submission status.
    - "submission_desc": A brief human-readable version of the
        submission status.
    - "grade": A numerical grade value, derived from the evaluation via
        the EVALUATION_SCORES dictionary defined in the config file. If
        no grade has been assigned, it will be the string '?' instead of
        a number. Grade overrides are factored in if present.
    - "grade_overridden": A boolean indicating whether the grade was
        overridden or not. Will be true when there's an override active
        even if the override indicates the same score as the automatic
        grade.
    - "notes": A string indicating the markdown source for custom notes
        applied to the task by an evaluator.
    - "notes_html": A string of HTML code rendered from the notes
        markdown.
    - "max_score": A number representing the maximum score possible
        based on the phase of the submission, either SCORE_BASIS for
        initial submissions or REVISION_MAX_SCORE for revisions.
    - "max_revision_score": A number representing the max score possible
        on a revision of this task (regardless of whether this is an
        initial or revised submission)
    """
    # Fetch basic info
    task["feedback_summary"] = storage.get_feedback_summary(
        course,
        semester,
        task_info,
        username,
        phase,
        psid,
        task["id"]
    )
    task["time_spent"] = storage.fetch_time_spent(
        course,
        semester,
        username,
        phase,
        psid,
        task["id"]
    )

    # Get submitted value
    # Note that we hedge here against the possibility that the feedback
    # summary isn't readable since some kinds of bad crashes of the
    # evaluator can cause that to happen (e.g., student accidentally
    # monkey-patches json.dump so that no report can be written).
    task["submitted"] = (task.get("feedback_summary") or {}).get("submitted")

    # Get inflight info so we know about timeouts
    ts, logfile, reportfile, status = storage.get_inflight(
        course,
        semester,
        username,
        phase,
        psid,
        task["id"]
    )

    # Get current time (IN UTC)
    now = potluck.time_utils.now()

    # Time submitted and time elapsed since submission
    if ts == "error":
        task["submitted_at"] = "unknown"
        task["eval_elapsed"] = "unknown"
    elif ts is not None:
        submit_time = potluck.time_utils.local_time(
            task_info,
            potluck.time_utils.time_from_timestring(ts)
        )
        task["submitted_at"] = submit_time
        task["eval_elapsed"] = now - submit_time
    else:
        try:
            submit_time = potluck.time_utils.local_time(
                task_info,
                potluck.time_utils.time_from_timestring(
                    task["feedback_summary"]["timestamp"]
                )
            )
            task["submitted_at"] = submit_time
            task["eval_elapsed"] = now - submit_time
        except Exception:
            task["submitted_at"] = None
            task["eval_elapsed"] = None

    task["eval_timeout"] = datetime.timedelta(
        seconds=app.config["FINAL_EVAL_TIMEOUT"]
    )

    # Set eval_status
    if ts == "error":
        task["eval_status"] = "unknown"
    else:
        task["eval_status"] = status

    # Override submitted value
    if status is not None:
        task["submitted"] = True

    # Add max score info
    task["max_score"] = (
        app.config["REVISION_MAX_SCORE"]
        if phase == "revision"
        else app.config["SCORE_BASIS"]
    )
    task["max_revision_score"] = app.config["REVISION_MAX_SCORE"]

    # Add grade info
    if task["eval_status"] in ("unknown", "initial", "in_progress"):
        task["grade"] = "?"
    elif task["eval_status"] in ("error", "expired"):
        task["grade"] = 0
    elif task["eval_status"] == "completed" or task["submitted"]:
        task["grade"] = app.config["EVALUATION_SCORES"].get(
            task["feedback_summary"]["evaluation"],
            app.config["EVALUATION_SCORES"].get("__other__", "???")
        )
        if task["grade"] == "???":
            flask.flash(
                (
                    "Warning: evaluation '{}' has not been assigned a"
                  + " grade value!"
                ).format(
                    task["feedback_summary"]["evaluation"]
                )
            )
            task["grade"] = None
    else:
        task["grade"] = None

    # Check for a grade override and grading note
    notes, notes_html, override = get_evaluation_info(
        course,
        semester,
        username,
        phase,
        psid,
        task["id"]
    )
    task["notes"] = notes
    task["notes_html"] = notes_html
    if override == '':
        task["grade_overridden"] = False
    else:
        task["grade_overridden"] = True
        task["grade"] = override

    # Set detailed submission status along with icon and description
    if task["eval_status"] == "unknown":
        task["submission_status"] = "inflight"
        task["submission_icon"] = "‽"
        task["submission_desc"] = "status unknown"
    if task["eval_status"] in ("initial", "in_progress"):
        task["submission_status"] = "inflight"
        task["submission_icon"] = "?"
        task["submission_desc"] = "evaluation in progress"
    elif task["eval_status"] in ("error", "expired"):
        task["submission_status"] = "unprocessed"
        task["submission_icon"] = "☹"
        task["submission_desc"] = "processing error"
    elif task["eval_status"] == "completed" or task["submitted"]:
        report = task["feedback_summary"]
        if report["warnings"]:
            task["submission_status"] = "issue"
            task["submission_icon"] = "✗"
            task["submission_desc"] = "major issue"
        elif report["evaluation"] == "incomplete":
            task["submission_status"] = "issue"
            task["submission_icon"] = "✗"
            task["submission_desc"] = "incomplete submission"
        elif report["evaluation"] == "not evaluated":
            task["submission_status"] = "unprocessed"
            task["submission_icon"] = "☹"
            task["submission_desc"] = "submission not evaluated"
        else:
            task["submission_status"] = "complete"
            task["submission_icon"] = "✓"
            task["submission_desc"] = "submitted"
    else:
        task["submission_status"] = "unsubmitted"
        task["submission_icon"] = "…"
        task["submission_desc"] = "not yet submitted"


def percentile(dataset, pct):
    """
    Computes the nth percentile of the dataset by a weighted average of
    the two items on either side of that fractional index within the
    dataset. pct must be a number between 0 and 100 (inclusive).

    Returns None when given an empty dataset, and always returns the
    singular item in the dataset when given a dataset of length 1.
    """
    fr = pct / 100.0
    if len(dataset) == 1:
        return dataset[0]
    elif len(dataset) == 0:
        return None
    srt = sorted(dataset)
    fridx = fr * (len(srt) - 1)
    idx = int(fridx)
    if idx == fridx:
        return srt[idx] # integer index -> no averaging
    leftover = fridx - idx
    first = srt[idx]
    second = srt[idx + 1] # legal index because we can't have hit the end
    return first * (1 - leftover) + second * leftover


def get_feedback_ps_and_task(
    task_info,
    course,
    semester,
    user,
    phase,
    psid,
    taskid
):
    """
    Given a task_info object and a particular
    course/semester/user/phase/pset/task we're interested in, extracts
    and augments ps and task objects to make them ready for rendering as
    feedback, returning a tuple of both.

    Returns a ValueError object in cases where the requested pset/task
    doesn't exist.
    """

    # Extract ps & task objects
    try:
        ps = get_ps_obj(task_info, psid)
    except ValueError as e:
        return e

    try:
        task = get_task_obj(task_info, ps, taskid)
    except ValueError as e:
        return e

    # Add status & time remaining info to pset and objects
    amend_pset(course, semester, task_info, ps, user)
    amend_task(course, semester, task_info, psid, task, user, phase)

    # Get full feedback for the task in question if it's available
    task["feedback"] = storage.get_feedback(
        course,
        semester,
        task_info,
        user,
        phase,
        ps["id"],
        task["id"]
    )
    # Get HTML feedback as well
    task["feedback_html"] = storage.get_feedback_html(
        course,
        semester,
        task_info,
        user,
        phase,
        ps["id"],
        task["id"]
    )
    if task["feedback"]["status"] != "missing":
        task["submitted"] = True
        potluck.render.augment_report(task["feedback"])

    return ps, task


def get_evaluation_info(
    course,
    semester,
    target_user,
    phase,
    psid,
    taskid
):
    """
    Fetches notes and override info for the given submission, and returns
    a triple including the notes markdown source, the notes rendered
    HTML, and the grade override value.

    The grade override will be an empty string if no override is active,
    and should be a floating-point value otherwise except in cases where
    a non-numeric value was set.

    The notes and notes HTML strings will be empty strings if no notes
    have been set.
    """
    # Fetch raw eval info dict
    evaluation = storage.fetch_evaluation(
        course,
        semester,
        target_user,
        phase,
        psid,
        taskid
    )

    if evaluation is None:
        return '', '', ''

    # Extract notes and grade override from stored info
    notes = evaluation.get("notes", "")
    override = evaluation.get("override")
    if override is None:
        override = ""
    else:
        try:
            override = float(override)
        except Exception:
            pass

    # Render notes as HTML
    notes_html = potluck.render.render_markdown(notes)

    return notes, notes_html, override


def get_grade_override(
    course,
    semester,
    target_user,
    phase,
    psid,
    taskid
):
    """
    Fetches notes and override info for the given submission, and returns
    just the grade override as a floating-point value, or None if there
    is no override active.
    """
    # Fetch raw eval info dict
    evaluation = storage.fetch_evaluation(
        course,
        semester,
        target_user,
        phase,
        psid,
        taskid
    )

    if evaluation is None:
        return None

    val = evaluation.get("override", None)
    if val == "":
        return None
    else:
        try:
            return float(val)
        except Exception:
            flask.flash(
                (
                    "Invalid grade override value '{}'. No override"
                    " applied."
                ).format(val)
            )
            return None


#----------------#
# Time functions #
#----------------#

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY = ONE_HOUR * 24
ONE_WEEK = ONE_DAY * 7


def pset_status_now(
    username,
    task_info,
    pset_obj,
    extensions=(False, False)
):
    """
    Returns the current state of the given pset object (also needs the
    task info object and the username). If "PAUSE_AT" is set in the task
    object and non-empty (see set_pause_time), that moment, not the
    current time, will be used. Extensions must contain two values (one
    for the initial phase and one for the revision phase). They may each
    be False for no extension, True for the default extension, or an
    integer number of hours. Those hours will be added to the effective
    initial and revision deadlines.

    Returns a dictionary with 'state', 'initial-extension',
    'revision-extension', 'release', 'due', 'reviewed', and 'finalized',
    keys. Each of the 'release', 'due', 'reviewed', and 'finalized' keys
    will be a sub-dictionary with the following keys:

    - 'at': A dateimte.datetime object specifying absolute timing.
    - 'at_str': A string representation of the above.
    - 'until': A datetime.timedelta representing time until the event (will
        be negative afterwards).
    - 'until_str': A string representation of the above.

    Each of the sub-values will be none if the pset doesn't have a
    deadline set.

    The 'state' value will be one of:

    - "unreleased": This pset hasn't yet been released; don't display
        any info about it.
    - "released": This pset has been released and isn't due yet.
    - "under_review": This pset's due time has passed, but the feedback
        review period hasn't expired yet.
    - "revisable": This pset's due time is past, and the review period has
        expired, so full feedback should be released, but revisions may
        still be submitted.
    - "final": This pset's due time is past, the review period has
        expired, and the revision period is also over, so full feedback
        is available, and no more submissions will be accepted.
    - "unknown": This pset doesn't have a due date. The
        seconds_remaining value will be None.

    The 'initial_extension' and 'revision_extension' will both be numbers
    specifying how many hours of extension were granted (these numbers
    are already factored into the deadline information the status
    contains). These numbers will be 0 for students who don't have
    extensions.
    """
    # Get extension/revision durations and grace period from task info:
    standard_ext_hrs = task_info.get("extension_hours", 24)
    review_hours = task_info.get("review_hours", 24)
    grace_mins = task_info.get("grace_minutes", 0)
    revision_hours = task_info.get("revision_hours", 72)

    # Get pset-specific review/grace/revision info if it exists
    review_hours = pset_obj.get("review_hours", review_hours)
    grace_mins = pset_obj.get("grace_minutes", grace_mins)
    revision_hours = pset_obj.get("revision_hours", revision_hours)

    # Figure out extension amounts
    initial_extension = 0
    if extensions[0] is True:
        initial_extension = standard_ext_hrs
    elif isinstance(extensions[0], (int, float)):
        initial_extension = extensions[0]
    elif extensions[0] is not False:
        flask.flash(
            "Ignoring invalid initial extension value '{}'".format(
                extensions[0]
            )
        )

    revision_extension = 0
    if extensions[1] is True:
        revision_extension = standard_ext_hrs
    elif isinstance(extensions[1], (int, float)):
        revision_extension = extensions[1]
    elif extensions[1] is not False:
        flask.flash(
            "Ignoring invalid revision extension value '{}'".format(
                extensions[1]
            )
        )

    # The default result
    result = {
        'state': "unknown",
        'release': {
            'at': None,
            'at_str': 'unknown',
            'until': None,
            'until_str': 'at some point (not yet specified)'
        },
        'due': {
            'at': None,
            'at_str': 'unknown',
            'until': None,
            'until_str': 'at some point (not yet specified)'
        },
        'reviewed': {
            'at': None,
            'at_str': 'unknown',
            'until': None,
            'until_str': 'at some point (not yet specified)'
        },
        'finalized': {
            'at': None,
            'at_str': 'unknown',
            'until': None,
            'until_str': 'at some point (not yet specified)'
        },
        'initial_extension': 0,
        'revision_extension': 0,
    }

    # Save extension info
    result['initial_extension'] = initial_extension or 0
    result['revision_extension'] = revision_extension or 0

    # Get current time:
    if "PAUSE_AT" in task_info and task_info["PAUSE_AT"]:
        now = potluck.time_utils.task_time__time(
            task_info,
            task_info["PAUSE_AT"]
        )
    else:
        now = potluck.time_utils.now()

    # Get release date/time:
    release_at = pset_obj.get("release", None) # if None, we assume release
    if release_at is not None:
        release_at = potluck.time_utils.task_time__time(
            task_info,
            release_at,
            default_time_of_day=task_info.get(
                "default_release_time_of_day",
                "23:59"
            )
        )
        # Fill in release info
        result['release']['at'] = release_at
        result['release']['at_str'] = potluck.time_utils.fmt_datetime(
            release_at
        )
        until_release = release_at - now
        result['release']['until'] = until_release
        result['release']['until_str'] = fuzzy_time(
            until_release.total_seconds()
        )

    # Get due date/time:
    due_at = pset_obj.get("due", None)
    if due_at is None:
        # Return empty result
        return result
    else:
        due_at = potluck.time_utils.task_time__time(
            task_info,
            due_at,
            default_time_of_day=task_info.get(
                "default_due_time_of_day",
                "23:59"
            )
        )
        review_end = due_at + datetime.timedelta(hours=review_hours)

    due_string = potluck.time_utils.fmt_datetime(due_at)

    base_deadline = due_at

    # Add extension hours:
    if initial_extension > 0:
        due_at += datetime.timedelta(hours=initial_extension)
        due_string = potluck.time_utils.fmt_datetime(due_at) + (
            ' <span class="extension_taken">'
          + '(after accounting for your {}‑hour extension)'
          + '</span>'
        ).format(initial_extension)

    grace_deadline = due_at + datetime.timedelta(minutes=grace_mins)

    # Fill in due info
    result['due']['at'] = due_at
    result['due']['at_str'] = due_string
    until_due = due_at - now
    result['due']['until'] = until_due
    result['due']['until_str'] = fuzzy_time(until_due.total_seconds())

    # Fill in review info
    result['reviewed']['at'] = review_end
    result['reviewed']['at_str'] = potluck.time_utils.fmt_datetime(
        review_end
    )
    until_reviewed = review_end - now
    result['reviewed']['until'] = until_reviewed
    result['reviewed']['until_str'] = fuzzy_time(
        until_reviewed.total_seconds()
    )

    # Get final date/time:
    # Note: any extension to the initial deadline is ignored. A separate
    # revision extension should be issued when an initial extension eats
    # up too much of the revision period.
    final_at = base_deadline + datetime.timedelta(
        hours=review_hours + revision_hours
    )

    final_string = potluck.time_utils.fmt_datetime(final_at)

    # Add extension hours:
    if revision_extension > 0:
        final_at += datetime.timedelta(hours=revision_extension)
        final_string = potluck.time_utils.fmt_datetime(final_at) + (
            ' <span class="extension_taken">'
          + '(after accounting for your {}‑hour extension)'
          + '</span>'
        ).format(revision_extension)

    grace_final = final_at + datetime.timedelta(minutes=grace_mins)

    # Fill in finalization info
    result['finalized']['at'] = final_at
    result['finalized']['at_str'] = final_string
    until_final = final_at - now
    result['finalized']['until'] = until_final
    result['finalized']['until_str'] = fuzzy_time(until_final.total_seconds())

    # Check release time:
    if release_at and now < release_at:
        result['state'] = "unreleased"
    # Passed release_at point: check if it's due or not
    elif now < grace_deadline:
        # Note time-remaining ignores grace period and may be negative
        result['state'] = "released"
    # Passed due_at point; check if it's still under review:
    elif now < review_end:
        result['state'] = "under_review"
    # Passed review period: are revisions still being accepted?
    elif now < grace_final:
        result['state'] = "revisable"
    # Passed review period: it's final
    else:
        result['state'] = "final"

    return result


#--------------------#
# Filename functions #
#--------------------#

def get_submission_filename(
    course,
    semester,
    task_info,
    username,
    phase,
    psid,
    taskid
):
    """
    Returns the filename for the user's submission for a given
    phase/pset/task. Raises a ValueError if the pset or task doesn't
    exit.

    TODO: Do we just do zip files for multi-file tasks? How is that
    handled?
    """
    ps = get_ps_obj(task_info, psid)
    task = get_task_obj(task_info, ps, taskid)

    return flask.safe_join(
        storage.submissions_folder(course, semester),
        username,
        "{}_{}_{}".format(
            psid,
            phase,
            task["target"]
        )
    )


#---------------#
# Jinja support #
#---------------#

_sorted = sorted


@app.template_filter()
def sorted(*args, **kwargs):
    """
    Turn builtin sorted into a template filter...
    """
    return _sorted(*args, **kwargs)


@app.template_filter()
def fuzzy_time(seconds):
    """
    Takes a number of seconds and returns a fuzzy time value that shifts
    units (up to weeks) depending on how many seconds there are. Ignores
    the sign of the value.
    """
    if seconds < 0:
        seconds = -seconds

    weeks = seconds / ONE_WEEK
    seconds %= ONE_WEEK
    days = seconds / ONE_DAY
    seconds %= ONE_DAY
    hours = seconds / ONE_HOUR
    seconds %= ONE_HOUR
    minutes = seconds / ONE_MINUTE
    seconds %= ONE_MINUTE
    if int(weeks) > 1:
        if weeks % 1 > 0.75:
            return "almost {:.0f} weeks".format(weeks + 1)
        else:
            return "{:.0f} weeks".format(weeks)
    elif int(weeks) == 1:
        return "{:.0f} days".format(7 + days)
    elif int(days) > 1:
        if days % 1 > 0.75:
            return "almost {:.0f} days".format(days + 1)
        else:
            return "{:.0f} days".format(days)
    elif int(days) == 1:
        return "{:.0f} hours".format(24 + hours)
    elif hours > 4:
        if hours % 1 > 0.75:
            return "almost {:.0f} hours".format(hours + 1)
        else:
            return "{:.0f} hours".format(hours)
    elif int(hours) > 0:
        return "{:.0f}h {:.0f}m".format(hours, minutes)
    elif minutes > 30:
        return "{:.0f} minutes".format(minutes)
    else:
        return "{:.0f}m {:.0f}s".format(minutes, seconds)


@app.template_filter()
def timestamp(value):
    """
    A filter to display a timestamp.
    """
    dt = potluck.time_utils.time_from_timestring(value)
    return potluck.time_utils.fmt_datetime(dt)


@app.template_filter()
def seconds(timedelta):
    """
    Converts a timedelta to a floating-point number of seconds.
    """
    return timedelta.total_seconds()


@app.template_filter()
def integer(value):
    """
    A filter to display a number as an integer.
    """
    if isinstance(value, (float, int)):
        return str(round(value))
    else:
        return str(value)


app.add_template_global(min, name='min')
app.add_template_global(max, name='max')
app.add_template_global(round, name='round')
app.add_template_global(sum, name='sum')

# Custom filename->slug filter from potluck
app.template_filter()(potluck.html_tools.fileslug)

# Time filters from potluck
app.template_filter()(potluck.time_utils.fmt_datetime)


@app.template_filter()
def a_an(h):
    """
    Returns the string 'a' or 'an' where the use of 'a/an' depends on the
    first letter of the name of the first digit of the given number, or
    the first letter of the given string.

    Can't handle everything because it doesn't know phonetics (e.g., 'a
    hour' not 'an hour' because 'h' is not a vowel).
    """
    digits = str(h)
    fd = digits[0]
    if fd in "18aeiou":
        return 'an'
    else:
        return 'a'


@app.template_filter()
def pset_combined_grade(pset):
    """
    Extracts a full combined grade value from a pset object. Respects
    task weights; fills in zeroes for any missing grades, and grabs the
    highest score from each task pool. Returns a floating-point value.
    """
    total_score = 0
    total_weight = 0
    pool_scores = {}
    for task in pset["tasks"]:
        # Get a grade & weight
        cg = task_combined_grade(task)
        tw = task.get("weight", 1)
        if cg is None:
            cg = 0

        # Figure out this task's pool and update the score for that pool
        pool = task_pool(task)
        if pool in pool_scores:
            old_score, old_weight = pool_scores[pool]
            if old_weight != tw:
                raise ValueError("Inconsistent weights for pooled tasks!")
            if old_score < cg:
                pool_scores[pool] = [cg, tw]
        else:
            pool_scores[pool] = [cg, tw]

    total_score = sum(grade for grade, weight in pool_scores.values())
    total_weight = sum(weight for grade, weight in pool_scores.values())

    return total_score / float(total_weight)


@app.template_filter()
def uses_pools(pset):
    """
    Returns True if the pset has at least two tasks that are in the same
    pool, and False otherwise.
    """
    pools = set(task_pool(task) for task in pset["tasks"])
    return len(pools) < len(pset["tasks"])


@app.template_filter()
def task_pool(task):
    """
    Grabs the pool for a task, which defaults to the task ID.
    """
    return task.get("pool", task["id"])


@app.template_filter()
def pset_pools(pset):
    """
    Returns a list of pairs, each containing a pool ID and a colspan
    integer for that pool.
    """
    seen = set()
    result = []
    for task in pset["tasks"]:
        pool = task_pool(task)
        if pool in seen:
            continue
        else:
            seen.add(pool)
            result.append((pool, pool_colspan(pset, task["id"])))
    return result


@app.template_filter()
def pool_colspan(pset, taskid):
    """
    Returns the column span for the pool of the given task in the given
    pset, assuming that the tasks of the pset are displayed in order.
    """
    start_at = None
    this_task = None
    for i in range(len(pset["tasks"])):
        if pset["tasks"][i]["id"] == taskid:
            start_at = i
            this_task = pset["tasks"][i]
            break

    if start_at is None:
        raise ValueError(
            "Pset '{}' does not contain a task '{}'.".format(
                pset["id"],
                taskid
            )
        )

    this_pool = task_pool(this_task)
    span = 1
    for task in pset["tasks"][i + 1:]:
        if task_pool(task) == this_pool:
            span += 1
        else:
            break # span is over

    return span


@app.template_filter()
def task_combined_grade(task):
    """
    Extracts the combined grade value between initial and revised
    submissions for the given task. Returns a point number, or None if
    there is not enough information to establish a grade.
    """
    base_grade = task.get("grade")
    if base_grade == "?":
        base_grade = None
    elif base_grade is not None:
        base_grade = float(base_grade)

    rev_task = task.get("revision")
    has_rev_grade = (
        rev_task
    and "grade" in rev_task
    and rev_task["grade"] not in (None, "?")
    )
    if has_rev_grade:
        rev_grade = min(
            app.config["REVISION_MAX_SCORE"],
            float(rev_task["grade"])
        )
        if base_grade is not None:
            full_grade = max(base_grade, rev_grade)
        else:
            full_grade = rev_grade
    else:
        rev_grade = None
        full_grade = base_grade

    return full_grade


@app.template_filter()
def grade_string(grade_value):
    """
    Turns a grade value (None, or a number) into a grade string (an HTML
    string w/ a denominator, or 'unknown').
    """
    if grade_value is None or not isinstance(grade_value, (int, float)):
        return "unknown"
    else:
        round_to = app.config["ROUND_SCORES_TO"]
        rounded = round(grade_value, round_to)
        rdenom = round( app.config["SCORE_BASIS"], round_to)
        if int(rounded) == rounded:
            rounded = int(rounded)
        if int(rdenom) == rdenom:
            rdenom = int(rdenom)
        return "{}&nbsp;/&nbsp;{}".format(rounded, rdenom)


@app.template_filter()
def shorter_grade(grade_string):
    """
    Shortens a grade string.
    """
    divis = "&nbsp;/&nbsp;"
    if divis in grade_string:
        return grade_string[:grade_string.index(divis)]
    elif grade_string == "unknown":
        return "?"
    else:
        return "!"


@app.template_filter()
def grade_category(grade_value):
    """
    Categorizes a grade value (0-100 or None).
    """
    if grade_value is None:
        return "missing"
    elif grade_value < app.config["GRADE_THRESHOLDS"]["low"]:
        return "low"
    elif grade_value < app.config["GRADE_THRESHOLDS"]["mid"]:
        return "mid"
    else:
        return "high"


@app.template_filter()
def timespent(time_spent):
    """
    Handles numerical-or-string-or-None time spent values.
    """
    if isinstance(time_spent, (int, float)):
        if time_spent == 0:
            return '-'
        elif int(time_spent) == time_spent:
            return "{}h".format(int(time_spent))
        else:
            return "{}h".format(round(time_spent, 2))
    elif isinstance(time_spent, str):
        return time_spent
    else:
        return "?"


@app.template_filter()
def initials(full_section_title):
    """
    Reduces a full section title potentially including time information
    to just first initials.
    """
    words = full_section_title.split()
    if len(words) > 1:
        return words[0][0] + words[1][0]
    else:
        return full_section_title


@app.template_filter()
def pronoun(pronouns):
    """
    Reduces pronoun info to a single pronoun.
    """
    test = '/'.join(re.split(r"[^A-Za-z]+", pronouns.lower()))
    if test in (
        "she",
        "she/her",
        "she/hers",
        "she/her/hers"
    ):
        return "she"
    elif test in (
        "he",
        "he/him",
        "he/his",
        "he/him/his"
    ):
        return "he"
    elif test in (
        "they",
        "they/them",
        "them/them/their"
    ):
        return "they"
    else:
        return pronouns


# Characters that need replacing to avoid breaking strings in JS script
# tags
_JS_ESCAPES = [ # all characters with ord() < 32
    chr(z) for z in range(32)
] + [
    '\\',
    "'",
    '"',
    '>',
    '<',
    '&',
    '=',
    '-',
    ';',
    u'\u2028', # LINE_SEPARATOR
    u'\u2029', # PARAGRAPH_SEPARATOR
]


@app.template_filter()
def escapejs(value):
    """
    Modified from:

    https://stackoverflow.com/questions/12339806/escape-strings-for-javascript-using-jinja2

    Escapes string values so that they can appear inside of quotes in a
    &lt;script&gt; tag and they won't end the quotes or cause any other
    trouble.
    """
    retval = []
    for char in value:
        if char in _JS_ESCAPES:
            retval.append(r'\u{:04X}'.format(ord(char)))
        else:
            retval.append(char)

    return jinja2.Markup(u"".join(retval))


#----------------#
# Roster loading #
#----------------#

def load_roster_from_stream(iterable_of_strings):
    """
    Implements the roster-loading logic given an iterable of strings,
    like an open file or a list of strings. See `load_roster`.
    """
    reader = csv.reader(iterable_of_strings)

    students = {}
    # [2018/09/16, lyn] Change to handle roster with titles
    # [2019/09/13, peter] Change to use standard Registrar roster columns
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


#-----------#
# Main code #
#-----------#

if __name__ == "__main__":
    use_ssl = True
    if app.config.get("NO_DEBUG_SSL"):
        use_ssl = False
    else:
        try:
            import OpenSSL # noqa F811, F401
        except ModuleNotFound_or_Import_Error:
            use_ssl = False

    if use_ssl:
        # Run with an ad-hoc SSL context since OpenSSL is available
        print("Running with self-signed SSL.")
        app.run('localhost', 8787, debug=False, ssl_context='adhoc')
    else:
        # Run without an SSL context (No OpenSSL)
        print("Running without SSL.")
        app.run('localhost', 8787, debug=False)
        # Note: can't enable debugging because it doesn't set __package__
        # when restarting and so relative imports break in 3.x
