import datetime
import os
import re
import shutil
import subprocess

import click
import git
from sentry_sdk import push_scope

from spell.cli.constants import BLACKLISTED_FILES, WHITELISTED_FILEEXTS
from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
    SPELL_INVALID_COMMIT,
    SPELL_BAD_REPO_STATE,
)
from spell.cli.log import logger
from spell.cli.utils import (
    cli_ssh_key_path,
    cli_ssh_config_path,
    ellipses,
    write_ssh_config_file,
    with_emoji,
)
from spell.cli.utils.sentry import capture_exception
from spell.api.models import Repository


# detect_repo determines a repository to use. In order of preference, a github_url,
# a local repository (uploading contents to gitlab), and finally no repository
def detect_repo(
    ctx,
    github_url,
    github_ref,
    force,
    description,
    commit_ref,
    allow_missing=True,
    resource_type="run",
):
    if github_url is not None:
        return Repository(github_url=github_url, commit_hash=github_ref if github_ref else "HEAD")
    git_repo = None
    try:
        git_repo = git.Repo(os.getcwd(), search_parent_directories=True)
    except git.exc.InvalidGitRepositoryError:
        pass
    if git_repo is None:
        if not allow_missing:
            raise ExitException(
                "A git repository needs to be specified to run this command.",
                SPELL_BAD_REPO_STATE,
            )
        if force:
            logger.warning("No git repository found! Running without a workspace.")
        else:
            click.confirm(
                "Could not find a git repository, so no user files will be available. " "Continue anyway?",
                default=True,
                abort=True,
            )
        return Repository()
    else:
        # Get relative path from git-root to CWD.
        local_root = git_repo.working_dir
        relative_path = os.path.relpath(os.getcwd(), local_root)
        root_directory = os.path.basename(local_root)

        try:
            next(git_repo.iter_commits(max_parents=0))
        except ValueError:
            raise ExitException(
                "The repository " + git_repo.working_dir + " has no commits! Please commit all files "
                "necessary to use this project before continuing.",
                SPELL_BAD_REPO_STATE,
            )

        if len(git_repo.submodules) > 0:
            logger.warning(
                "Spell does not currently support Git submodules. "
                "Files within submodules will not be available within the {}.".format(resource_type)
            )

        workspace_id, commit_hash, commit_message, uncommitted_hash = push_workspace(
            ctx,
            git_repo,
            commit_ref,
            force=force,
            include_uncommitted=ctx.obj["include_uncommitted"],
            resource_type=resource_type,
        )
        workspace_remote_url = get_remote_url(git_repo)
        if description is None:
            description = commit_message
        return Repository(
            local_root=local_root,
            workspace_id=workspace_id,
            workspace_remote_url=workspace_remote_url,
            commit_hash=commit_hash,
            uncommitted_hash=uncommitted_hash,
            relative_path=relative_path,
            root_directory=root_directory,
            description=description,
        )


def sync_repos(ctx, repo_specs, force, include_uncommitted=False, resource_type="run"):
    """Given an array of shape: ["path-to-repo:commit-ref", ...], will sync each repo to spell"""
    invalid_repos = []
    workspace_info = {}
    for repo_spec in repo_specs:
        repo_path = repo_spec["path"]
        commit_ref = repo_spec["commit_ref"]
        # get the git repo
        try:
            git_repo = git.Repo(repo_path)
        except Exception:
            click.echo(click.wrap_text("Could not find a repo at {}".format(repo_path)), err=True)
            invalid_repos.append(repo_path)
            continue
        # actually sync the workspace
        click.echo(with_emoji("✨", "Syncing repo {}.".format(repo_path), ctx.obj["utf8"]))
        try:
            workspace_id, commit_hash, _, _ = push_workspace(
                ctx,
                git_repo,
                commit_ref,
                force=force,
                include_uncommitted=include_uncommitted,
                resource_type=resource_type,
            )
        except ExitException as ex:
            invalid_repos.append(repo_path)
            click.echo(click.wrap_text(str(ex)), err=True)
            continue
        # add workspace to output
        if repo_spec["name"] in workspace_info:
            invalid_repos.append(repo_path)
            click.echo(
                click.wrap_text("Each repo name must be unique, {} is repeated".format(repo_spec["name"])),
                err=True,
            )
            continue
        workspace_info[repo_spec["name"]] = {
            "workspace_id": workspace_id,
            "commit_hash": commit_hash,
        }

    if len(invalid_repos) > 0:
        click.echo(click.wrap_text("The following repos could not be synced to spell:"), err=True)
        for r in invalid_repos:
            click.echo(click.wrap_text(" - " + r), err=True)
        raise ExitException("Invalid Git Repo(s)", SPELL_BAD_REPO_STATE)

    return workspace_info


# Remove hardlinked files
def clean_hardlinked_repo(ctx, repo):
    git_dst = os.path.join(
        ctx.obj["config_handler"].spell_dir,
        "repos",
        repo.git_dir[1:],
    )
    if os.path.isdir(git_dst):
        shutil.rmtree(git_dst)


# Creates hardlinks between .git dir of given repo and a location in
# the .spell config dir
def hardlink_repo(ctx, repo):
    # NOTE(peter): Trailing slash is required to properly copy directory contents
    git_src = repo.git_dir + "/"
    # Destination is the absolute path to the git dir moved into the local dir
    #  e.g. /Users/me/myrepo/.git ->
    #         /Users/me/.spell/repos/Users/me/myrepo/.git
    git_dst = os.path.join(
        ctx.obj["config_handler"].spell_dir,
        "repos",
        repo.git_dir[1:],
    )

    # Run the rsync to create hardlinks
    if not os.path.isdir(git_dst):
        os.makedirs(git_dst)
    rsync_cmd = [
        "rsync",
        "--archive",
        "--delete",
        # Exclude commit hooks
        "--exclude",
        "hooks",
        "--link-dest",
        git_src,
        git_src,
        git_dst,
    ]
    logger.info("rsyncing .git files")
    before = datetime.datetime.now()
    subprocess.check_call(rsync_cmd)
    after = datetime.datetime.now()
    # TODO(peter): Send warnings to Sentry if this takes a long time after we release to users
    logger.info("rsync took: {}".format(after - before))

    # Return the parallel .git dir
    return git_dst


def commit_to_parallel(repo, parallel_git):
    # Make the commit
    commit_cmd = [
        "git",
        "--git-dir",
        parallel_git,
        "--work-tree",
        repo.working_dir,
        "commit",
        "--all",
        "--message",
        "Uncommitted changes",
    ]
    with open(os.devnull, "w") as devnull:
        logger.info("committing to parallel repo")
        subprocess.check_call(commit_cmd, stdout=devnull)

    # Get the new commit hash
    rev_parse_cmd = [
        "git",
        "--git-dir",
        parallel_git,
        "--work-tree",
        repo.working_dir,
        "rev-parse",
        "HEAD",
    ]
    logger.info("retrieving parallel repo hash")
    commit_hash = subprocess.check_output(rev_parse_cmd).decode("utf-8").strip()
    return commit_hash


def push_workspace(ctx, git_repo, commit_ref, force=False, include_uncommitted=False, resource_type="run"):
    """Syncs a single repo to spell"""
    git_path = git_repo.working_dir
    git_dir = git_repo.git_dir

    # get the root commit
    try:
        root_commit = next(git_repo.iter_commits(max_parents=0))
    except ValueError:
        raise ExitException(
            "The repository " + git_repo.working_dir + " has no commits! Please commit all files "
            "necessary to use this project before continuing.",
            SPELL_BAD_REPO_STATE,
        )
    # resolve commit_ref to its sha hash
    try:
        commit = git_repo.commit(commit_ref)
        commit_hash = commit.hexsha
    except git.BadName:
        raise ExitException(
            'Could not resolve commit "{}" for repo {}'.format(commit_ref, git_repo.working_dir),
            SPELL_INVALID_COMMIT,
        )

    workspace_name = os.path.basename(git_path)

    # hit the API for new workspace info
    client = ctx.obj["client"]
    with api_client_exception_handler():
        logger.info("Retrieving new workspace information from Spell")
        workspace = client.new_workspace(str(root_commit), workspace_name, "")

    workspace_id = workspace.id
    git_remote_url = workspace.git_remote_url

    # fail if staged/unstaged changes, and warn if files are untracked
    if (has_staged(git_repo) or has_unstaged(git_repo)) and not include_uncommitted:
        if not force:
            raise ExitException(
                "Uncommitted changes to tracked files detected in repo {}"
                " -- please commit first".format(git_repo.working_dir),
                SPELL_BAD_REPO_STATE,
            )
        logger.warning("Repo contains uncommitted changes that will not be included in the run.")
    if has_untracked(git_repo):
        if not force:
            click.confirm(
                "There are some untracked files in repo {}. They won't be available on this {}."
                "\n{}\nContinue the {} anyway?".format(
                    git_repo.working_dir, resource_type, get_untracked(git_repo), resource_type
                ),
                default=True,
                abort=True,
            )
        else:
            logger.warning("Repo contains untracked files that will not be included in the {}.".format(resource_type))

    # use specific SSH key if one is in the spell directory
    gitenv = os.environ.copy()
    ssh_key_path = cli_ssh_key_path(ctx.obj["config_handler"])
    ssh_config_path = cli_ssh_config_path(ctx.obj["config_handler"])
    # TODO(Brian): eventually remove ssh config file creation here once enough people have done runs
    # with this code and/or we think it's been sufficiently long that most people have
    # run spell login or spell keys generate with new code that generates ssh config files
    if not os.path.isfile(ssh_config_path):
        write_ssh_config_file(ctx.obj["config_handler"])
    if os.path.isfile(ssh_key_path) and os.path.isfile(ssh_config_path) and "GIT_SSH_COMMAND" not in gitenv:
        ssh_cmd = gitenv.get("GIT_SSH", "ssh")
        gitenv["GIT_SSH_COMMAND"] = "{} -F '{}' -o IdentitiesOnly=yes -i '{}'".format(
            ssh_cmd, ssh_config_path, ssh_key_path
        )

    # Commit uncommitted changes to parallel repo
    uncommitted_hash = None
    if (has_staged(git_repo) or has_unstaged(git_repo)) and include_uncommitted:
        click.echo(with_emoji("✨", "Preparing uncommitted changes" + ellipses(ctx.obj["utf8"]), ctx.obj["utf8"]))
        clean_hardlinked_repo(ctx, git_repo)
        git_dir = hardlink_repo(ctx, git_repo)
        uncommitted_hash = commit_to_parallel(git_repo, git_dir)

    if get_repo_size(git_repo) > (1 << 30):
        raise ExitException("Repo size must be less than 1GB")
    # push to the spell remote
    refspec = "{}:refs/heads/br_{}".format(git_repo.head, uncommitted_hash or commit_hash)
    git_push = [
        "git",
        "--git-dir",
        git_dir,
        "--work-tree",
        git_repo.working_dir,
        "push",
        "--no-verify",  # TODO(peter): Re-enable pre-push hooks when we support Git LFS
        git_remote_url,
        refspec,
    ]
    try:
        subprocess.check_call(git_push, cwd=git_path, env=gitenv)
    except subprocess.CalledProcessError:
        msg = "Push to Spell remote failed"
        v = git_version()
        if v and v < (2, 3):
            msg += ". Git version 2.3 or newer is required -- detected Git version: {}".format(v)
        elif not v:
            msg += ". Please ensure Git version 2.3 or newer is installed."
        raise ExitException(msg)

    # Clean up parallel repo
    if uncommitted_hash is not None:
        clean_hardlinked_repo(ctx, git_repo)

    return workspace_id, commit_hash, commit.message.strip(), uncommitted_hash


def get_remote_url(repo):
    try:
        return repo.remote().url
    except ValueError:
        return


def has_staged(repo):
    """given a git.Repo, returns True if there are staged changes in the index"""
    if repo.is_dirty(index=True, working_tree=False, untracked_files=False):
        return len(get_staged_filenames(repo)) > 0
    return False


def get_staged_filenames(repo):
    staged_fnames = []
    for diff in repo.index.diff("HEAD"):
        # For file creation, a_path will be None so fall back to b_path
        path = diff.a_path or diff.b_path
        if path.split(".")[-1] not in WHITELISTED_FILEEXTS:
            staged_fnames.append(path)
    return staged_fnames


def has_unstaged(repo):
    """given a git.Repo, returns True if there are unstaged changes in the working tree"""
    if repo.is_dirty(index=False, working_tree=True, untracked_files=False):
        return len(get_unstaged_filenames(repo)) > 0
    return False


def get_unstaged_filenames(repo):
    return [diff.a_path for diff in repo.index.diff(None) if diff.a_path.split(".")[-1] not in WHITELISTED_FILEEXTS]


def has_untracked(repo):
    """given a git.Repo, returns True if there are untracked files in the working tree"""
    if repo.is_dirty(index=False, working_tree=False, untracked_files=True):
        return len(get_untracked_filenames(repo)) > 0
    return False


def get_untracked(repo):
    return "\n".join(["\t{}".format(f) for f in get_untracked_filenames(repo)])


def get_untracked_filenames(repo):
    return [f for f in repo.untracked_files if os.path.split(f)[1] not in BLACKLISTED_FILES]


def get_git_repo(f):
    """decorator that passes the git repo into the called function as git_repo kwarg"""
    import git

    def inner(*args, **kwargs):
        git_repo = None
        try:
            git_repo = git.Repo(os.getcwd(), search_parent_directories=True)
        except git.exc.InvalidGitRepositoryError:
            pass
        f(*args, git_repo=git_repo, **kwargs)

    return inner


# git_version returns the first two digits of git version as a tuple of ints
# or None if the version cannot be determined
def git_version():
    try:
        output = subprocess.check_output(["git", "--version"]).decode()
        # match the first 2 digits of version since that is all we care about
        m = re.match(r"(\d+)\.(\d+)", output.split()[2])
        if m:
            return (int(m.group(1)), int(m.group(2)))
        return None
    except Exception as e:
        with push_scope() as scope:
            scope.level = "info"
            scope.set_tag("internal_exception", "true")
            capture_exception(e)
            return None


def get_repo_size(r):
    for line in r.git.count_objects("-v").splitlines():
        if line.startswith("size:"):
            return int(line[len("size:") :].strip())
    return None


# Get the path relative to the repos root if the path is tracked by the repo.
# Returns None if the path is not tracked.
def get_tracked_repo_path(repo, path):
    expanded_path = os.path.expanduser(path)
    if not os.path.exists(expanded_path):
        return None

    # Start with naive is subpath logic to quickly exit if the file isn't in
    # the repo directory
    realpath = os.path.realpath(expanded_path)
    repo_root = os.path.realpath(repo.local_root)
    if os.path.commonprefix((realpath, repo_root)) != repo_root:
        return None

    git_repo = git.Repo(repo_root)
    relative_path = os.path.relpath(realpath, repo_root)

    # Check if the path is in the staged changes. We include all staged changes
    # so this is valid
    files_staged = [item.a_path for item in git_repo.index.diff("HEAD")]
    if relative_path in files_staged:
        return relative_path

    # Split relative path into intermediate dirs so we
    # can navigate dir-by-dir through the repo file tree
    path_pieces = []
    curr_path = relative_path
    while curr_path != "":
        curr_path, piece = os.path.split(curr_path)
        path_pieces.insert(0, piece)

    # Navigate through the repo tree
    tree = git_repo.tree()
    for piece in path_pieces:
        was_found = False
        # Search for path piece in directories of tree. If a match is found,
        # that path piece is a directory that is tracked by the repo
        for candidate in tree.trees:
            if candidate.name == piece:
                tree = candidate
                was_found = True
                break
        if was_found:
            continue
        # Search for path piece in files of tree. If a match is found, that
        # path piece is a file that is tracked by the repo, and since it is a
        # file, no further iteration is required so return immediately
        for candidate in tree.blobs:
            if candidate.name == piece:
                return relative_path if os.path.isfile(realpath) else None
        if not was_found:
            return None
    return relative_path
