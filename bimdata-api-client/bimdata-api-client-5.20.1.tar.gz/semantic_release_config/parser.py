from semantic_release import UnknownCommitMessageStyleError
from semantic_release.settings import config
from semantic_release.history.parser_helpers import ParsedCommit


def parse_commit_message(message):
    """
    Parses a commit message according to the 1.0 version of python-semantic-release. It expects
    a tag of some sort in the commit message and will use the rest of the first line as changelog
    content.
    :param message: A string of a commit message.
    :raises semantic_release.UnknownCommitMessageStyle: If it does not recognise the commit style
    :return: A tuple of (level to bump, type of change, scope of change, a tuple with descriptions)
    """
    if config.get('minor_tag') in message:
        level = 'feature'
        level_bump = 2
        subject = message.replace(config.get('minor_tag'), '')

    elif config.get('fix_tag') in message:
        level = 'fix'
        level_bump = 1
        subject = message.replace(config.get('fix_tag'), '')

    elif config.get('major_tag') in message:
        level = 'breaking'
        level_bump = 3
        subject = message.replace(config.get('major_tag'), '')

    else:
        raise UnknownCommitMessageStyleError(
            'Unable to parse the given commit message: {0}'.format(message)
        )

    body = message
    footer = message

    return ParsedCommit(level_bump, level, None, (subject.strip(), body.strip(), footer.strip()), None)
