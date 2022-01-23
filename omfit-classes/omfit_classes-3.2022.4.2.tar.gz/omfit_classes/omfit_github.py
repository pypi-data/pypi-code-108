try:
    # framework is running
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


import requests
import datetime
from urllib.parse import quote_plus
import numpy as np

__all__ = [
    'get_gh_remote_org_repo_branch',
    'on_latest_gh_commit',
    'convert_gh_time_str_datetime',
    'get_OMFIT_GitHub_token',
    'set_OMFIT_GitHub_token',
    'OMFITgithub_paged_fetcher',
    'get_pull_request_number',
    'get_git_branch_info',
    'post_comment_to_github',
    'find_gh_comments',
    'delete_matching_gh_comments',
    'edit_github_comment',
    'set_gh_status',
]


def get_git_branch_info(
    remote=None,
    org=None,
    destination_org=None,
    repository=None,
    branch=None,
    url=None,
    omfit_fallback=True,
    no_pr_lookup=False,
    return_pr_destination_org=True,
    server=None,
):
    """
    Looks up local name for upstream remote repo, GitHub org, repository name, current branch, & open pull request info
    All parameters are optional and should only be provided if trying to override some results

    :param remote: string [optional]
        Local name for the upstream remote.
        If None, attempts to lookup with method based on git rev-parse.

    :param org: string [optional]
        The organization that the repo is under, like 'gafusion'.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to gafusion on failure.

    :param destination_org: string [optional]
        Used for cross-fork pull requests: specify the destination org of the pull request.
        The pull request actually exists on this org, but it is not where the source branch lives.
        If None it defaults to same as org

    :param repository: string [optional]
        The name of the repo on GitHub.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to OMFIT-source on failure.

    :param branch: string [optional]
        Local/remote name for the current branch
        NOTE: there is an assumption that the local and upstream branches have same name

    :param url: string [optional]
        Provided mainly for testing.
        Overrides the url that would be returned by `git config --get remote.origin.url`.

    :param omfit_fallback: bool
        Default org and repository are gafusion and OMFIT-source instead of None and None in case of failed lookup.

    :param no_pr_lookup: bool
        Improve speed by skipping lookup of pull request number

    :param return_pr_destination_org: bool
        If an open pull request is found, changes remote, org, repository,
        and branch to match the destination side of the pull request.
        If there is no pull request or this flag is False,
        remote/org/repo/branch will correspond to the source.

    :param server: string [optional]
        The server of the remote - usually github.com, but could also be something like vali.gat.com.

    :return: tuple containing 4 strings and a dict, with elements to be replaced with None for lookup failure
        remote (str), org (str), repository (str), branch (str), pull_request_info (dict)
    """

    def _parse_remote_url(url):
        """
        A utility function to parse a git remote url

        :return: protocol, server, org, repo
        """
        if not url.endswith('.git'):
            url = url + '.git'
        # https://stackoverflow.com/a/4667014/6605826
        remote_re = r'(git@(.+?):|https://(.+?)/)(.+?)/(.+?)\.git$'
        m = re.search(remote_re, url)
        if m:
            server = m.group(2) if m.group(2) else m.group(3)
            return m.group(1), server, m.group(4), m.group(5)
        raise ValueError('Unable to parse remote url %s' % url)

    pr_info = None  # Default unless overwritten by something real

    if remote is not None and branch is not None:
        revparse = '{}/{}'.format(remote, branch)
    else:
        revparse = repo('rev-parse --abbrev-ref @{u}')

    # Jenkins server defines the GIT_BRANCH environment variable
    if len(revparse.split('/')) < 2:
        revparse = os.environ.get('GIT_BRANCH', revparse)
        # If this is a pr branch, then we can directly look up the relevant info (if requested)
        if '/pr/' in revparse and not no_pr_lookup and branch is None:
            dest_repo, _, number, __ = revparse.split('/')
            assert _ == 'pr', 'Upstream pr pattern %s not parsed correctly' % revparse
            assert __ == 'head', 'Upstream pr pattern %s not parsed correctly' % revparse
            url = repo('config --get remote.{}.url'.format(dest_repo))
            protocol_, server_, org_, repository_ = _parse_remote_url(url)
            pr_info = OMFITgithub_paged_fetcher(org=org_, path='pulls/%s' % number, repository=repository_).fetch()[0]
            if not return_pr_destination_org:
                printw('pr branch detected, but return_pr_destination_org is False')
                branch = branch or pr_info.get('head', {}).get('ref', None)
                full_name = pr_info.get('head', {}).get('repo', {}).get('full_name', "").split('/')
                org = org or (full_name[0] if len(full_name) is 2 else None)
                repository = repository or (full_name[1] if len(full_name) is 2 else None)
            else:
                remote = remote or dest_repo
                org = org or org_
                repository = repository or repository_
                branch = branch or pr_info.get('base', {}).get('ref', None)
            return remote, org, repository, branch, pr_info

    # Handle case of local branch with no upstream: we can't do much here
    if len(revparse.split('/')) < 2:
        printw('Warning: failed to determine remote/org/repo/branch info from git rev-parse: {}'.format(revparse))
        print('You probably are on a local branch that does not have an upstream.')
        branch = branch or repo.active_branch()[0]
        if omfit_fallback:
            if org is not None and repository is not None:
                print('org and repository were specified, so they are fine')
            else:
                print('org and repository will default to gafusion and OMFIT-source if not overridden')
            org = org or 'gafusion'
            repository = repository or 'OMFIT-source'
        printw('Returning: ({}, {}, {}, {}, {})'.format(remote, org, repository, branch, pr_info))
        return remote, org, repository, branch, pr_info

    # Get primary remote and upstream branch information
    remote_ = revparse.split('/')[0]
    branch_ = revparse.split('/')[-1]
    remote = remote or remote_
    branch = branch or branch_
    url = url or repo('config --get remote.{}.url'.format(remote))

    protocol_, server_, org_, repository_ = _parse_remote_url(url)
    org = org or org_
    repository = repository or repository_
    server = server or server_

    if no_pr_lookup:
        printd('Returning remote, org, repository, and branch before pull request lookup; pr_info will be None')
        return remote, org, repository, branch, pr_info

    # Build a list of remotes to check, starting with the first one
    destination_org = destination_org or org
    remotes = [remote]
    urls = [url]
    destination_orgs = [destination_org]
    repositories = [repository]
    servers = [server]
    for new_remote in repo('remote').split('\n'):
        if new_remote not in remotes:
            url = repo('config --get remote.{}.url'.format(new_remote))
            protocol, server, org_, repository_ = _parse_remote_url(url)
            remotes.append(new_remote)
            urls.append(url)
            destination_orgs.append(org_)
            repositories.append(repository_)
            servers.append(server)
            printd('    Found new remote to check: {} with org = {}, repo = {}'.format(new_remote, org, repository))
    # Make sure gafusion/OMFIT-source is in the list
    if 'gafusion' not in destination_orgs:
        destination_orgs.insert(1, 'gafusion')
        remotes.insert(1, None)
        repositories.insert(1, 'OMFIT-source')
        branches.insert(1, 'unstable')
        servers.insert(1, 'github.com')
    # Prioritize gafusion and check it first or second, but not after a bunch of other forks
    if 'gafusion' not in destination_orgs[0:2]:
        g_idx = destination_orgs.index('gafusion')
        for thing in [destination_orgs, remotes, repositories, servers, urls]:
            thing.insert(1, thing.pop(g_idx))

    # Loop through list of possible remote orgs and search for an open pull request
    head = '{org:}:{branch}'.format(org=org, branch=branch)  # The source branch, not the destination
    i = j = 0
    info = [{'empty': None}]
    printd('Searching for open pull requests for {}/{}:{} with destination_org in {}'.format(org, repository, branch, destination_orgs))
    while i < len(destination_orgs) and info[0].get('number', None) is None:
        if servers[i] != 'github.com':
            i += 1
            continue
        a = OMFITgithub_paged_fetcher(org=destination_orgs[i], path='pulls', selection=dict(head=head), repository=repository)
        j = i
        info = a.fetch()
        if not len(info):
            info = [{}]
        if not isinstance(info[0], dict):
            info = [{}]
        printd(
            "    PR lookup attempt i = {i:}, destination_org = {do:}, info[0].get('number', None) = {num:}".format(
                i=i, do=destination_orgs[i], num=info[0].get('number', None)
            )
        )
        info[0].setdefault('org', destination_orgs[i])
        i += 1

    if info[0].get('number', None) is None:
        printd('This branch ({}:{}) does not seem to have an open pull request.'.format(org, branch))
    else:
        pr_info = info[0]
        if return_pr_destination_org:
            printd(
                'Open pull request {}#{} found! Reassigning remote, org, repository, and branch to correspond to '
                'the destination side of the pull request.'.format(destination_orgs[j], pr_info.get('number', None))
            )
            remote = remotes[j]
            org = destination_orgs[j]
            repository = repositories[j]
            branch = pr_info.get('base', {}).get('ref', None)
            printd('    remote = {remote:}, org = {org:}, repository = {repository:}, branch = {branch:}'.format(**locals()))

    return remote, org, repository, branch, pr_info


def on_latest_gh_commit():
    """
    Returns true if the current working commit is the same as the github latest commit for this branch.
    """
    remote, org, repository, branch, pr_info = get_git_branch_info(return_pr_destination_org=False)
    if org and repo and branch:
        headers = {'Authorization': 'token ' + get_OMFIT_GitHub_token()}
        url = "https://api.github.com/repos/{}/{}/commits?sha={}".format(org, repository, quote_plus(branch))
        print("URL : " + url)
        response = requests.get(url, headers=headers)
        local_hash = repo.get_hash('HEAD~0')
        if response.status_code == 200:
            commits = response.json()
            if commits and commits[0].get('sha', local_hash) != local_hash:
                return False

    else:
        print("Could not find corresponding GitHub branch. Assuming current commit is latest.")
    return True


def get_gh_remote_org_repo_branch(**kw):
    """
    Looks up local name for upstream remote repo, GitHub org, repository name, and current branch
    Like calling get_git_branch_info with `no_pr_lookup=True`

    :return: tuple containing 4 strings
        remote, org, repository, branch
    """
    kw['no_pr_lookup'] = True  # Make sure no one can override this; the function wouldn't make any sense otherwise.
    return get_git_branch_info(**kw)[0:4]


def _get_OMFIT_GitHub_credential():
    user = OMFIT['MainSettings']['SERVER'].get('GITHUB_username', '')
    if not len(user):
        raise ValueError('No GitHub username has been set!')
    return user + '@token.github.com:0'


def get_OMFIT_GitHub_token(token=None):
    """
    :param token: string or None
        Token for accessing GitHub
        None triggers attempt to decrypt from $GHUSER@token.github.com credential file
        Must be set up in advance with set_OMFIT_GitHub_token() function

    :return: GitHub token
    """
    if not token:
        _, token = decrypt_credential(_get_OMFIT_GitHub_credential())
    if len(token) == 40:
        return token
    if not len(token):
        raise ValueError(
            'See https://github.com/settings/tokens/new to create a token, ' 'then use set_OMFIT_GitHub_token() to encrypt and store it.'
        )
    raise ValueError('string `%s` is not a valid token' % token)


def set_OMFIT_GitHub_token(token):
    """
    :param token: 40 chars Token string to be encrypted in $GHUSER@token.github.com credential file
    """
    cred = _get_OMFIT_GitHub_credential()
    if not len(token):
        return reset_credential(credential=cred)
    if len(token) != 40:
        raise ValueError('string `%s` is not a valid token' % token)
    try:
        encrypt_credential(credential=cred, password='', otp=token)
        printi('GitHub token stored in:', cred)
    except Exception as e:
        printe('GitHub token save failed:', repr(e))


def convert_gh_time_str_datetime(t):
    """
    Convert a GitHub (gh) time string to a datetime object

    :param t: A time string like
    """
    if t is None:
        return None
    y, M, d = list(map(int, t.split('T')[0].split('-')))
    h, m, s = list(map(int, t.split('T')[1].strip('Z').split(':')))
    return datetime.datetime(y, M, d, h, m, s)


class OMFITgithub_paged_fetcher(list):
    """
    Interact with GitHub via the GitHub api: https://developer.github.com/v3/
    to fetch data from a path
    https://api.github.com/repos/{org}/{repo}/{path}
    that has paged results
    """

    def __init__(self, org=None, repository=None, path='comments', token=None, selection=None):
        """
        https://api.github.com/repos/{org}/{repo}/{path}

        :param org: string [optional] The organization that the repo is under, like 'gafusion'.
            If None, attempts to lookup with method based on git rev-parse.
            Falls back to gafusion on failure.

        :param repository: string [optional]
            The name of the repo on GitHub.
            If None, attempts to lookup with method based on git rev-parse.
            Falls back to OMFIT-source on failure.

        :param path: string
            The part of the repo api to access

        :param token: string or None
            Token for accessing GitHub
            None triggers attempt to decrypt from file (must be set up in advance).
            Passed to get_OMFIT_GitHub_token.

        :param selection: dict
            A dictionary such as {'state':'all'}
        """
        self.token = get_OMFIT_GitHub_token(token)
        self.path = path
        # Avoid infinite recursion
        if org is None or repository is None:
            remote, org, repository, branch = get_gh_remote_org_repo_branch(org=org, repository=repository)
        self.url = 'https://api.github.com/repos/{org}/{repository}/{path}'.format(**locals())
        if selection is None:
            self.selection = {}
        else:
            self.selection = selection
        self.current_page = 1
        self.find_last_page()

    def find_last_page(self):
        """
        Find the last page number and sets self.last_page

        :returns: self.last_page
        """
        req = requests.get(self.url + self.get_sel_str(page=1), headers={'Authorization': 'token %s' % self.token})
        if hasattr(req, 'links') and 'last' in req.links and 'url' in req.links['last']:
            last = self.last_page_url = req.links['last']['url']
            for s in last.split('?')[1].split('&'):
                if 'page' in s:
                    self.last_page = int(s.split('=')[1].strip())
                    break
        else:
            self.last_page = 1
            printd('Unable to find last page of GitHub paged results')
        return self.last_page

    def fetch(self):
        """
        Fetch the paged results from GitHub and store them in self

        :returns: self
        """
        if (self.current_page == self.last_page) and (self.last_page > 1):
            printd('Already fetched last page; not fetching again')
            return
        start = self.current_page
        for i in range(self.current_page, self.last_page + 1):
            ascii_progress_bar(i, start, self.last_page, mess='Getting GitHub %s pages' % self.path, newline=False)
            try:
                req = requests.get(self.url + self.get_sel_str(page=i), headers={'Authorization': 'token %s' % self.token})
            except KeyboardInterrupt:
                break
            json = req.json()
            # Some paths (such as requesting only a single pull request) only return a single dictionary
            if isinstance(json, dict):
                json = [json]
            self.extend(json)
            self.current_page = i
        return self

    def get_sel_str(self, **kw):
        r"""
        Figure out how to get the selection part of the url, such as ?state=all&page=1, etc.

        :param \**kw: Any variables (such as page) to override self.selection set at initialization

        :return: An ampersand '&' separated string of key=value (and the question mark)
        """

        sel = copy.deepcopy(self.selection)
        sel.update(kw)
        if len(sel):
            return '?' + '&'.join(['%s=%s' % (x[0], x[1]) for x in list(sel.items())])
        else:
            return ''

    @property
    def results(self):
        return self


def get_pull_request_number(return_info=False, **kw):
    """
    Gets the pull request number associated for the current git branch if there is an open pull request.

    Passes parameters org, destination_org, branch, and repository to get_git_branch_info().

    :param return_info: bool [optional]
        Return a dictionary of information instead of just the pull request number

    :return: int, dict-like, or None
        Pull request number if one can be found, otherwise None.
        If return_info: dictionary returned by OMFITgithub_paged_fetcher with 'org' key added. Contains 'number', too.
    """
    kw['no_pr_lookup'] = False  # Make sure no one can override this; the function wouldn't make any sense otherwise.
    pr_info = get_git_branch_info(**kw)[4]
    if return_info or pr_info is None:
        return pr_info
    else:
        return pr_info.get('number', None)


def find_gh_comments(thread=None, contains='automatic_regression_test_post', user=False, id_only=True, org=None, repository=None, **kw):
    r"""
    Looks up comments on a GitHub issue or pull request and searches for ones with body text matching `contains`

    :param thread: int or None
        int: issue or pull request number
        None: look up pull request number based on active branch name. Only works if a pull request is open.

    :param contains: string or list of strings
        Check for these strings within comment body text. They all must be present.

    :param user: bool or string [optional]
        True: only consider comments made with the current username (looks up GITHUB_username from MainSettings)
        string: only comments made by the specified username.

    :param id_only: bool
        Return only the comment ID numbers instead of full dictionary of comment info

    :param org: string [optional] The organization that the repo is under, like 'gafusion'.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to gafusion on failure.

    :param repository: string [optional]
        The name of the repo on GitHub. If None, attempts to lookup with
        method based on git rev-parse. Falls back to OMFIT-source on failure.

    :param \**kw: keywords to pass to OMFITgithub_paged_fetcher

    :return: list of dicts (id_only=False) or list of ints (id_only=True)
    """
    assert contains is not None, 'Must specify text to match.'
    _, org, repository, _ = get_gh_remote_org_repo_branch(org=org, repository=repository)
    if thread is None:
        thread = get_pull_request_number(org=org, repository=repository)
        if thread is None:
            print(
                'Automatic lookup of pull request # failed. Must provide a pull request or issue number to post '
                'comments to GitHub. Nothing will be posted. Goodbye.'
            )
    info = OMFITgithub_paged_fetcher(org=org, path='issues/{}/comments'.format(thread), repository=repository, **kw).fetch()
    matching_comments = [cmt for cmt in info if np.all([c in cmt.get('body', '') for c in tolist(contains)])]
    if user is True:
        user = OMFIT['MainSettings']['SERVER'].get('GITHUB_username', False)
    if user:
        matching_comments = [cmt for cmt in matching_comments if cmt.get('user', {}).get('login', None) == user]
        userm = user
    else:
        userm = '(any user)'
    ids = [comment.get('id', None) for comment in matching_comments]
    printd(
        'Found {} comments in {}/{}#{} containing {} and user matching {} with IDs: {}'.format(
            len(matching_comments), org, repository, thread, ' and '.join(tolist([repr(c) for c in contains])), userm, ids
        ),
        topic='omfit_github',
    )
    if id_only:
        return ids
    return matching_comments


def delete_matching_gh_comments(
    thread=None,
    keyword=None,
    test=True,
    token=None,
    org=None,
    repository=None,
    quiet=False,
    exclude=None,
    exclude_contain=None,
    match_username=None,
    **kw,
):
    r"""
    Deletes GitHub comments that contain a keyword. Use CAREFULLY for clearing obsolete automatic test report posts.

    :param thread: int [optional]
        Supply issue or comment number or leave as None to look up an open pull request # for the active branch

    :param keyword: string or list of strings
        CAREFUL! All comments which match this string will be deleted.
        If a list is provided, every substring in the list must be present in a comment.

    :param test: bool
        Report which comments would be deleted without actually deleting them.

    :param token: string or None
        Token for accessing GitHub
        None triggers attempt to decrypt from $GHUSER@token.github.com credential file
        Must be set up in advance with set_OMFIT_GitHub_token() function

    :param org: string [optional] The organization that the repo is under, like 'gafusion'.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to gafusion on failure.

    :param repository: string [optional]
        The name of the repo on GitHub.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to OMFIT-source on failure.

    :param quiet: bool
        Suppress print output

    :param exclude: list of strings [optional]
        List of CIDs to exclude / protect from deletion. In addition to actual CIDs, the special value of 'latest' is
        accepted and will trigger lookup of the matching comment with the most recent timestamp. Its CID will replace
        'latest' in the list.

    :param exclude_contain: list of strings [optional]
        If provided, comments must contain all of the strings listed in their body in order to qualify for exclusion.

    :param match_username: bool or string [optional]
        True: Only delete comments that match the current username.
        string: Only delete comments that match the specified username.

    :param \**kw: keywords to pass to find_gh_comments()

    :return: list of responses from requests (test=False) or list of dicts with comment info (test=True)
        response instances should have a `status_code` attribute, which is normally int(201) for successful
        GitHub posts and probably 4xx for failures.
    """

    printd(
        'delete_matching_gh_comments: thread = {thread:}, keyword = {keyword:}, test = {test:}, org = {org:}, '
        'repository = {repository:}, exclude = {exclude:}, exclude_contain = {exclude_contain:}, '
        'match_username = {match_username:}'.format(**locals()),
        topic='delete_comments',
    )

    def printq(*args):
        if not quiet:
            print(*args)
        return

    gafusion_fallback_allowed = org is None  # Don't allow fallback to gafusion if the original org is explicit

    # Setup github interfacing information
    token = get_OMFIT_GitHub_token(token=token)
    hed = {'Authorization': 'token ' + token}
    responses = []
    remote, org, repository, branch = get_gh_remote_org_repo_branch(org=org, repository=repository)

    thread = thread or get_pull_request_number(org=org, repository=repository)

    # Lookup comments
    info = find_gh_comments(
        thread=thread, contains=keyword, id_only=False, token=token, org=org, repository=repository, user=match_username, **kw
    )
    cids = [c['id'] for c in info]

    if (len(cids) == 0) and (org != 'gafusion') and gafusion_fallback_allowed:
        # This may be a cross-fork pull request where "org" is not gafusion but the pull request is on gafusion.
        # See if we can find the comments if we change the org to gafusion and search there.
        gafusion_info = find_gh_comments(
            thread=thread, contains=keyword, id_only=False, token=token, org='gafusion', repository=repository, user=match_username, **kw
        )
        gafusion_cids = [c['id'] for c in gafusion_info]
        if len(gafusion_cids) > 0:
            info = gafusion_info
            cids = gafusion_cids
            printd('Found {} comments by changing org to gafusion'.format(len(cids)), topic='delete_comments')
            org = 'gafusion'
        else:
            printd('Changing org to gafusion did not help find comments', topic='delete_comments')
    elif len(cids) == 0:
        printd(
            "Nothing found in search for comments to delete; fallback method would've been nice, but wasn't attempted",
            topic='delete_comments',
        )
        if org == 'gafusion':
            printd('Fallback to searching for comments on gafusion not attempted because org was already gafusion', topic='delete_comments')
        if not gafusion_fallback_allowed:
            printd(
                'Fallback to searching for comments on gafusion not allowed because '
                'org was explicit in call to delete_matching_gh_comments()',
                topic='delete_comments',
            )
    else:
        printd('Found some comments on the first attempt with org={}; skipping fallback search plan'.format(org), topic='delete_comments')

    # Handle exclusions
    exclude = tolist(exclude)
    if 'latest' in exclude and len(info):
        printq('Excluding latest matching comment...')
        dates = [datetime.datetime.strptime(c['created_at'], "%Y-%m-%dT%H:%M:%SZ") for c in info]
        exclude_ = cids[np.array(dates).argmax()]
        printq('  CID of latest comment is {}'.format(exclude_))
        for i in range(len(exclude)):
            if exclude[i] == 'latest':
                exclude[i] = exclude_
        if exclude_ not in exclude:
            printw('Warning: had to use fallback to  put {} in exclude list'.format(exclude_))
            exclude += [exclude_]
    else:
        printd('No exclusion for latest comment', topic='delete_comments')
    if exclude_contain is not None:
        for i in range(len(exclude)):
            for k in range(len(info)):
                if info[k]['id'] == exclude[i]:
                    for ec in tolist(exclude_contain):
                        if ec not in info[k]['body']:
                            printq(
                                'Revoking protection for {} (it is no longer excluded from deletion) because '
                                'it does not contain all of the substrings: {}'.format(exclude[i], exclude_contain)
                            )
                            exclude[i] = None
    else:
        printd('No special requirements for excluded comments', topic='delete_comments')

    info = [info_ for info_ in info if info_['id'] not in exclude]
    cids = [c['id'] for c in info]

    # Test mode: return info without trying to delete anything
    if test:
        printq(
            'Bad authorization; nothing would be deleted because of bad token.'
            if token is None
            else 'Authorization may be okay. You could actually delete these comments:'
        )
        printq('{} comments would be deleted in #{}.'.format(len(cids), thread))
        printq('No comments have actually been deleted because test=True')
        return info
    for cid in cids:
        url = 'https://api.github.com/repos/{org:}/{repo:}/issues/comments/{cid:}'.format(org=org, repo=repository, cid=cid)
        responses += [requests.delete(url, headers=hed)]
        printd('responses to deletion requests: {}'.format(responses), topic='delete_comments')
    printq('Ordered deletion of {} comments in {}/{}#{}'.format(len(responses), org, repository, thread))
    return responses


def _define_new_content(old_content, new_content, mode='replace_between', separator='---', close_separator=None):
    """
    Defines new content of a comment after editing.

    Used for assigning output of the edit_github_comment function and also predicting results.

    :param old_content: str
        Content of the comment's body before editing

    :param new_content: str
        New content to add (maybe as a replacement of some old content)

    :param mode: str
        Edit mode: 'replace', 'append', 'replace_between' separators

    :param separator: str
        Separator between old_content and new content

    :param close_separator: str [optional]
         A different separator at the end of the block of new content

    :return: str, None, or ValueError
        str: try to do the edit, using this string as the new comment body
        None: abort
        ValueError: This error should be raised. It's returned instead of raised here to help predict output in tests.
    """
    if new_content is None:
        if mode == 'replace_between':
            if separator in old_content:
                before = old_content.split(separator)[0]
                after = separator.join(old_content.split(separator)[1:])
                if close_separator is not None:
                    if close_separator in old_content:
                        after = close_separator.join(after.split(close_separator)[1:])
                    else:
                        after = ''
                elif separator in after:
                    after = separator.join(after.split(separator)[1:])
                else:
                    after = ''
                content = before + after
            else:
                print('No separators found in output. Aborting deletion of material between separators ' '({}).'.format(separator))
                return None
        else:
            return ValueError("Can't accept None as content except in mode 'replace_between'")
        # new_content == '' is acceptable for modes replace and append, but has special behavior for replace_between
    elif mode == 'replace':
        content = new_content
    elif mode == 'append' and separator is None:
        content = old_content + '\n' + new_content
    elif mode == 'append':
        content = old_content + separator + new_content
        if close_separator is not None:
            content += close_separator
    elif mode == 'replace_between' and separator is None:
        return ValueError('Using mode: replace between separators requires specifying a separator.')
    elif mode == 'replace_between':
        if separator in old_content:
            if close_separator is None:
                content = old_content.split(separator)
                content[1] = new_content
                content = separator.join(content)
            else:
                before = old_content.split(separator)[0]
                after = separator.join(old_content.split(separator)[1:])
                after = close_separator.join(after.split(close_separator)[1:])
                content = before + separator + new_content + close_separator + after
        else:
            content = old_content + separator + new_content
            if close_separator is not None:
                content += close_separator
    else:
        return ValueError('Unrecognized mode: {}'.format(mode))
    return content


def edit_github_comment(
    comment_mark=None, separator='---', new_content=None, mode='replace_between', thread=None, org=None, repository=None, token=None
):
    """
    Edits GitHub comments to update automatically generated information, such as regression test reports.

    :param comment_mark: str or None
        None: edit top comment.
        str: Search for a comment (not including top comment) containing comment_mark as a substring.

    :param new_content: str
        New content to put into the comment

        Special cases:
        If content is None and mode == 'replace_between':
            Separate close separator and close separator present in target: del between 1st open sep and next close sep
            Separate close separator & close separator not present in target: del everything after 1st open sep
            All same separator & one instance present in target: delete it and everything after
            All same separator & multiple instances present: delete the first two and everything in between.
        If content is None and mode != 'replace_between', raise ValueError
        If None and mode == 'replace_between', but separator not in comment, abort but do not raise.

    :param separator: str or list of strings
        Substring that separates parts that should be edited from parts that should not be edited.
        `'---'` will put a horizontal rule in GitHub comments, which seems like a good idea for this application.
        If this is a list, the first and second elements will be used as the opening and closing separators to allow for
        different open/close around a section.

    :param mode: str
        Replacement behavior.
        'replace': Replace entire comment. Ignores separator.
        'append': Append new content to old comment. Places separator between old and new if separator is supplied.
           Closes with another separator if separate open/close separators are supplied; otherwise just places one
           separator between the original content and the addition.
        'replace_between: Replace between first & second appearances of separator (or between open & close separators).
           Raises ValueError if separator is not specified.
           Acts like mode == 'append' if separator (or opening separator) is not already present in target comment.
        other: raises ValueError

    :param thread: int [optional]
        Issue or pull request number. Looked up automatically if not provided

    :param org: str [optional]
        GitHub org. Determined automatically if not supplied.

    :param repository: str [optional]
        GitHub repository. Determined automatically if not supplied.

    :param token: str
        Token for accessing GitHub. Decrypted automatically if not supplied.

    :return: response instance or None
        None if aborted before attempting to post, otherwise response instance, which is an object generated
        by the requests module. It should have a `status_code` attribute which is 2** on success
        and often 4** for failures.
    """
    if separator is not None:
        seps = tolist(separator)
        separator = seps[0]
        if len(seps) > 1:
            close_separator = seps[1]
        else:
            close_separator = None
    else:
        close_separator = None

    if separator is not None and '\n' not in separator:
        printw('edit_github_comment: Your life would be better if you included a line break in your separator.')

    # Figure out remote, org, etc. so ensure it's consistent throughout all function calls
    token = get_OMFIT_GitHub_token(token=token)
    remote, org_, repository_, branch, pr_info = get_git_branch_info(
        destination_org=org, repository=repository, no_pr_lookup=False, return_pr_destination_org=True
    )
    org = org or org_
    repository = repository or repository_
    thread = thread or (pr_info.get('number', None) if pr_info is not None else None)
    if thread is None:
        print(
            'Automatic lookup of pull request # failed. Must provide a pull request or issue number to post '
            'comments to GitHub. Nothing will be posted. Goodbye.'
        )
        return None

    # Get old content and cid if needed
    if comment_mark is not None:
        matching = find_gh_comments(contains=comment_mark, org=org, repository=repository, thread=thread, token=token, id_only=False)
        cid = matching[0]['id']
        old_content = matching[0]['body']
    elif mode in ['append', 'replace_between']:
        # The top "comment" isn't really a comment by GitHub's naming convention, apparently.
        old_content = OMFITgithub_paged_fetcher(org=org, repository=repository, path='issues/{}'.format(thread), token=token).fetch()[0][
            'body'
        ]
        cid = None
    else:
        old_content = ''  # Mode 'replace' just replaces, so no one cares what this is and we can save time fetching it.
        cid = None

    # Deal with different line break conventions; \r\n moves to the start of the line and then breaks, \n just breaks.
    # On Unix, \n should be used. \r\n is used by Windows and apparently web stuff like GitHub. It's only important
    # here because it breaks the str comparison. GitHub will convert \n into whatever it needs.
    if old_content is None:
        old_content = ''
    old_content = old_content.replace('\r\n', '\n')

    # Define content to post
    content = _define_new_content(old_content, new_content, mode=mode, separator=separator, close_separator=close_separator)
    if content is None:
        return None
    elif isinstance(content, ValueError):
        raise content

    # Edit the comment on GitHub!
    hed = {'Authorization': 'token ' + token}
    data = {'body': content}
    if comment_mark is None:
        # The issue itself (not a real comment)
        url = 'https://api.github.com/repos/{org:}/{repo:}/issues/{thread:}'.format(org=org, thread=thread, repo=repository)
    else:
        # A comment on the issue
        url = 'https://api.github.com/repos/{org:}/{repo:}/issues/comments/{cid:}'.format(org=org, repo=repository, cid=cid)
    response = requests.patch(url, json=data, headers=hed)

    return response


def post_comment_to_github(thread=None, comment=None, org=None, fork=None, repository=None, token=None):
    """
    Posts a comment to a thread (issue or pull request) on GitHub.
    Requires setup of a GitHub token to work.

    This function may be tested on fork='gafusion', thread=3208 if needed.

    Setup::

        1. Create a GitHub token with the "repo" (Full control of private repositories) box checked.
           See https://github.com/settings/tokens .

        2. [Optional] Safely store the token to disk by executing:
              set_OMFIT_GitHub_token(token)
           This step allows you to skip passing the token to the function every time.

    :param thread: int [optional]
        The number of the issue or pull request within the fork of interest
        If not supplied, the current branch name will be used to search for open pull requests on GitHub.

    :param comment: string
        The comment to be posted

    :param org: string [optional]
        Leave this as gafusion to post to the main OMFIT repo.
        Enter something else to post on a fork.

    :param fork: string [optional]
        Redundant with org. Use org instead. Fork is provided for backwards compatibility

    :param repository: string [optional]
        The name of the repo on GitHub.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to OMFIT-source on failure.
        You should probably leave this as None unless you're doing some testing,
        in which case you may use the regression_notifications repository under gafusion.

    :param token: string or None
        Token for accessing GitHub
        None triggers attempt to decrypt from $GHUSER@token.github.com credential file
        Must be set up in advance with set_OMFIT_GitHub_token() function

    :return: response instance
        As generated by requests.
        It should have a `status_code` attribute, which is normally int(201) for successful
        GitHub posts and probably 4xx for failures.
    """
    import requests

    if org is None:
        org = fork

    if comment is None:
        print('Provide a comment if you want to post a comment.')
        return

    remote, org_, repository_, branch, pr_info = get_git_branch_info(
        destination_org=org, repository=repository, no_pr_lookup=False, return_pr_destination_org=True
    )
    org = org or org_
    repository = repository or repository_
    thread = thread or (pr_info.get('number', None) if pr_info is not None else None)
    if thread is None:
        print(
            'Automatic lookup of pull request # failed. Must provide a pull request or issue number to post '
            'comments to GitHub. Nothing will be posted. Goodbye.'
        )
        return

    token = get_OMFIT_GitHub_token(token=token)
    hed = {'Authorization': 'token ' + token}
    data = {'body': comment}

    url = 'https://api.github.com/repos/{org:}/{repo:}/issues/{thread:}/comments'.format(org=org, thread=thread, repo=repository)
    response = requests.post(url, json=data, headers=hed)
    return response


def set_gh_status(
    org=None, repository=None, commit=None, state=None, context='regression/auto', description='', target_url=None, destination_org=None
):
    """
    Updates the status of a pull request on GitHub. Appears as green check mark or red X at the end of the thread.

    :param org: string [optional] The organization that the repo is under, like 'gafusion'.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to gafusion on failure.

    :param destination_org: string [optional]
        Used for cross-fork pull requests: specify the destination org of the pull request.
        The pull request actually exists on this org, but it is not where the source branch lives.
        Passed to get_pull_request_number when determining whether a pull request is open.
        Defines first org to check.
        If None it defaults to same as org

    :param repository: string [optional]
        The name of the repo on GitHub.
        If None, attempts to lookup with method based on git rev-parse.
        Falls back to OMFIT-source on failure.

    :param commit: commit hash or keyword
        'latest' or 'HEAD~0':
                Look up latest commit. This is appropriate if you have reloaded modules and classes as needed.
        'omfit' or None:
                use commit that was active when OMFIT launched.
                Appropriate if testing classes as loaded during launch and not reloaded since.
        else: treats input as a commit hash and will fail if it is not one.

    :param state: string or bool
        'success' or True: success -> green check
        'failure' or False: problem -> red X
        'pending' -> yellow circle

    :param context: string
        Match the context later to update the status

    :param description: string
        A string with a description of the status. Up to 140 characters. Long strings will be truncated.
        Line breaks, quotes, parentheses, etc. are allowed.

    :param target_url: string
       URL to associate with the status

    :return: response instance s generated by `requests`.
        It should have a `status_code` attribute, which is normally int(201) for successful GitHub posts and probably 4xx for failures.
    """
    if commit in ['latest', 'HEAD~0']:
        printd('Using latest commit (assuming modules and classes have been reloaded as needed)')
        sha = repo.get_hash('HEAD~0')
    elif commit in ['omfit', None]:
        printd('Using active commit at time of OMFIT launch')
        try:
            sha = repo.get_hash(repo_active_branch_commit)
        except NameError:
            repo_active_branch, repo_active_branch_commit, repo_str = repo.active_branch()
            sha = repo.get_hash(repo_active_branch_commit)
    else:
        sha = commit
    remote, org, repository, branch, pr_info = get_git_branch_info(org=org, repository=repository, destination_org=destination_org)
    url = 'https://api.github.com/repos/{org}/{repository}/statuses/{sha}'
    url = url.format(org=org, repository=repository, sha=sha)
    h = {'Authorization': 'token ' + get_OMFIT_GitHub_token()}
    final_state = 'success' if state is True else ('failure' if state is False else state)
    printd('set_gh_status(): state = {}, context = {}, description = {}, sha = {}'.format(final_state, context, description, sha))
    if target_url is None:
        target_url = os.environ.get('BUILD_URL', None)
    data = {
        'state': final_state,
        'context': context,
        'description': description[:140],  # GitHub status has a 140 char length limit
        'target_url': target_url,
    }
    response = requests.post(url, json=data, headers=h)
    return response


############################################
if '__main__' == __name__:
    test_classes_main_header()

    if False:  # remove test since token is encrypted with ssh key which has passphrase#os.environ.get('USER','') in ['eldond','smithsp']:
        comments = OMFITgithub_paged_fetcher()
        assert comments.last_page > 1
        assert convert_gh_time_str_datetime('2018-12-05T15:40:30Z') == datetime.datetime(2018, 12, 5, 15, 40, 30)
        post_comment_to_github(thread=3, comment='Command line import test comment', fork='smithsp')
    else:
        print('No tests of omfit_github, because no guaranteed token')
