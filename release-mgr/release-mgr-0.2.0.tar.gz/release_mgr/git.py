from subprocess import check_output


def git(*args):
    cmd = ["git"]
    cmd.extend(args)
    return check_output(cmd).decode("utf-8")


def get_repo():
    remotes = check_output(["git", "remote", "-v"]).decode("utf-8").split("\n")
    for remote in remotes:
        if not remote:
            continue

        first_segment, _ = remote.split(" ")
        _, url = first_segment.split("\t")

        if "github.com" not in url:
            continue

        if url.startswith("ssh") or url.startswith("git@"):
            repo = url.split(":")[-1]
            if repo.endswith(".git"):
                repo = repo[: -len(".git")]

            return repo
        else:
            return "/".join(url.split("/")[-2:])


def get_tags():
    return (
        check_output(
            [
                "git",
                "for-each-ref",
                "--sort=-taggerdate",
                "--format",
                "%(refname)",
                "refs/tags",
            ],
        )
        .decode("utf-8")
        .split("\n")
    )


def get_commit_for_tag(tag):
    return check_output(["git", "rev-list", "-n", "1", tag]).decode("utf-8").strip()


def get_contributors_between(oldest_commit, latest_commit):
    return (
        check_output(
            [
                "git",
                "log",
                "--pretty=format:%an <%ae>",
                f"{oldest_commit}...{latest_commit}",
            ],
        )
        .decode("utf-8")
        .split("\n")
    )


def get_messages_between(oldest_commit, latest_commit):
    return (
        check_output(
            [
                "git",
                "log",
                "--pretty=format:%h %s",
                f"{oldest_commit}...{latest_commit}",
            ],
        )
        .decode("utf-8")
        .split("\n")
    )
