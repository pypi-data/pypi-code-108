"""
This file contains classes and functions for setting up regression test suites with convenient utilities
Usage:
 - Subclass a test case from OMFITtest
 - Override any of the default settings you like at the top of the class
 - Write test methods
 - Supply your test case (or a list of OMFITtest-based test cases) to manage_tests() as the first argument

See also: OMFIT-source/regression/test_template.py
"""

try:
    # Framework is running
    from .startup_choice import *
except ImportError as _excp:
    # class is imported by itself
    if (
        'attempted relative import with no known parent package' in str(_excp)
        or 'No module named \'omfit_classes\'' in str(_excp)
        or "No module named '__main__.startup_choice'" in str(_excp)
    ):
        from startup_choice import *
    else:
        raise

import traceback
import numpy as np
import unittest
import warnings
from matplotlib import pyplot
from matplotlib.cbook import MatplotlibDeprecationWarning
import yaml
import traceback

from omfit_classes.omfit_github import (
    set_gh_status,
    post_comment_to_github,
    get_pull_request_number,
    get_gh_remote_org_repo_branch,
    get_OMFIT_GitHub_token,
    delete_matching_gh_comments,
    on_latest_gh_commit,
)

__all__ = [
    'OMFITtest',
    'manage_tests',
    'setup_warnings',
    'get_server_name',
    'clear_old_test_report_comments',
    'auto_comment_marker',
    'run_test_outside_framework',
    'RedirectStdStreams',
    'auto_test_mode',
    'standard_test_keywords',
]


# Make a class for standard_test_keywords so it can have a docstring that describes the keywords
class StandardTestKeywords(dict):
    """
    Set of standard keywords to be accepted by defaultVars in OMFIT regression tests

    Provided as a central feature to make developing new tests easier.

    :param run_tests: bool
        Switch for enabling execution of tests. Disabling execution allows
        importing of objects from the test script.

    :param allow_gui: bool
        Allows test units that require GUI interactions to execute. Recommended:
        decorate affected units with:
            @unittest.skipUnless(allow_gui, 'GUIs not allowed')
            def test_blah_blah(...

    :param allow_long: bool
        Allows long test units to run. What qualifies as long is subjective.
        Recommended: decorate with:
            @unittest.skipUnless(allow_long, 'Long tests are not allowed')
            def test_blah(...

    :param failfast: bool
        Halt execution at the first failure instead of testing remaining units.
        Passed to unittest.

    :param force_gh_status: bool [optional]
        If not None, override default GitHub status posting behavior and force posting or not posting.

    :param force_gh_comment: int [optional]
        If not None, override default GitHub comment posting behavior with this value.
        The value is interpreted as bits, so 5 means 1 and 4.
            1 (bit 0): do a post or update
            2 (bit 1): if there's a failure to report, do a post or update
            4 (bit 2): edit an existing comment instead of posting if possible, otherwise post
            8 (bit 3): edit the top comment to add or update the test report (ignored if not combined with bit 2)

    :param only_these: string or list of strings [optional]
        Names of test units to run (with or without leading `test_`).
        Other test units will not be run. (None to run all tests)

    :param there_can_be_only_one: int or bool
        Set test report comment cleanup behavior; not very relevant if bit 3 of
        gh_comment isn't set. This value is interpreted as a set of binary flags,
        so 6 should be interpreted as options 2 and 4 being active.

        A value of True is converted into 255 (all the bits are True, including unused bits).
        A value of None is replaced by the default value, which is True or 255.
        A float or string will work if it can be converted safely by int().

        1: Any of the flags will activate this feature. The 1 bit has no special meaning beyond activation.
            If active, old github comments will be deleted. The newest report may be retained.
        2: Limit deletion to reports that match the combined context of the test being run.
        4: Only protect the latest comment if it reports a failure; if the last test passed, all comments may be deleted
        8: Limit scope to comments with matching username

    """
    def __init__(self):
        self.update(
            dict(
                run_tests=True,
                allow_gui=bool(('rootGUI' in OMFITaux) and OMFITaux['rootGUI']),
                allow_long=True,
                failfast=False,
                force_gh_status=None,
                force_gh_comment=None,
                only_these=None,
                there_can_be_only_one=True,
            )
        )


standard_test_keywords = StandardTestKeywords()

auto_comment_marker = (
    '<!--This comment was automatically generated by OMFIT and was not posted directly by a human. ' 'A2ZZJfxk2910x2AZZf -->'
)

# auto_test_mode is a flag that indicates that the tests are being run automatically, such as by morti, and so behavior should be modified.
try:
    auto_test_mode = bool(is_server('localhost', 'morti')) and repo is not None
except KeyError:
    auto_test_mode = False


class setup_warnings(object):
    """
    A context manager like `catch_warnings`, that copies and restores the warnings
    filter upon exiting the context, with preset levels of warnings that turn some
    warnings into exceptions.

    :param record: specifies whether warnings should be captured by a
        custom implementation of warnings.showwarning() and be appended to a list
        returned by the context manager. Otherwise None is returned by the context
        manager. The objects appended to the list are arguments whose attributes
        mirror the arguments to showwarning().

    :param module: to specify an alternative module to the module
        named 'warnings' and imported under that name. This argument is only useful
        when testing the warnings module itself.

    :param level: (int) Controls how many warnings should throw errors

        -1: Do nothing at all and return immediately

        0: No warnings are promoted to exceptions. Specific warnings defined in
            higher levels are ignored and the rest appear as warnings, but with
            'always' instead of 'default' behavior: they won't disappear after
            the first instance.

        All higher warning levels turn all warnings into exceptions and then
        selectively ignore some of them:

        1: Ignores everything listed in level 2, but also ignores many common
            math errors that produce NaN.

        2: RECOMMENDED: In addition to level 3, also ignores several warnings
            of low-importance, but still leaves many math warnings (divide by 0)
            as errors.

        3: Ignores warnings which are truly irrelevant to almost any normal
            regression testing, such as the warning about not being able to make
            backup copies of scripts that are loaded in developer mode. Should
            be about as brutal as level 4 during the actual tests, but somewhat
            more convenient while debugging afterward.

        4: No warnings are ignored. This will be really annoying and not useful
            for many OMFIT applications.
    """

    def __init__(self, level=2, record=False, module=None):
        """Specify whether to record warnings and if an alternative module
        should be used other than sys.modules['warnings'].

        For compatibility with Python 3.0, please consider all arguments to be keyword-only.
        """
        self._level = level
        self._record = record
        self._module = module or sys.modules['warnings']
        self._entered = False

    def __enter__(self):
        if self._entered:
            raise RuntimeError("Cannot enter %r twice" % self)
        self._entered = True
        self._filters = self._module.filters
        self._module.filters = self._filters[:]
        self._showwarning = self._module.showwarning
        if self._record:
            log = []

            def showwarning(*args, **kwargs):
                log.append(WarningMessage(*args, **kwargs))

            self._module.showwarning = showwarning
        else:
            log = None

        level = self._level

        if level < 0:
            if self._record:
                return log
            else:
                return None

        warnings.resetwarnings()
        np.seterr(all='warn')
        if level <= 0:
            warnings.simplefilter('always')
        else:
            warnings.simplefilter('error')

        if level <= 3:
            warnings.filterwarnings('ignore', message='OMFIT is unable to create script backup copies')
            warnings.filterwarnings('ignore', message='findfont: Font family*')
            # Future
            warnings.filterwarnings('ignore', category=FutureWarning)

        if level <= 2:
            # tight_layout()
            warnings.filterwarnings('ignore', message='tight_layout cannot make axes width small*')
            warnings.filterwarnings('ignore', message='tight_layout : falling back to Agg renderer')
            warnings.filterwarnings('ignore', message='Tight layout not applied*')
            # Underflow
            warnings.filterwarnings('ignore', message="underflow encountered in *")
            np.seterr(under='ignore')
            # Deprecation
            warnings.filterwarnings('ignore', category=DeprecationWarning)
            warnings.filterwarnings('ignore', category=MatplotlibDeprecationWarning)
            warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
            # xarray and numpy
            warnings.filterwarnings('ignore', category=DeprecationWarning, message='Using or importing the ABCs*')
            warnings.filterwarnings('ignore', category=FutureWarning, message='The Panel class is removed*')
            warnings.filterwarnings('ignore', category=PendingDeprecationWarning)
            warnings.filterwarnings('ignore', category=UserWarning, message="Warning: converting a masked element to nan.")
            # psycopg2
            warnings.filterwarnings('ignore', message='The psycopg2 wheel package will be renamed from release 2.8*')
            # pandas
            warnings.filterwarnings('ignore', message="Pandas doesn't allow columns to be created via a new attribute name*")

        if level <= 1:
            # Divide by 0
            warnings.filterwarnings('ignore', message='divide by zero encountered.*')
            warnings.filterwarnings('ignore', message='invalid value encountered in divide')
            warnings.filterwarnings('ignore', message='invalid value encountered in true_divide')
            # Too many NaNs
            warnings.filterwarnings('ignore', message="All-NaN slice encountered")
            # Bad comparisons
            warnings.filterwarnings('ignore', message="invalid value encountered in *", category=RuntimeWarning)
            np.seterr(divide='ignore', invalid='ignore')
            # These warnings come out of NetCDF4
            warnings.filterwarnings(
                'ignore', message=r"tostring\(\) is deprecated\. Use tobytes\(\) instead\.", category=DeprecationWarning
            )
            # psycopg2 forward compatibility (which has already taken care of)
            warnings.filterwarnings(
                'ignore', message=r'The psycopg2 wheel package will be renamed from release 2\.8*"', category=UserWarning
            )

        if self._record:
            return log
        else:
            return None

    def __repr__(self):
        args = []
        if self._record:
            args.append("record=True")
        if self._module is not sys.modules['warnings']:
            args.append("module=%r" % self._module)
        name = type(self).__name__
        return "%s(%s)" % (name, ", ".join(args))

    def __exit__(self, *exc_info):
        if not self._entered:
            raise RuntimeError("Cannot exit %r without entering first" % self)
        self._module.filters = self._filters
        self._module.showwarning = self._showwarning
        return


def get_server_name(hostname=socket.gethostname()):
    """
    Returns the hostname.
    For known servers, it sanitizes hostname; e.g. irisd.cluster --> iris.gat.com
    """
    try:
        SERVER
    except NameError:
        printd(
            'get_server_name could not look up SERVER dictionary; returning unmodified hostname {}'.format(hostname), topic='omfit_testing'
        )
        return hostname
    else:
        server = is_server(hostname, list(SERVER.keys()))
        if server == 'localhost':
            printd('server is localhost so returning it unmodified', topic='omfit_testing')
            return hostname
        elif server in list(SERVER.keys()):
            printd('server {} is in SERVER dictionary, so parsing it'.format(server), topic='omfit_testing')
            return parse_server(SERVER[server]['server'])[2]
        else:
            printd('server {} is not in the server dictionary; will be returned without modification'.format(server), topic='omfit_testing')
            printd(SERVER, topic='omfit_testing')
            return hostname


def clear_old_test_report_comments(lvl=15, keyword=auto_comment_marker, contexts=None, remove_all=False, **kw):
    r"""
    Removes old automatic test reports
    :param lvl: int
        Interpreted as a set of binary flags, so 7 means options 1, 2, and 4 are active.
        1: Actually execute the deletion commands instead of just testing. In test mode, it returns list of dicts
           containing information about comments that would be deleted.
        2: Limit scope to current context (must supply contexts) and do not delete automatic comments from other context
        4: Do not preserve the most recent report unless it describes a failure
        8: Only target comments with matching username
    :param keyword: string [optional]
        The marker for deletion. Comments containing this string are gathered. The one with the latest timestamp
        is removed from the list. The rest are deleted. Defaults to the standard string used to mark automatic comments.
    :param contexts: string or list of strings [optional]
        Context(s) for tests to consider. Relevant only when scope is limited to present context.
    :param remove_all: bool
        Special case: don't exclude the latest comment from deletion because its status was already resolved. This comes
        up when the test would've posted a comment and then immediately deleted it and just skips posting. In this case,
        the actual last comment is not really the last comment that would've existed had we not skipped posting, so
        don't protect it.
    :param \**kw: optional keywords passed to delete_matching_gh_comments:
        thread: int [optional]
            Thread#, like pull request or issue number.
            Will be looked up automatically if you supply None and the current branch has an open pull request.
        token: string [optional]
            Token for accessing Github.
            Will be defined automatically if you supply None and you
            have previously stored a token using set_OMFIT_GitHub_token()
        org: string [optional]
            Organization on github, like `'gafusion'`.
            Will be looked up automatically if you supply None and the current branch has an open pull request.
        repository: string [optional]
            Repository on github within the org
            Will be looked up automatically if you supply None and the current branch has an open pull request.
    :return: list
        List of responses from github API requests, one entry per comment that the function attempts to delete.
        If the test keyword is set, this will be converted into a list of dicts with information about the comments that
        would be targeted.
    """

    def printq(*args):
        """Shortcut to assigning a consistent topic to printd"""
        return printd(*args, topic='delete_comments')

    printq('clear_old_test_report_comments()')
    ckw = [keyword]
    b = [int(bb) for bb in np.binary_repr(int(lvl), 8)[::-1]]
    printq('    b = {}, initial ckw = {}'.format(b, ckw))
    # Bit 2^0: live vs test
    test = bool(1 - b[0])
    # Bit 2^1: limit scope to current context
    if b[1]:
        if contexts is None:
            printq('    Was asked to narrow scope to current context w/o having context provided. Ignoring 2^1 bit!')
        else:
            ckw += ['||' + ' + '.join(tolist(contexts)) + '||']
            printq('    Asked to narrow scope to current context(s) {}. ckw updated & is now {}'.format(contexts, ckw))
    # Bit 2^2: don't protect passing comments
    if b[2]:
        printq('    Requiring that reports are fails in order to be retained (a final pass report will be deleted)')
        kw['exclude_contain'] = '## Some tests failed!'
        printq('        kw updated and is now {}'.format(kw))
    else:
        printq('    Allowing a passing report to remain if it is the last comment')
        kw['exclude_contain'] = None
    # Bit 2^3: require username to match
    match_username = bool(b[3])

    # Other keywords
    if remove_all:
        exclude = None
        printq('    remove_all is set; exclude = {}'.format(exclude))
    else:
        exclude = 'latest'
        printq('    remove_all is not set; exclued = {}'.format(exclude))

    printq(
        '  Making the call! delete_matching_gh_comments(exclude={exclude:}, keyword={ckw:}, test={test:}, '
        'match_username={match_username:}, **kw={kw:})'.format(**locals())
    )
    return delete_matching_gh_comments(exclude=exclude, keyword=ckw, test=test, match_username=match_username, **kw)


def enforce_test_report_header_in_top_comment(thread=None, **kw):
    """
    Checks for a test report header in the top of a pull request and appends it if it's missing.

    :param thread: int
        Pull request number. If not provided, it will be looked up.

    :param kw: Keywords passed to GitHub functions.
        These may include org, repository, token. Most of the functions will figure this stuff out on their own.
    """
    from omfit_classes.omfit_github import OMFITgithub_paged_fetcher, edit_github_comment

    test_report_header = '### Test reports\n\n---\n'
    if thread is None:
        thread = get_pull_request_number(**kw)
    if thread is None:
        print('Could not find an open pull request: no top comment to edit. Aborting.')
        return
    content = OMFITgithub_paged_fetcher(path='issues/{}'.format(thread), **kw).fetch()[0]['body']
    if content is None:  # Top comment is blank
        content = ''
    # Change line break style; otherwise the report header won't match after comment has been edited manually on GitHub.
    content = content.replace('\r\n', '\n')
    if test_report_header not in content:
        printd('Adding test report header to top comment of #{}'.format(thread), topic='omfit_testing')
        edit_github_comment(new_content=test_report_header, mode='append', separator=None)
    else:
        printd('#{} already has a test report header; nothing to do about this.'.format(thread), topic='omfit_testing')
    return


def gh_test_report_update(
    the_gh_comment='',
    contexts=None,
    gh_comment=None,
    skipped_comment=False,
    rtf=None,
    there_can_be_only_one=True,
    errors=0,
    post_comment_to_github_keywords=None,
    total_test_count_report='',
):
    """
    Handles github comment posts, edits, and cleanup

    :param the_gh_comment: str
        The comment to maybe post, including the test report

    :param contexts: str or list of strings
        Context(s) to consider when clearing old test report comments

    :param gh_comment: int or list of ints
        Comment behavior bits. Interpretation: 5 means do behaviors associated with 1 and 4.
        If a list is provided, the bits are combined with or. So [1, 4] comes out to 5, and [1, 5] comes out to 5.
        1 (bit 0): do a post or update (this function shouldn't be called by manage_tests unless bit 0 or bit 1 is set)
        2 (bit 1): if there's a failure to report, do a post or update
        4 (bit 2): edit an existing comment instead of posting if possible, otherwise post
        8 (bit 3): edit the top comment to add or update the test report (ignored if not combined with bit 2)

    :param skipped_comment: bool
        Flag indicating whether building the comment was already skipped; manage_tests has already interpreted
        there_can_be_only_one to mean it should suppress building of content to post as a comment and thus if it
        passes in nothing to post, we should act as if the last comment isn't really the last comment, because we're
        aware of a "true" last comment that would've existed if we hadn't skipped its creation and immediate deletion.
        So, the actual last comment doesn't get protected for being the last comment.

    :param rtf: str
        Formatted results table

    :param there_can_be_only_one: int
        Old report cleanup behavior bits. See clear_old_test_report_comments

    :param errors: int
        Number of errors encountered. Mostly matters whether this is 0 or not.

    :param post_comment_to_github_keywords: dict
        Keywords like org, repository to pass to post_comment_to_github() or edit_github_comment

    :param total_test_count_report: str
        A brief summary of the total number of test units executed and skipped
    """
    from omfit_classes.omfit_github import edit_github_comment
    import functools

    printd('Trying to update test report comments...', topic='omfit_testing')
    # Combine github comment bits
    gh_comment = functools.reduce(lambda x, y: x | y, gh_comment)
    ghc_bits = [int(bb) for bb in np.binary_repr(int(gh_comment), 8)[::-1]]
    # Now ghc_bits[0] is 1 if any of the 2^0 bits were set for any of the test suites in the list

    # Some setup stuff
    notice = 'Some tests failed!' if errors > 0 else 'All tests passed!'
    comment_would_be_deleted = int(np.binary_repr(int(there_can_be_only_one), 8)[::-1][2]) and (errors == 0)
    clear_shortcut = False
    # Update obsolete fork keyword into org, if it exists. Newer functions aren't being built with compatibility for the
    # old convention.
    if 'fork' in post_comment_to_github_keywords:
        post_comment_to_github_keywords['org'] = post_comment_to_github_keywords.pop('fork')

    jcontexts = ' + '.join(contexts)
    keytag = 'errors were detected while testing `||{}||`'.format(jcontexts)

    if ghc_bits[2] and ghc_bits[3]:
        # This is being inserted into the top comment, so apply some extra formatting and define separators.
        open_separator = '\n<details><summary>{}</summary>\n\n'.format(jcontexts)
        close_separator = '\n\n</details><!--{}-->\n'.format(jcontexts)
        comment_mark = None
        separator = [open_separator, close_separator]
        mode = 'replace_between'
        new_content = None  # Default new content to cause clearing of old report; overwrite if not clearing
    elif ghc_bits[2]:
        # Edit existing comment, completely replacing contents
        comment_mark = keytag
        mode = 'replace'
        separator = None
        new_content = ''
    else:
        mode = 'no_edit'  # Not a valid mode; don't run edit_github_comment
        separator = comment_mark = new_content = None
    edits_handled = False
    printd('  Update comments has edit mode = {}, and searches for comment_mark = {}'.format(mode, comment_mark), topic='omfit_testing')

    if len(the_gh_comment) and comment_would_be_deleted:
        # There's some content to post as a comment, but it would be cleaned up, so let's just skip everything.
        printd(
            'Skipping comment posting because it would be instantly deleted because the test passed and '
            'there_can_be_only_one = {}, which will cause the deletion of all passing test report comments '
            'for this context.'.format(there_can_be_only_one),
            topic='delete_comments',
        )
        clear_shortcut = True  # Don't preserve the last comment because we already resolved last-comment behavior

    elif len(the_gh_comment) and not comment_would_be_deleted:
        # There's content to post that wouldn't be automatically cleaned up after, so proceed with posting.

        # Add some header stuff to the comment
        the_gh_comment = '## {}\n{} {}\n{}\n{}'.format(notice, errors, keytag, total_test_count_report, the_gh_comment)
        the_gh_comment += '<details><summary>Test environment details</summary>\n\n```\n{}```\n</details>\n\n'.format(
            test_comp_info_summary(long_form=True)
        )
        if rtf is not None:
            the_gh_comment += '\n\n```\n{}\n```'.format(rtf)
        the_gh_comment += (
            '\n{} <!--The presence of the previous statement makes this comment vulnerable to automatic '
            'deletion. To protect it, delete the thing about it being automatically generated. -->'.format(auto_comment_marker)
        )

        # Figure out how to target it
        if ghc_bits[2] and ghc_bits[3]:
            # This is being inserted into the top comment, so apply some extra formatting.
            line_prefix = '> '  # Indents nested <details> tags to make them easier to interpret
            new_content = the_gh_comment.replace('\n', '\n' + line_prefix)
            enforce_test_report_header_in_top_comment()
        elif ghc_bits[2]:
            # Edit existing comment, completely replacing contents
            new_content = the_gh_comment
        else:
            new_content = ''

        if mode == 'no_edit':  # This isn't a real option in edit_github_comment, so we use it internally
            post_needed = True
        else:
            edits_handled = True
            post_needed = False
            printd('  Attempting to edit a comment...', topic='omfit_testing')
            try:
                edit_github_comment(
                    new_content=new_content, mode=mode, separator=separator, comment_mark=comment_mark, **post_comment_to_github_keywords
                )
            except KeyError:
                if not ghc_bits[3]:
                    printd('Could not find the GitHub comment to edit; create it instead', topic='omfit_testing')
                    # Trying to edit a regular comment and couldn't find a matching one, so matching[0] throws KeyError
                    # Post the comment instead of editing
                    post_needed = True
                else:
                    print('Attempt to edit GitHub comment has failed!')
            else:
                printd('  Success! Comment edited.', topic='omfit_testing')

        if post_needed:
            printd('Posting GitHub comment:\n{}'.format(the_gh_comment), topic='omfit_testing')
            try:
                post_comment_to_github(comment=the_gh_comment, **post_comment_to_github_keywords)
            except ValueError:  # Bad/missing token (expected common problem) results in ValueError
                print('GitHub comment post failed')
    elif (not len(the_gh_comment)) and skipped_comment:
        printd('No comment to post because it was already suppressed', topic='delete_comments')
        clear_shortcut = True

    if (np.any(gh_comment) or skipped_comment) and there_can_be_only_one != 0:
        printd('  Running cleanup tasks at the end of gh_test_report_update...', topic='omfit_testing')
        # Clear old GitHub comments
        relevant_keywords = ['thread', 'org', 'repository', 'token']
        if isinstance(post_comment_to_github_keywords, dict):
            clear_kw = {k: v for k, v in post_comment_to_github_keywords.items() if k in relevant_keywords}
        else:
            clear_kw = {}
        if int(np.binary_repr(int(there_can_be_only_one), 8)[-1]):
            lvl = there_can_be_only_one
        else:
            lvl = there_can_be_only_one + 1  # Make sure it's not a test
        printd(
            'Processing clearing of old github comments... '
            'lvl={lvl:}, clear_shortcut={clear_shortcut:}, contexts={contexts:}'.format(**locals()),
            topic='delete_comments',
        )
        if mode == 'no_edit':
            # We aren't editing comments, so we can do normal comment deletion behavior
            clear_old_test_report_comments(lvl=lvl, contexts=contexts, remove_all=clear_shortcut, **clear_kw)
        elif not edits_handled:
            printd('  Editing comments to clear old reports', topic='omfit_testing')
            # We're editing, so do cleanup by erasing parts of comments. new_content should've already been
            # appropriately defined as None (delete material from top comment) or '' (replace regular comment body
            # with blank).
            # In edit mode, cleanup isn't needed unless edits were skipped above. There is an overly complicated
            # interaction with the pre-existing system that handled comment creation and deletion; if we only ever did
            # edits, the whole thing could be simpler.
            edit_github_comment(
                new_content=new_content, mode=mode, separator=separator, comment_mark=comment_mark, **post_comment_to_github_keywords
            )
    else:
        printd('Skipped processing old github comment clearing', topic='delete_comments')
    return


class RedirectStdStreams(object):
    """Redirects stdout and stderr streams so you can merge them and get an easier to read log from a test."""

    # https://stackoverflow.com/a/6796752/6605826
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush()
        self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush()
        self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    # End of class RedirectStdStreams


def run_test_outside_framework(test_script, catch_exp_reports=True):
    """
    Deploys a test script outside the framework. Imports will be different.

    To include this in a test unit, do
    >>> return_code, log_tail = run_test_outside_framework(__file__)

    :param test_script: string
        Path to the file you want to test.
        If a test has a unit to test itself outside the framework, then this should be __file__.
        Also make sure a test can't run itself this way if it's already outside the framework.

    :param catch_exp_reports: bool
        Try to grab the end of the log starting with exception reports.
        Only works if test_script merges stdout and stderr; otherwise the exception reports will be somewhere else.
        You can use `with RedirectedStdStreams(stderr=sys.stdout):` in your code to do the merging.

    :return: (int, string)
        Return code (0 is success)
        End of output
    """

    print('Running {} in a separate process (no framework)'.format(os.path.basename(test_script)))
    result = subprocess.Popen(['python3', test_script], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    result.wait()
    return_code = result.returncode
    print('Run complete. Return code = {}'.format(return_code))
    output = result.communicate()[0]
    table_mark = 'Table of results for all tests:'
    excp_mark = 'Exception reports from failed tests'
    if catch_exp_reports and (excp_mark in output):
        log_tail = excp_mark + output.split(excp_mark)[-1]
    elif table_mark in output:
        log_tail = table_mark + output.split(table_mark)[-1]
    else:
        lines = output.split('\n')
        log_tail = '\n'.join(lines[-(min([10, len(lines)])) :])

    return return_code, log_tail


def _is_subtype(expected, basetype):
    """Stolen from unittest to support _AssertRaiseSimilarContext"""
    if isinstance(expected, tuple):
        return all(_is_subtype(e, basetype) for e in expected)
    return isinstance(expected, type) and issubclass(expected, basetype)


class _AssertRaiseSimilarContext(object):
    """
    Copied from unittest and modified to support loose matching
    """

    _base_type = BaseException
    _base_type_str = 'an exception type or tuple of exception types'

    def __init__(self, similar_exc, test_case, expected_regex=None):
        assert issubclass(similar_exc, Exception), f'similar_exc should be subclass of Exception, not {similar_exc}'
        self.similar_exc = similar_exc
        self.test_case = test_case
        if expected_regex is not None:
            expected_regex = re.compile(expected_regex)
        self.expected_regex = expected_regex
        self.obj_name = None
        self.msg = None

    def _raiseFailure(self, standard_msg):
        raise self.test_case.failureException(f'{self.msg} : {standard_msg}')

    def __enter__(self):
        return self

    def check_similarity(self, exc_type):
        """
        Checks whether an exception is similar to the nominally expected similar exception

        :param exc_type: class
            An exception class to be compared to self.similar_exc
        """
        if issubclass(exc_type, Exception):
            same_name = exc_type.__name__ == self.similar_exc.__name__
            same_bases = exc_type.__bases__ == self.similar_exc.__bases__
            return same_name and same_bases
        else:
            return False

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            try:
                exc_name = self.similar_exc.__name__
            except AttributeError:
                exc_name = str(self.similar_exc)
            if self.obj_name:
                self._raiseFailure("{} not raised by {}".format(exc_name, self.obj_name))
            else:
                self._raiseFailure("{} not raised".format(exc_name))
        else:
            traceback.clear_frames(tb)
        if (not issubclass(exc_type, self.similar_exc)) and (not self.check_similarity(exc_type)):
            # let unexpected exceptions pass through if their names don't match expectation
            return False
        # store exception, without traceback, for later retrieval
        self.exception = exc_value.with_traceback(None)
        if self.expected_regex is None:
            return True

        expected_regex = self.expected_regex
        if not expected_regex.search(str(exc_value)):
            self._raiseFailure('"{}" does not match "{}"'.format(expected_regex.pattern, str(exc_value)))
        return True

    def handle(self, name, args, kwargs):
        """
        If args is empty, assertRaises/Warns is being used as a
        context manager, so check for a 'msg' kwarg and return self.
        If args is not empty, call a callable passing positional and keyword
        arguments.
        """
        try:
            if not _is_subtype(self.similar_exc, self._base_type):
                raise TypeError('%s() arg 1 must be %s' % (name, self._base_type_str))
            if not args:
                self.msg = kwargs.pop('msg', None)
                if kwargs:
                    raise TypeError('%r is an invalid keyword argument for this function' % (next(iter(kwargs)),))
                return self

            callable_obj, *args = args
            try:
                self.obj_name = callable_obj.__name__
            except AttributeError:
                self.obj_name = str(callable_obj)
            with self:
                callable_obj(*args, **kwargs)
        finally:
            # bpo-23890: manually break a reference cycle
            self = None


class OMFITtest(unittest.TestCase):
    """
    Test case with some extra methods to help with OMFIT testing tasks

    To use this class, make your own class that is a subclass of this one:
    >> class TestMyStuff(OMFITtest):
    >>     notify_gh_status = True  # Example of a test setting you can override
    In the top of your file, override key test settings as needed

    Test settings you can override by defining them at the top of your class:
    -------------------------------
    :param warning_level: int
        Instructions for turning some warnings into exceptions & ignoring others
        -1: Make no changes to warnings
        0: No exceptions from warnings
        1: Ignores some math warnings related to NaNs & some which should be
            benign. Exceptions for other warnings.
        2: (RECOMMENDED) Ignores a small set of warnings which are probably
            benign, but exceptions for everything else.
        3: Exceptions for practically every warning. Only ignores some really
            inconsequential ones from OMFIT.
        4: No warnings allowed. Always throw exceptions!
        The warnings are changed before your test starts, so you can still
        override or change them in s() or __init__().

    :param count_figs: bool
        Enable counting of figures. Manage using collect_figs(n) after opening
        n figures. The actual figure count will be compared to the expected
        count (supplied by you as the argument), resulting in an AssertionError
        if the count does not match.

    :param count_guis: bool
        Enable counting of GUIs. Manage using collect_guis(n) after opening
        n GUIs. AssertionError if GUI count does not match expectation given
        via argument.

    :param leave_figs_open: bool
        Don't close figures at the end of each test (can lead to clutter)

    :param modules_to_load: list of strings or tuples
        Orders OMFIT to load the modules as indicated.
        Strings: modules ID. Tuples: (module ID, key)

    :param report_table: bool
        Keep a table of test results to include in final report

    :param table_sorting_columns: list of strings
        Names of columns to use for sorting table. Passed to table's group_by().
        This is most useful if you are adding extra columns to the results table
        during your test class's __init__() and overriding tearDown() to
        populate them.

    :param notify_gh_comment: int
        Turn on automatic report in a GitHub comment
        0: off
        1: always try to post or edit
        2: try to post or edit on failure only
        4: edit a comment instead of posting a new one if possible; only post if necessary
        8: edit the top comments and append test report or replace existing report with same context
        5 = behaviors of 4 and 1 (for example)

    :param notify_gh_status: bool
        Turn on automatic GitHub commit status updates

    :param gh_individual_status: int
        0 or False: No individual status contexts.
            Maximum of one status report if notify_gh_status is set.
        1 or True: Every test gets its own status context, including a pending
            status report when the test starts.
        2: Tests get their own status context only if they fail.
            No pending status for individual tests.
        3: Like 2 but ignores notify_gh_status and posts failed status reports
            even if reports are otherwise disabled.

    :param gh_overall_status_after_individual: bool
        Post the overall status even if individual status reports are enabled
        (set to 1 or True). Otherwise, the individual contexts replace the
        overall context. The overall status will be posted if individual status
        reports are set to 2 (only on failure).

    :param notify_slack: bool
        Post automatic test report on slack

    :param notify_email: bool
        Automatically send a test report to the user via email

    :param slack_channel: string
        Slack's code for the channel where the slack report should be posted,
        like "CHLS03MQC".

    :param slack_username: string
        The name to use for the apparent author of the slack post

    :param save_stats_to: dict-like
        Container for catching test statistics

    :param stats_key: string [optional]
        Test statistics are saved to save_stats_to[stats_key].
        stats_key will be automatically generated using the subclass name and a
        timestamp if left as None.

    :param topics_skipped: list of strings
        Provide a list of skipped test topics in order to have them included in
        the test report. The logic for skipping probably happens in the setup of
        your subclass, so we can't easily generate this list here.

    :param omfitx: reference to OMFITx
        Provide a reference to OMFITx to enable GUI counting and closing.
        This class might not be able to find OMFITx by itself, depending on how
        it is loaded.
    """

    # Test setup: All of these settings can be overridden in the subclass
    # Define them here instead of in init so they're available to class methods
    count_figs = False
    count_guis = False
    leave_figs_open = False
    modules_to_load = []
    omfitx = None
    report_table = True
    table_sorting_columns = ['Result', 'Time']
    notify_gh_status = 0
    notify_gh_comment = 14 * auto_test_mode  # 14 is append report of failures only to top comment
    gh_individual_status = 2 + auto_test_mode  # 2 is only on failure, 3 is on failure even if overall status is off.
    gh_overall_status_after_individual = True
    notify_slack = False
    notify_email = False
    slack_channel = 'auto_test_reports'
    slack_username = 'OMFIT_test_reports'
    save_stats_to = None
    stats_key = None
    topics_skipped = []
    warning_level = 2
    verbosity = 1
    debug_topic = None

    # Tracking
    stats = {
        'figures_expected': 0,
        'figures_detected': 0,
        'pre_opened_figs': None,  # We don't know this when the class gets defined. Update it in init.
        'already_saw_figures': None,
        'guis_expected': 0,  # Keep count the number of GUIs that should be opened by the test so the user can confirm
        'guis_detected': 0,
        'time_elapsed': {},
        'fig_count_discrepancy': 0,
        'gui_count_discrepancy': 0,
    }

    # Timing
    test_timing_t0 = 0
    test_timing_t1 = 0

    force_gh_status = None
    set_gh_status_keywords = {}  # This will be overwritten by manage_tests; don't control from here.

    def __init__(self, *args, **kwargs):
        import astropy.table

        super().__init__(*args, **kwargs)

        # Define sample experiment information: override later if needed
        experiment = dict(device='DIII-D', shot=154749, shots=[154749, 154754], time=2500.0, times=[2500.0, 3000.0])
        self.default_attr(experiment)

        # Reset stats
        for thing in self.stats.keys():
            if is_numeric(self.stats[thing]):
                self.stats[thing] = 0
        self.stats['pre_opened_figs'] = pyplot.get_fignums()
        self.stats['time_elapsed'] = {}
        self.force_gh_status = None  # manage_tests() might set this differently when running

        # Manage figures and GUIs
        if self.count_guis and self.omfitx is not None:
            try:
                self.omfitx.CloseAllGUIs()
            except NameError:
                # OMFITx not defined because running outside of GUI
                self.count_guis = False
            else:
                assert len(self.omfitx._GUIs) == 0, 'GUIs should have all been closed just now.'

        if len(self.modules_to_load):
            for m2l in self.modules_to_load:
                if isinstance(m2l, tuple):
                    m2l, tag = m2l
                else:
                    tag = '{}_test_copy'.format(m2l)
                try:
                    okay_ = OMFIT[tag]['SETTINGS']['MODULE']['ID'] == m2l
                except KeyError:
                    okay_ = False

                if okay_:
                    setattr(self, m2l, OMFIT[tag])
                else:
                    if hasattr(OMFIT, 'loadModule'):
                        OMFIT.loadModule(m2l, location="{}['{}']".format(treeLocation(OMFIT)[-1], tag), quiet=True)
                        setattr(self, m2l, OMFIT[tag])
                    else:
                        printe('UNABLE TO LOAD MODULES OUTSIDE OF THE FRAMEWORK. Failed to load {}.'.format(m2l))
                        setattr(self, m2l, None)

        if self.stats_key is None:
            self.stats_key = 'stats_{}_{}'.format(self.__class__.__name__, str(datetime.datetime.now()).replace(' ', '_'))

        if self.report_table:
            self.results_tables = [astropy.table.Table(names=('Name', 'Result', 'Time', 'Notes'), dtype=('S50', 'S30', 'f8', 'S50'))]
            self.results_tables[0]['Time'].unit = 'ms'
            self.results_tables[0]['Time'].format = '0.3e'
        else:
            self.results_tables = [None]
        # Make a place to allow for collection of test meta data to be printed with exception reports
        self.meta_data = {}

        # Tell the user about potential problems with their setup
        show_general = False
        if self.omfitx is None and self.count_guis:
            self.printv(
                'To count GUIs, please define self.omfitx = OMFITx in namespace that has access to OMFITx.\n'
                'This message was shown because count_guis was set but no reference to OMFITx was provided.',
                print_function=printw,
            )
            show_general = True
        if show_general:
            self.printv(
                '\nYou can just define things for your test class right at the top of the class definition.\n'
                'For example, for OMFITx, just put omfitx = OMFITx right after class.\n'
                'You can also put self.omfitx = OMFITx within __init__().',
                print_function=printw,
            )
        return

    def assertRaisesSimilar(self, similar_exc, *args, **kwargs):
        """
        Assert that some code raises an exception similar to the one provided.

        The purpose is to bypass the way OMFIT's .importCode() will provide a new reference to an exception
        that differs from the exception received by a script that does from OMFITlib_whatever import Thing

        """
        context = _AssertRaiseSimilarContext(similar_exc, self)
        try:
            return context.handle('assertRaises', args, kwargs)
        finally:
            # bpo-23890: manually break a reference cycle
            context = None

    def default_attr(self, attr, value=None):
        """
        Sets an attribute to a default value if it is not already set

        :param attr: string or dict
            string: the name of the attribute to set
            dict: call self once for each key/value pair, using keys for attr and values for value

        :param value: object
            The value to assign to the attribute
        """
        if isinstance(attr, dict):
            for k, v in attr.items():
                self.default_attr(k, v)
            return

        if getattr(self, attr, None) is None:
            setattr(self, attr, value)
        return

    def collect_guis(self, count=0):
        """
        Counts and then closes GUIs

        :param count: int
            Number of GUIs expected since last call.
            Actual and expected counts will be accumulated in self.stats.
        """
        if self.omfitx is None:
            return
        self.stats['guis_expected'] += int(bool(self.count_guis)) * count
        self.stats['guis_detected'] += len(self.omfitx._GUIs) * int(bool(self.count_guis))
        self.omfitx.CloseAllGUIs()
        if self.count_guis:
            prior_discrepancy = copy.copy(self.stats['gui_count_discrepancy'])
            expect_mod = self.stats['guis_expected'] + prior_discrepancy
            # Update the discrepancy so the same mismatch doesn't trigger another error during teardown.
            self.stats['gui_count_discrepancy'] = self.stats['guis_detected'] - self.stats['guis_expected']
            # fmt: off
            assert self.stats['guis_detected'] == expect_mod, (
                "{} GUIs detected doesn't match {} expected "
                "(expectation modified to include prior discrepancies: {})".format(
                    self.stats['guis_detected'], expect_mod, prior_discrepancy
                )
            )
            # fmt: on
        elif count > 0:
            self.printv('GUI counting is disabled. To count GUIs opened and compare to expectations, set self.count_guis')
        return

    def collect_figs(self, count=0):
        """
        Counts and/or closes figures

        :param count: int
            Number of figures expected since last call.
            Actual and expected counts will be accumulated in self.stats.
        """

        draw_problems = []
        draw_tracebacks = []

        self.stats['figures_expected'] += count * int(self.count_figs)
        if (count > 0) and (not self.count_figs):
            self.printv('Figure counting is disabled. To count figures opened & compare to expectations, set self.count_figs')

        if not self.leave_figs_open:
            for fignum in pyplot.get_fignums():
                if fignum not in self.stats['pre_opened_figs']:
                    try:
                        figure(fignum).canvas.draw()
                    except Exception as exc:
                        draw_problems += [exc]
                        draw_tracebacks += [''.join(traceback.format_exception(*sys.exc_info()))]
                    close(figure(fignum))
                    self.stats['figures_detected'] += int(self.count_figs)
            if self.count_figs:
                expect_mod = self.stats['figures_expected'] + self.stats['fig_count_discrepancy']
                # Update the discrepancy so the same mismatch doesn't trigger another error during teardown.
                self.stats['fig_count_discrepancy'] = self.stats['figures_detected'] - self.stats['figures_expected']
                # fmt: off
                assert self.stats['figures_detected'] == expect_mod, (
                    "{} figs detected doesn't match {} expected "
                    "(expectation modified to include prior discrepancies)".format(self.stats['figures_detected'], expect_mod)
                )
                # fmt: on
        else:
            try:
                pyplot.gcf().canvas.draw()
            except Exception as exc:
                draw_problems += [exc]
                draw_tracebacks += [''.join(traceback.format_exception(*sys.exc_info()))]

        if len(draw_problems) > 0:
            message = f'{len(draw_problems)} problem(s) detected while rendering the present group of plots:'
            printe(message)
            for idp, draw_problem in enumerate(draw_problems):
                print(f'Draw problem {idp + 1}/{len(draw_problems)}:')
                printe(draw_tracebacks[idp])
            print('Raising the first draw problem...')
            raise draw_problems[0]
        return

    def setUp(self):
        # Announce start of test
        test_id = self.id()
        test_name = '.'.join(test_id.split('.')[-2:])
        header = '\n'.join(['', '~' * len(test_name), test_name, '~' * len(test_name)])
        print(header)
        self.printdq(header)
        if self.count_figs:
            self.stats['fig_count_discrepancy'] = self.stats['figures_detected'] - self.stats['figures_expected']
            self.printdq(
                '    Starting {} with pre-existing overall figure count discrepancy of {}'.format(
                    test_name, self.stats['fig_count_discrepancy']
                )
            )
        if self.count_guis:
            self.stats['gui_count_discrepancy'] = self.stats['guis_detected'] - self.stats['guis_expected']
            self.printdq(
                '    Starting {} with pre-existing overall GUI count discrepancy of {}'.format(
                    test_name, self.stats['gui_count_discrepancy']
                )
            )
        if self.notify_gh_status and (int(self.gh_individual_status) == 1) and (self.force_gh_status is not False):
            context = self.get_context()
            response = set_gh_status(state='pending', context=context, **self.set_gh_status_keywords)
            self.printdq('gh_post', 'pending', context, response)
        self.stats['already_saw_figures'] = pyplot.get_fignums()
        self.test_timing_t0 = time.time()
        return

    def tearDown(self):
        import astropy.table

        # Announce end of test with debug print
        self.test_timing_t1 = time.time()
        dt = self.test_timing_t1 - self.test_timing_t0
        test_name = '.'.join(self.id().split('.')[-2:])
        self.printdq('    {} done.'.format(test_name))
        self.printdq('    {} took {:0.6f} s\n'.format(test_name, dt))
        self.stats['time_elapsed'][test_name] = dt

        # Cleanup figures and GUIs between tests
        try:
            self.collect_figs()
            self.collect_guis()
        except AssertionError as fg_exc:
            fig_gui_mismatch = fg_exc
        else:
            fig_gui_mismatch = False

        # Handle individual GitHub status reports & Results table

        # Check for errors/failures in order to get state & description.  https://stackoverflow.com/a/39606065/6605826
        if hasattr(self, '_outcome'):  # Python 3.4+
            result = self.defaultTestResult()  # these 2 methods have no side effects
            self._feedErrorsToResult(result, self._outcome.errors)
            problem = result.errors or result.failures
            state = (not problem) and (not fig_gui_mismatch)
            if result.errors:
                exc_note = result.errors[0][1].strip().split('\n')[-1]
            elif result.failures:
                exc_note = result.failures[0][1].strip().split('\n')[-1]
            else:
                exc_note = '' if state else "(couldn't get exception report)"
        else:  # Python 3.2 - 3.3 or 3.0 - 3.1 and 2.7
            # result = getattr(self, '_outcomeForDoCleanups', self._resultForDoCleanups)  # DOESN'T WORK RELIABLY
            exc_type, exc_value, exc_traceback = sys.exc_info()
            state = (exc_type in [None, unittest.case._ExpectedFailure]) and not fig_gui_mismatch
            exc_note = '' if exc_value is None else '{}: {}'.format(exc_type.__name__, exc_value)

        gis = int(self.gh_individual_status)
        ngs = self.notify_gh_status
        if ((gis == 1) and ngs) or ((gis == 2) and (not state) and ngs) or ((gis == 3) and (not state)):
            description = test_comp_info_summary() + exc_note
            context = self.get_context()

            # Post it
            try:
                response = set_gh_status(state=state, context=context, description=description, **self.set_gh_status_keywords)
            except ValueError:  # Bad/missing token (expected common problem) results in ValueError
                self.printv('Failed to update GitHub status')
            else:
                self.printdq('gh_post', state, context, description, response)

        if self.results_tables[0] is not None:
            test_result = 'pass' if state else 'FAIL'
            self.printdq(
                '  Adding row to results_table: {}, {}, {:0.2e} ms, {} | {}'.format(test_name, test_result, dt * 1000, exc_note, self.id())
            )
            self.results_tables[0].add_row()
            self.results_tables[0][-1]['Time'] = dt * 1000  # Convert to ms
            self.results_tables[0][-1]['Result'] = test_result
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=astropy.table.StringTruncateWarning)
                self.results_tables[0][-1]['Name'] = test_name
                self.results_tables[0][-1]['Notes'] = exc_note

        if self.leave_figs_open:
            # If figures aren't being closed, give them nicer titles at least
            new_plots = [plot for plot in pyplot.get_fignums() if plot not in self.stats['already_saw_figures']]
            for i, plot in enumerate(new_plots):
                pyplot.figure(plot).canvas.set_window_title('{} {}'.format(test_name, i))

        if fig_gui_mismatch:
            raise fig_gui_mismatch

        self.printdq('-' * 80 + '\n')
        return

    def get_context(self):
        """Sanitize test id() so it doesn't start with omfit_classes.omfit_python or who knows what --> define context"""
        class_name = self.__class__.__name__
        test_name = self.id().split(class_name)[-1][1:]  # First char will be .
        pyver = '.'.join(map(str, sys.version_info[0:2]))
        context = 'p{} {}.{}@{}'.format(pyver, class_name, test_name, get_server_name())
        return context

    @classmethod
    def printv(cls, *args, **kw):
        if cls.verbosity > 0:
            kw.pop('print_function', print)(*args)
        return

    def printdq(self, *args):
        topic = self.debug_topic or self.__class__.__name__
        printd(*args, topic=topic)
        return

    @classmethod
    def tearDownClass(cls):

        if cls.omfitx is not None and cls.count_guis:
            cls.printv('  This test should have opened {:} GUI(s)'.format(cls.stats['guis_expected']))
            guis_during_teardown = len(cls.omfitx._GUIs)
            cls.stats['guis_detected'] += guis_during_teardown
            if not cls.leave_figs_open:
                cls.omfitx.CloseAllGUIs()
            gui_count_match = cls.stats['guis_detected'] == cls.stats['guis_expected']
            cls.printv(
                '\n{} GUIs were counted, with {} counted while tearing down the test class.'.format(
                    cls.stats['guis_detected'], guis_during_teardown
                )
            )
            cls.printv(
                '{} GUIs were expected. There is {} problem here.'.format(cls.stats['guis_expected'], ['a', 'no'][int(gui_count_match)])
            )
        else:
            gui_count_match = True

        if cls.count_figs:
            # Cleanup any remaining figures (they probably were all taken care of in tearDown() after each test)
            if cls.leave_figs_open:
                cls.stats['figures_detected'] = len(pyplot.get_fignums()) - len(cls.stats['pre_opened_figs'])
            else:
                for fignum in pyplot.get_fignums():
                    if fignum not in cls.stats['pre_opened_figs']:
                        close(figure(fignum))
                        cls.stats['figures_detected'] += 1
            count_match = cls.stats['figures_detected'] == cls.stats['figures_expected']
            cls.printv('\n{} figures were counted while tearing down the test class.'.format(cls.stats['figures_detected']))
            cls.printv(
                '{} figures should have been opened. There is {} problem here.'.format(
                    cls.stats['figures_expected'], ['a', 'no'][int(count_match)]
                )
            )
        else:
            count_match = True

        if isinstance(cls.save_stats_to, dict):
            cls.printv('Saving test statistics within user-provided dict-like object with key {}'.format(stats_key))
            cls.save_stats_to[stats_key] = cls.stats

        # Put backup experiment settings back in place
        if OMFIT is not None:
            OMFIT['MainSettings']['Experiment'].update(getattr(cls, 'backup_experiment', {}))
            backups = [k for k in dir(cls) if k.startswith('backup_experiment_')]
            for backup in backups:
                module = backup.split('backup_experiment_')[-1]
                OMFIT['{}_test_copy'.format(module)].experiment(**getattr(cls, backup, {}))

        if cls.leave_figs_open:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=UserWarning, message='.*non-GUI backend.*')
                pyplot.show()

        # Get angry?
        assert count_match, 'Number of figures detected ({}) does not match number of figures expected ({})'.format(
            cls.stats['figures_detected'], cls.stats['figures_expected']
        )
        assert gui_count_match, 'Number of GUIs detected ({}) does not match number of GUIs expected ({})'.format(
            cls.stats['guis_detected'], cls.stats['guis_expected']
        )
        return

    # End of class OMFITtest


# noinspection PyBroadException
def test_comp_info_summary(short=False, long_form=False):
    """
    Generates a short summary of computing environment setup

    Potentially includes hostname, git branch, current time, and commit hashes,
    depending on short & long_form keywords

    :param short: bool
        Return compact form: squeeze onto one line and drop branch info. Since
        this is intended for GitHub status reports, the branch is probably
        already known, and it won't fit, anyway.

    :param long_form: bool
        Add more info to the end, concerning commit hashes. This is intended for
        non-GitHub uses like email and slack, where the report won't be attached
        to a commit history in an obvious way. This triggers a simple append
        operation that will work even if short=True.

    :return: string
        Intended to be appended to a test report
    """
    try:
        test_branch = repo.active_branch()[0]
    except Exception:
        test_branch = '<<<Failed to look up current branch>>>'
    try:
        omfit_sha = repo.get_hash(repo_active_branch_commit)
        branch_sha = repo.get_hash('HEAD~0')
    except Exception:
        omfit_sha = branch_sha = '<<<Failed to determine commit hash>>>'

    pyver = '.'.join(map(str, sys.version_info[0 : 2 if short else 3]))

    form = 'p{v:} {h:} @ {t:} ' if short else 'Py ver {v:}\nHost: {h:}\nCompleted {t:}\n' 'On branch {b:}\n'
    if long_form:
        form += 'Most recent commit @ OMFIT start time: {omfit_sha:}\n' 'Most recent commit on the branch now: {branch_sha:}\n'
    return form.format(
        h=socket.gethostname(),
        t=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        b=test_branch,
        omfit_sha=omfit_sha,
        branch_sha=branch_sha,
        v=pyver,
    )


def manage_tests(
    tests,
    failfast=False,
    separate=True,
    combined_context_name=None,
    force_gh_status=None,
    force_gh_comment=None,
    force_email=None,
    force_slack=None,
    force_warning_level=None,
    print_report=True,
    there_can_be_only_one=True,
    raise_if_errors=True,
    max_table_width=-1,
    set_gh_status_keywords=None,
    post_comment_to_github_keywords=None,
    ut_verbosity=1,
    ut_stream=None,
    only_these=None,
    **kw,
):
    """
    Utility for running a set of OMFITtest-based test suites
    Example usage:
    >> class TestOmfitThingy(OMFITtest):
    >>     def test_thingy_init(self):
    >>         assert 1 != 0, '1 should not be 0'
    >> manage_tests(TestOmfitThingy)

    :param tests: OMFITtest instance or list of OMFITtest instances
        Define tests to run

    :param failfast: bool
        Passed straight to unittest. Causes execution to stop at the first error
        instead of running all tests and reporting which pass/fail.

    :param separate: bool
        Run each test suite separately and give it a separate context. Otherwise
        they'll have a single combined context.

    :param combined_context_name: string [optional]
        If not separate, override the automatic name
        ('+'.join([test.__class__.__name__) for test in tests]))

    :param force_gh_status: bool [optional]
        If None, use GitHub status post settings from the items in tests.
        If True or False: force status updates on/off.

    :param force_gh_comment: bool or int [optional]
        Like force_gh_status, but for comments, and with extra options:
        Set to 2 to post comments only on failure.

    :param force_email: bool [optional]
        None: notify_email on/off defined by test.
        True or False: force email notifications to be on or off.

    :param force_slack: bool [optional]
        None: notify_slack on/off defined by test.
        True or False: force slack notifications to be on or off.

    :param force_warning_level: int [optional]
        None: warning_level defined by test.
        int: Force the warning level for all tests to be this value.

    :param print_report: bool
        Print to console / command line?

    :param there_can_be_only_one: True, None or castable as int
        This value is interpreted as a set of binary flags. So 6 should be interpreted as options 2 and 4 active.

        A value of True is converted into 255 (all the bits are True, including unused bits).
        A value of None is replaced by the default value, which is True or 255.
        A float or string will work if it can be converted safely by int().

        1: Any of the flags will activate this feature. The 1 bit has no special meaning beyond activation.
            If active, old github comments will be deleted. The newest report may be retained.
        2: Limit deletion to reports that match the combined context of the test being run.
        4: Only protect the latest comment if it reports a failure; if the last test passed, all comments may be deleted
        8: Limit scope to comments with matching username

    :param raise_if_errors: bool
        Raise an OMFITexception at the end if there were any errors

    :param max_table_width: int
        Width in columns for the results table, if applicable. If too small,
        some columns will be hidden. Set to -1 to allow the table to be any
        width.

    :param set_gh_status_keywords: dict [optional]
        Dictionary of keywords to pass to set_gh_status()

    :param post_comment_to_github_keywords: dict [optional]
        Dictionary of keywords to pass to post_comment_to_github(), like thread, org, repository, and token

    :param ut_verbosity: int
        Verbosity level for unittest. 1 is normal, 0 suppresses ., E, and F reports from unittest as it runs.

    :param ut_stream:
        Output stream for unittest, such as StingIO() or sys.stdout

    :param only_these: string or list of strings
        Names of test units to run (with or without leading `test_`). Other test units will not be run. (None to run all tests)

    :param kw: quietly ignores other keywords

    :return: tuple containing:
        list of unittest results
        astropy.table.Table instance containing test results
        string reporting test results, including a formatted version of the table
    """
    import astropy.table
    import functools

    # Sanitize
    tests = tolist(tests)  # It's just easier to enter 'Test' than ['Test'] for only one. Let's allow that.
    if only_these is not None:  # It's just easier to enter 'asd' than ['test_asd']. Let's allow that.
        only_these = tolist(only_these)
        only_these = list(map(lambda x: x if x.startswith('test_') else 'test_' + x, only_these))
    server_name = get_server_name()
    set_gh_status_keywords = set_gh_status_keywords or {}
    post_comment_to_github_keywords = post_comment_to_github_keywords or {}
    for test in tests:
        test.set_gh_status_keywords = set_gh_status_keywords

    # Figure out flags
    gh_status = [
        force_gh_status or (test.notify_gh_status * bool(test.gh_overall_status_after_individual or (test.gh_individual_status != 1)))
        for test in tests
    ]
    gh_comment = [force_gh_comment or test.notify_gh_comment for test in tests]
    notify_email = [force_email or test.notify_email for test in tests]
    notify_slack = [force_slack or test.notify_slack for test in tests]
    warning_levels = [force_warning_level or test.warning_level for test in tests]
    if there_can_be_only_one is True or there_can_be_only_one is None:
        # True turns on all the bits, even unused ones for future compatibility.
        # None does default behavior, which is True which is 255
        there_can_be_only_one = 255
    else:
        there_can_be_only_one = int(there_can_be_only_one)

    for test in tests:
        test.force_gh_status = force_gh_status

    # Look up more settings from the tests
    if np.any(notify_slack):
        slack_channel = common_in_list([test.slack_channel for test in tests])
    else:
        slack_channel = None
    skipped_topics = [test.topics_skipped for test in tests]
    table_sorting_columns = common_in_list(['\n'.join(test.table_sorting_columns) for test in tests]).split('\n')

    # Prepare context information
    contexts = [test.__name__ + ('*' if len(test.topics_skipped) or only_these is not None else '') for test in tests]
    pyver_header = 'p' + '.'.join(map(str, sys.version_info[0:2]))

    ut_stream = ut_stream or StringIO()

    def post_pending_status():
        for ghs, context_ in zip(gh_status, contexts):
            if ghs:
                desc = test_comp_info_summary(short=True)
                resp = set_gh_status(state='pending', context=context_, description=desc, **set_gh_status_keywords)
                printd(
                    'Got response {res:} when posting GitHub status state = {s:}, context = {c:}, '
                    'description = {d:}'.format(s='pending', c=context_, d=desc, res=resp),
                    topic='omfit_testing',
                )

    # Run tests and collect results and settings
    meta_data = {}
    if separate:
        # Do each OMFITtest instance separately and give it its own context
        contexts = ['{} {}@{}'.format(pyver_header, context, server_name) for context in contexts]
        post_pending_status()
        results = []
        results_tables = []
        suite_tests = []
        for i, test in enumerate(tests):
            with setup_warnings(warning_levels[i]):
                if only_these is None:
                    suite = unittest.makeSuite(test)
                else:
                    suite = unittest.TestSuite()
                    for method in tolist(only_these):
                        try:
                            suite.addTest(test(method))
                        except ValueError as excp:
                            printd(excp)

                suite_tests += suite._tests
                results += [unittest.TextTestRunner(verbosity=ut_verbosity, stream=ut_stream, failfast=failfast).run(suite)]
            # Add results tables (probably just a one element list of 1 table) to the list
            for suite_test in suite_tests:
                meta_data.update(suite_test.meta_data)
                if getattr(suite_test, 'results_tables', [None])[0] is not None:
                    results_tables += copy.copy(suite_test.results_tables)
                    suite_test.results_tables = [None]  # Reset
                    printd('Cleared results table', topic='omfit_testing')

    else:
        # Merge all OMFITtest instances into one context containing all of the sub-tests together
        gh_status = [functools.reduce(lambda x, y: x | y, gh_status)]
        gh_comment = [functools.reduce(lambda x, y: x | y, gh_comment)]
        contexts = [combined_context_name or '{} {}@{}'.format(pyver_header, '+'.join(contexts), server_name)]
        post_pending_status()
        # Form test suite and grab list of tests within the suite so they can be interrogated later
        # Making a suite with makeSuite() & then adding to it with suite.addTest() can result in multiple copies of test
        # So do this instead:
        if only_these is None:
            suite_list = []
        else:
            suite_list = [unittest.TestSuite()]
        for test in tests:
            if only_these is None:
                suite_list.append(unittest.TestLoader().loadTestsFromTestCase(test))
            else:
                for method in tolist(only_these):
                    try:
                        suite_list[0].addTest(test(method))
                    except ValueError as excp:
                        printe(excp)

        combo_suite = unittest.TestSuite(suite_list)
        suite_tests = []
        for suite in suite_list:
            suite_tests += suite._tests
        with setup_warnings(max(warning_levels)):
            results = [unittest.TextTestRunner(verbosity=ut_verbosity, stream=ut_stream, failfast=failfast).run(combo_suite)]

        new_skip = []
        for context, skipped in zip(contexts, skipped_topics):
            new_skip += ['.'.join([context, skip]) for skip in skipped]
        skipped_topics = [new_skip]  # [[context+'.'+skipped for context, skipped in zip(contexts, skipped_topics)]]
        notify_email = [np.any(notify_email)]
        notify_slack = [np.any(notify_slack)]
        results_tables = []
        for suite_test in suite_tests:
            meta_data.update(suite_test.meta_data)
            printd(
                'suite_test = {}, has results table = {}, type = {}'.format(
                    suite_test, hasattr(suite_test, 'results_tables'), type(suite_test)
                ),
                topic='omfit_testing',
            )
            results_tables += copy.copy(getattr(suite_test, 'results_tables', [None]))
        results_tables = [res_tab for res_tab in results_tables if res_tab is not None]

    printd('meta_data = {}'.format(meta_data), topic='omfit_testing')
    warn_context = '{}: {}'.format('separate' if separate else 'combined', ', '.join([test.__name__ for test in tests]))
    if len(results_tables):
        a = []
        while (len(a) == 0) and len(results_tables):
            a = results_tables.pop(0)  # Skip empty tables, if any
        results_table = a
        for rt in results_tables:
            if len(rt):
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', category=DeprecationWarning)
                    results_table = astropy.table.join(results_table, rt, join_type='outer')
        # noinspection PyBroadException
        try:
            results_table = results_table.group_by(table_sorting_columns)
        except Exception as excp:
            printw('Error sorting test results table. Columns may not be in the preferred order. ({})'.format(warn_context))
            excp_stack = traceback.format_exception(*sys.exc_info())
            printe('    The error that caused this was {}'.format(excp))
            printe(''.join(excp_stack))
        column_names = list(results_table.columns.keys())
        alignments = ['<' if cn == 'Notes' else '>' for cn in column_names]
        if len(results_table):
            rtf = '\n'.join(results_table.pformat(align=alignments, max_width=max_table_width, max_lines=-1))
            exp_res = np.sum([result.testsRun - len(result.skipped) for result in results])
            if len(results_table) != exp_res:
                printw(
                    'ERROR forming results table. Expected {} results, but table length is {}. ({})'.format(
                        exp_res, len(results_table), warn_context
                    )
                )
        else:
            rtf = None

    else:
        results_table = rtf = None

    # Prepare reports
    the_gh_comment = ''
    email_body = ''
    slack_message = ''
    errors = 0
    total_tests_run = 0
    total_tests_skipped = 0
    skipped_comment = False
    # There will usually be one result. To have more, must supply list of test suites and set separate=False.
    for i in range(len(results)):
        # Gather general information
        result = results[i]
        context = contexts[i]
        failed_tests = [f[0] for f in result.failures] + [f[0] for f in result.errors]
        failed_long_names = [ft.__class__.__name__ + '.' + getattr(ft, '_testMethodName', '?') for ft in failed_tests]
        failed_names = [getattr(ft, '_testMethodName', '?') for ft in failed_tests]
        meta_data_chunks = [meta_data.get(fln, None) for fln in failed_long_names]
        error_reports = [f[1] for f in result.failures] + [f[1] for f in result.errors]
        error_summaries = [[a for a in er.split('\n') if len(a)][-1] for er in error_reports]
        errors += len(failed_tests)
        printd(
            'manage_tests: i = {}, result = {}, failed_long_names = {}, failed_names = {}, failed_tests = {}, '
            'error_reports = {}, meta_data_chunks = {}'.format(
                i, result, failed_long_names, failed_names, failed_tests, error_reports, meta_data_chunks
            ),
            topic='omfit_testing',
        )
        tests_run = result.testsRun
        tests_skipped = len(result.skipped)
        total_tests_run += tests_run
        total_tests_skipped += tests_skipped
        skiplist = [ssk[0]._testMethodName for ssk in result.skipped]

        state = (len(failed_tests)) == 0
        conclusion = context + (' PASSED! Congratulations!' if state else ' FAILED!')
        comp_info = test_comp_info_summary(short=True)
        if len(skipped_topics[i]) or tests_skipped:
            skipped_topics_report_short = ', skip{}t:{}i'.format(len(skipped_topics[i]), tests_skipped)
        else:
            skipped_topics_report_short = ''
        skipped_topics_report = '{} test topics were skipped'.format(len(skipped_topics[i]))
        skipped_topics_report_2 = '{} individual tests were skipped'.format(tests_skipped)
        skipped_topics_report_long = skipped_topics_report + (
            ':\n  - ' + '\n  - '.join(skipped_topics[i]) if len(skipped_topics[i]) else ''
        )
        skipped_topics_report_long += '\n\n' + skipped_topics_report_2 + (':\n  - ' + '\n  - '.join(skiplist) if tests_skipped else '')
        skipped_topics_report += skipped_topics_report_2

        test_count_report = '{} individual tests were considered'.format(tests_run)
        test_count_report += '\n{} individual tests were actually executed'.format(tests_run - tests_skipped)

        # Handle GitHub status
        if gh_status[i]:
            description = comp_info + ' ran {} test(s)'.format(tests_run) + skipped_topics_report_short
            for ft, er in zip(failed_names, error_summaries):
                description += '\n{}: {}'.format(ft, er)
            try:
                response = set_gh_status(state=state, context=context, description=description, **set_gh_status_keywords)
            except ValueError:  # Bad/missing token (expected common problem) results in ValueError
                print('GitHub comment post failed!')
            else:
                printd(
                    'Got response {res:} when posting GitHub status state = {s:}, context = {c:}, '
                    'description = {d:}'.format(s=state, c=context, d=description, res=response),
                    topic='omfit_testing',
                )

        # Handle GitHub comments
        ghc_bits = [int(bb) for bb in np.binary_repr(int(gh_comment[i]), 8)[::-1]]
        if ghc_bits[0] or (ghc_bits[1] and len(failed_tests)):
            comment_details_form = '<details><summary>{}</summary>\n{}\n</details>\n'
            comment_part = '### {conclusion:}\n{tests:}\n{skip:}\n'.format(
                conclusion=conclusion,
                tests=test_count_report,
                skip=comment_details_form.format('skipped tests', skipped_topics_report_long),
            )
            if len(failed_tests):
                comment_part += '<details><summary>Exception reports</summary>'
                for ft, er, mdc in zip(failed_long_names, error_reports, meta_data_chunks):
                    comment_part += '\n{}\n\n```\n{}```\n\nMeta data for {}:\n{}\n'.format(ft, er, ft, mdc)
                comment_part += '</details>\n\n'
            the_gh_comment += comment_part
        elif ghc_bits[1] and (not len(failed_tests)):
            skipped_comment = True

        # Handle email body
        if notify_email[i]:
            email_part = '{conclusion:}\n{tests:}\n{skip:}'.format(
                conclusion=conclusion, tests=test_count_report, skip=skipped_topics_report_long
            )
            if len(failed_tests):
                email_part += '\nException reports:\n-----\n'
                for ft, er, mdc in zip(failed_long_names, error_reports, meta_data_chunks):
                    email_part += '\n{}\n\n{}\n\nMeta data for {}:\n{}\n'.format(ft, er, ft, mdc)
            email_body += email_part + '-----'

        # Handle slack message
        if notify_slack[i]:
            slack_message += conclusion + '\n' + test_count_report + '\n' + skipped_topics_report + '\n'
            if len(failed_tests):
                slack_message += 'Exception reports for {}:\n'.format(context)
                for ft, er, mdc in zip(failed_long_names, error_reports, meta_data_chunks):
                    slack_message += '{}\n{}\nMeta data for {}:\n{}\n'.format(ft, er, ft, mdc)

        # Print to console
        if print_report:
            if state:
                printi(conclusion)
                print(test_count_report)
                print(skipped_topics_report_long)
            else:
                printe(conclusion)
                print(test_count_report)
                print(skipped_topics_report_long)
                print('Exception reports from failed tests in {}'.format(context))
                for ft, er, mdc in zip(failed_tests, error_reports, meta_data_chunks):
                    print(ft)
                    printe(er)
                    print('Meta data for {}:'.format(ft))
                    printw(mdc)

    # Finalize reports
    notice = 'Some tests failed!' if errors > 0 else 'All tests passed!'

    total_test_count_report = '{} individual tests were executed & {} were skipped while running all test cases'.format(
        total_tests_run, total_tests_skipped
    )

    # Finalize and post GitHub comment (if applicable)
    gh_test_report_update(
        the_gh_comment=the_gh_comment,
        contexts=contexts,
        gh_comment=gh_comment,
        there_can_be_only_one=there_can_be_only_one,
        rtf=rtf,
        errors=errors,
        skipped_comment=skipped_comment,
        post_comment_to_github_keywords=post_comment_to_github_keywords,
        total_test_count_report=total_test_count_report,
    )

    # Finalize and send email (if applicable)
    if len(email_body):
        prn = get_pull_request_number()
        remote, org, repository, branch = get_gh_remote_org_repo_branch()
        if prn is None:
            pr_info = 'Did not find an open pull request for this branch.'
        else:
            pr_info = 'Open pull request for this branch: {prn:} . URL = https://github.com/{org:}/{repo:}/pull/{prn:}'
        pr_info = pr_info.format(prn=prn, repo=repository, org=org)
        email_body = '{n:}\n\n{e:} errors were detected while testing {c:}\n\n{run:}\n{b:}\n=====\n{ci:}\n{pr:}'.format(
            n=notice,
            e=errors,
            c=' + '.join(contexts),
            r=total_test_count_report,
            b=email_body,
            ci=test_comp_info_summary(long_form=True),
            run=total_test_count_report,
            pr=pr_info,
        )
        if results_table is not None:
            email_body += '\n\n' + rtf
        email_subject = '{notice:} {context:} had {errors:} errors'.format(notice=notice, context=' + '.join(contexts), errors=errors)
        printd('Sending email: subject = {}, body = {}'.format(email_subject, email_body), topic='omfit_testing')
        send_email(to=MainSettings['SETUP']['email'], subject=email_subject, message=email_body, fromm=MainSettings['SETUP']['email'])

    # Finalize and post slack message (if applicable)
    if len(slack_message):
        from omfit_classes.omfit_slack import post_to_slack

        remote, org, repository, branch = get_gh_remote_org_repo_branch()
        prn = get_pull_request_number(org=org, repository=repository)
        if prn is not None:
            pr_info = 'PR URL: https://github.com/{org:}/{rep:}/pull/{prn:}\n'.format(prn=prn, rep=repository, org=org)
        else:
            pr_info = ''
        slack_message = '''
{notice:}
{errors:} errors while testing {context:}
{run:}
{body:}
{comp:}
{pr_info:}'''.strip().format(
            notice=notice,
            errors=errors,
            context=' + '.join(contexts),
            body=slack_message,
            comp=test_comp_info_summary(),
            pr_info=pr_info,
            run=total_test_count_report,
        )
        if results_table is not None:
            slack_message += '\n\n' + rtf
        try:
            post_to_slack(message=slack_message, channel=slack_channel)
        except ValueError as excp:  # Bad/missing token (expected common problem) results in ValueError
            printe(repr(excp))
            printe('Slack post failed')

    # Closing remarks to console
    err_count = '\n{er:} error(s) were detected while testing {ct:}'.format(er=errors, ct=' + '.join(contexts))
    error_function = printe if errors > 0 else printi
    report_strings = [err_count]
    report_functions = [error_function]
    if results_table is not None:
        report_strings += ['\nTable of results for all tests:\n\n{}'.format(rtf), err_count]
        report_functions += [print, error_function]

    if print_report:
        for report_function, report_string in zip(report_functions, report_strings):
            report_function(report_string)

    if raise_if_errors and errors > 0:
        raise OMFITexception('{ct:} failed with {er:} errors'.format(er=errors, ct=' + '.join(contexts)))

    return results, results_table, '\n'.join(report_strings)


def run_test_series(exit_at_end=False, post_gh_comment=False, post_gh_status=False, tests=None, test_plan_file=None, script_timeout=0):
    """
    Run series of regression tests and store results directly in OMFIT tree

    :param exit_at_end: bool
        Quit python session on exit

    :param post_gh_comment: bool
        Post comment to github

    :param post_gh_status: bool or 'final'
        Post status to github for each test (or only final status of whole test with 'final')

    :param tests: list of strings
        names of regression tests to be run

    :param test_plan_file: string
        Filename with a YAML file containing a test plan

    :param script_timeout: int
        Number of seconds before an exception is thrown to kill the script for taking too long. 0 to disable.
    """

    from omfit_classes.omfit_python import OMFITpythonTest
    from omfit_classes.omfit_base import OMFITtree

    # Tuning parameters for prioritization system. Higher priority tests run before lower priority tests. The group of
    # tests that failed last time is sorted within itself and goes before the group of tests that passes last time.
    initial_priority = 1  # When new tests are added to the series, they start with this priority
    # This is just a backup. The setting that's more likely to be used is in bin/verify_build.py
    priority_fail_increment = 1  # x>0 Increases priority on fail; repeat offenders tend to run first
    priority_success_multiplier = 0.7165  # 0<x<1 Priority decays on success; prioritize recent problems
    priority_cap = 5  # Priority can't wind up too far
    priority_failfast_thresh = 1  # Elevated priority triggers failfast behavior, even if test passed last time.
    #                               Set higher than cap to disable failfast on tests that passed on the last iteration.
    priority_failfast_thresh_include = priority_failfast_thresh  # High priority tests aren't skipped by failfast
    priority_speed_bonus_scale = 0.01  # Maximum size of the speed bonus
    priority_speed_bonus_timescale = 10.0  # Duration (s) that gets max speed bonus; no benefit for shorter than this

    if test_plan_file is not None:
        with open(test_plan_file, 'r') as f:
            test_plan = yaml.load(f.read(), Loader=yaml.Loader)
            exit_at_end = test_plan.get('exit_at_end', exit_at_end)
            post_gh_comment = test_plan.get('post_gh_comment', post_gh_comment)
            post_gh_status = test_plan.get('post_gh_status', post_gh_status)
            script_timeout = test_plan.get('script_timeout', script_timeout)
    else:
        tests = tests or []
        test_plan = {'tests': [{"name": test} for test in tests]}

    gh = OMFIT['MainSettings']['SERVER']['GITHUB_username'] and (post_gh_comment or post_gh_status)
    gh_all = gh and (post_gh_status != 'final')
    if gh:
        print('GitHub interaction was requested. Making sure you have a valid token (or else Exception!)...')
        get_OMFIT_GitHub_token()

        # noinspection PyBroadException
        try:
            test_branch = repo.active_branch()[0]
        except Exception:
            test_branch = '<<<Failed to look up current branch>>>'

        # Get a hostname for the server for use in setting context
        hostname = socket.gethostname()
        servername = get_server_name(hostname)
        pyverheader = 'p' + '.'.join(map(str, sys.version_info[0:2]))

        # TODO: Remove context_legacy after merging requires the new context.
        context_legacy = '{} run_test_series@{}'.format(pyverheader, servername)
        context = 'regression_test_runs@{}'.format(servername)

        c_fn = OMFITsrc + os.path.sep + '.regression_test_runs.context'
        with open(c_fn, 'w') as f:
            f.write(context)
        comp_info_start = 'Executing on host {h:}\nTest started {t:}\nRunning on branch {b:}'.format(
            h=hostname, t=datetime.datetime.now(), b=test_branch
        )

        if post_gh_status:
            set_gh_status(state='pending', context=context, description=comp_info_start)
            # TODO: Remove the next line after merging requires the new context.
            set_gh_status(state='pending', context=context_legacy, description=comp_info_start)
    else:
        servername = hostname = test_branch = pyverheader = context = comp_info_start = None

    success = []
    # regression scripts, errors and times
    OMFIT['regression_errors'] = errors = SortedDict()
    OMFIT['regression_allowed_errors'] = allowed_errors = SortedDict()
    OMFIT['regression_stacks'] = stacks = SortedDict()
    OMFIT['regression_times'] = times = SortedDict()
    OMFIT['regression_scripts'] = OMFITtree(sorted=True)
    # record what keys are in the OMFIT tree now to cleanup later
    old_keys = list(OMFIT.keys())

    def timeout_handler(signum, frame):
        signal.alarm(0)
        raise KeyboardInterrupt("Script timed out")

    signal.signal(signal.SIGALRM, timeout_handler)
    test_plan['results'] = {}
    print('Test plan:')
    for test in test_plan['tests']:
        # Define status and priority prior to failfast check, so priorities aren't forgotten when tests are skipped
        test_plan['results'][test['name']] = dict(status='not started', priority=test.get('priority', initial_priority))
        print(test['name'], 'starting priority:', test_plan['results'][test['name']]['priority'])

    last_commit_check_time = time.time()
    tests_since_last_commit_check = 0
    for test in test_plan['tests']:

        # Check github for a newer commit and abort if it's newer than the current ones if the option is enabled.
        if test_plan.get('newer_commit_abort', False) and (
            (time.time() - last_commit_check_time > test_plan.get('newer_commit_check_period', 120))
            or (tests_since_last_commit_check > test_plan.get('newer_commit_test_num_period', 10))
        ):
            print("Checking for newer github commit.")
            if not on_latest_gh_commit():
                print("Newer commit to branch detected, aborting remaining tests.")
                break
            tests_since_last_commit_check = 0
            last_commit_check_time = time.time()

        # If we are on the first previously non-failing test and
        # There have been other failing tests beforehand, abort to
        # save time (unless the test has built up high enough priority).
        # If there haven't been any errors yet then test everything else in the plan
        if (
            test_plan.get('fail_fast', False)
            and (test.get('priority', initial_priority) < priority_failfast_thresh_include)
            and (test.get('last_status', 'not run') != 'failure')
        ):
            if len(errors) > 0:
                break
            else:
                test_plan['fail_fast'] = False

        test_plan['results'][test['name']]['status'] = 'incomplete'
        # Individual tests can change their own warning level. 1 is a tolerant choice for generic tests.
        with setup_warnings(1):
            OMFIT['regression_scripts'][test['name']] = OMFITpythonTest(
                OMFITsrc + '/../regression/{}.py'.format(test['name']), modifyOriginal=True
            )
        if gh_all:
            t_context = '{} {}@{}'.format(pyverheader, test['name'], servername)
            set_gh_status(state='pending', context=t_context, description=comp_info_start)
        else:
            t_context = None
        t0 = time.time()
        try:
            print('\n' * 3)
            print('=' * 80)
            print('START OF TEST: %s' % test['name'])
            print('=' * 80)
            print('\n' * 3)
            timeout = (
                test_plan.get('yaml_timeout_factor', 0) * test.get('runtime', 0)
                if test_plan.get('yaml_timeout_factor', 0)
                else script_timeout
            )
            signal.alarm(timeout)
            OMFIT['regression_scripts'][test['name']].run(**test.get('params', {}))
        except (KeyboardInterrupt, Exception) as excp:
            # Need to disable alarm both here and after else: instead of the finally block
            # in case getting stack and posting to github moves us over the timeout threshold.
            signal.alarm(0)
            etype, value, tb = sys.exc_info()
            excp_stack = ''.join(traceback.format_exception(etype, value, tb))
            print(excp_stack)  # print the full stack on failure
            allow_failure = test.get('allow_failure', None)
            print(f'allow_failure = {allow_failure}')
            stacks[test['name']] = excp_stack
            test_plan['results'][test['name']]['stack'] = excp_stack
            if allow_failure:
                allowed_errors[test['name']] = repr(excp)
                test_plan['results'][test['name']]['status'] = 'allowed failure'
            else:
                errors[test['name']] = repr(excp)
                test_plan['results'][test['name']]['status'] = 'failure'
                if test_plan['results'][test['name']]['priority'] >= priority_failfast_thresh:  # Priority before increment
                    test_plan['fail_fast'] = True
                    print('fail_fast has been activated because this test has a poor track record')
                test_plan['results'][test['name']]['priority'] += priority_fail_increment
                if test_plan['results'][test['name']]['priority'] > priority_cap:
                    test_plan['results'][test['name']]['priority'] = priority_cap
            if gh_all:
                t_desc = comp_info_start
                if isinstance(excp, KeyboardInterrupt):
                    t_desc = 'Timeout:' + t_desc
                set_gh_status(state=False, context=t_context, description=t_desc)
        else:
            # Disabling the alarm should happen before anything else as to not risk moving over the timeout threshold.
            signal.alarm(0)
            if False:
                mod_list = sorted(list(set([mod['ID'] for mod in list(OMFIT.moduleDict().values())])))
                test_content = OMFIT['regression_scripts'][test['name']].read()
                if 'modules:' in test_content:
                    OMFIT['regression_scripts'][test['name']].write(re.sub('modules:.*\n', 'modules: %r\n' % mod_list, test_content))
                else:
                    OMFIT['regression_scripts'][test['name']].write(
                        re.sub('labels:(.*)\n', 'labels:\1\nmodules: %r\n' % mod_list, test_content)
                    )
            success.append(test['name'])
            test_plan['results'][test['name']]['priority'] *= priority_success_multiplier
            test_plan['results'][test['name']]['status'] = 'success'
            if gh_all:
                set_gh_status(state=True, context=t_context, description=comp_info_start)
        finally:
            times[test['name']] = time.time() - t0

            # Slightly increase priority for fast tests so they go first; if all tests had an even failure potential,
            # this would reveal problems sooner.
            priority_speed_bonus = priority_speed_bonus_scale * min([1.0, priority_speed_bonus_timescale / times[test['name']]])
            test_plan['results'][test['name']]['priority'] += priority_speed_bonus

            tests_since_last_commit_check += 1
            test_plan['results'][test['name']]['time'] = times[test['name']]
            close('all')
            os.environ['OMFIT_DEBUG'] = "0"
            for k in list(OMFIT.keys()):
                if k not in old_keys:
                    del OMFIT[k]

    # update test plan with results
    class YAMLDumper(yaml.Dumper):
        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow, False)

    if test_plan_file:
        test_plan_yaml_update = yaml.dump(test_plan, Dumper=YAMLDumper, default_flow_style=False)
        print("Test Plan With Results:\n" + test_plan_yaml_update)
        with open(test_plan_file, 'w') as f:
            f.write(test_plan_yaml_update)

    # print test summary results
    print('\n' * 3)
    print('=' * 80)
    print('TESTS SUMMARY')
    print('=' * 80)
    print('\n' * 3)
    out_mess = ['Timing information:', '-' * 40]
    for i in np.argsort(list(times.values())):
        out_mess.append((test_plan['tests'][i]['name'], list(times.values())[i]))
    total_tests = len(test_plan['tests'])
    remaining_tests = total_tests - len(success) - len(errors) - len(allowed_errors)
    out_mess.append('-' * 40)
    out_mess.append('{}/{} Tests succeeded'.format(len(success), total_tests))
    out_mess.append('{}/{} Tests failed'.format(len(errors), total_tests))
    out_mess.append(f'{len(allowed_errors)}/{total_tests} Tests failed but were tolerated anyway.')
    out_mess.append('{}/{} Tests not run'.format(remaining_tests, total_tests))
    if len(errors):
        for test, error in errors.items():
            out_mess.append('== Error of %s ==' % test)
            out_mess.append(error)
    print('\n'.join(map(str, out_mess)))

    # Post final comment/status to GitHub
    if gh:
        if post_gh_comment:
            post_comment_to_github(comment='```\n%s\n```' % ('\n'.join(map(str, out_mess))))
        if post_gh_status:
            comp_info = '{s:}/{tot:} success on host {h:} at {t:} on branch {b:}'.format(
                s=len(success), tot=len(test_plan['tests']), h=hostname, t=time.ctime(), b=test_branch
            )

            gh_state = not len(errors)
            if gh_state and remaining_tests:
                comp_info = 'Aborted early due to new github commit. Host {h:} at {t:} on branch {b:}'.format(
                    h=hostname, t=time.ctime(), b=test_branch
                )
                gh_state = 'pending'

            set_gh_status(state=gh_state, context=context, description=comp_info)
            # TODO: Remove the next line after merging requires the new context.
            set_gh_status(state=gh_state, context=context_legacy, description=comp_info)
            if os.path.exists(c_fn):
                os.remove(c_fn)

    print('run_test_series() completed.')
    if exit_at_end:
        if len(errors):
            sys.exit(1)
        sys.exit(0)


############################################
if __name__ == '__main__':
    test_classes_main_header()

    # To run the unit tests, provide a number > 0 or the word test as a command line argument while calling
    if len(sys.argv) > 1:
        try:
            test_flag = int(sys.argv[1])
        except ValueError:
            test_flag = int(sys.argv[1] == 'test')
    else:
        test_flag = 0

    if test_flag > 0:
        sys.argv.pop(1)
        unittest.main(failfast=False)
    else:
        pass

elif __name__ == 'omfit_classes.omfit_python':
    with open(OMFITsrc + '/../regression/test_omfit_testing.py') as f_:
        exec(compile(f_.read(), OMFITsrc + '/../regression/test_omfit_testing.py', 'exec'))
