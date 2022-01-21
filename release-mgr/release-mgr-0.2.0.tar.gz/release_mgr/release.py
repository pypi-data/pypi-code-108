from release_mgr.git import get_contributors_between, get_messages_between


def build_changelog(messages):
    return "\n".join(
        [
            f"- {message}"
            for message in messages
            if message
            and "release: " not in message
            and "Merge pull request" not in message
        ],
    )


def build_contributors(emails):
    return "\n".join({f"- {email}" for email in emails if email})


def build_release_notes(
    version,
    messages,
    emails,
    title="",
):
    if title:
        release_notes = f"# {title}\n\n"
    else:
        release_notes = f"# Release {version}\n\n"

    release_notes += build_changelog(messages)
    release_notes += "\n\n# Contributors to this Release\n\n"
    release_notes += build_contributors(emails)
    release_notes += "\n"

    return release_notes


def release_notes_for_version(
    version,
    version_commit,
    last_version_commit,
):
    messages = get_messages_between(last_version_commit, version_commit)
    emails = get_contributors_between(last_version_commit, version_commit)
    return build_release_notes(
        version=version,
        messages=messages,
        emails=emails,
    )
