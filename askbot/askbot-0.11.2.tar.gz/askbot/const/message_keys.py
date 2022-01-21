'''
This file must hold keys for translatable messages
that are used as variables
it is important that a dummy _() function is used here
this way message key will be pulled into django.po
and can still be used as a variable in python files.
'''
_ = lambda v:v

#NOTE: all strings must be explicitly put into this dictionary,
#because you don't want to import _ from here with import *
__all__ = []

#messages loaded in the templates via direct _ calls
_('most relevant questions')
_('click to see most relevant questions')
_('by relevance')
_('click to see the oldest questions')
_('by date')
_('click to see the newest questions')
_('click to see the least recently updated questions')
_('by activity')
_('click to see the most recently updated questions')
_('click to see the least answered questions')
_('by answers')
_('click to see the most answered questions')
_('click to see least voted questions')
_('by votes')
_('click to see most voted questions')
_('interesting')
_('ignored')
_('subscribed')
TAGS_ARE_REQUIRED_MESSAGE = _('tags are required')
TAG_WRONG_CHARS_MESSAGE = _(
    'please use letters, numbers and characters "-+.#"'
)
TAG_WRONG_FIRST_CHAR_MESSAGE = _(
    '# is not a valid character at the beginning of tags, use only letters and numbers'
)
ACCOUNT_CANNOT_PERFORM_ACTION = _(
    'Sorry, you cannot %(perform_action)s because %(your_account_is)s'
)
MIN_REP_REQUIRED_TO_PERFORM_ACTION = _('>%(min_rep)s points required to %(perform_action)s')
CANNOT_PERFORM_ACTION_UNTIL = _('Sorry, you will be able to %(perform_action)s after %(until)s')
MODERATORS_OR_AUTHOR_CAN_PEFROM_ACTION = _(
    'Sorry, only moderators or the %(post_author)s %(perform_action)s'
)
PUNISHED_USER_INFO = _('Your account might be blocked in error - please contact the site administrators, if you think so.')
