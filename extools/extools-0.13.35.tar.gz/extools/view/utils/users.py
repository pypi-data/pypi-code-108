import re

from extools.view import exview
from extools.view.errors import ExViewRecordDoesNotExist, ExViewError
from extools.message import logger_for_module

def get_user(userid):
    """Get a user's email from the a4wuser view.

    :param a4wuser: An open AS0003 view
    :type a4wuser: accpac.View
    :param userid: The Sage User ID.
    :type userid: str
    :returns: user object
    :rtype: dict
    """
    try:
        with exview("AS0003") as user:
            user.put("USERID", userid)
            user.read()
            return user.to_dict()
    except ExViewRecordDoesNotExist:
        return {}
    return user.to_dict()

def get_users_for_group(groupid):
    """Get the users and their emails for a vi group.

    :param groupid: The Extender Group ID.
    :type groupid: str
    :returns: list of matching user dicts.
    :rtype: [{}, ...]
    """
    users = []
    try:
        with exview("VI0024") as groups:
            groups.browse('GROUP="{}"'.format(groupid))
            while groups.fetch():
                user = get_user(groups.get("USERID"))
                if user:
                    users.append(user)
    except ExViewError:
        pass

    return users

def resolve_users(emails):
    """Resolve a ; separated list to a list of (username, email) tuples.

    Given a ; separated list, resolve to Sage Usernames and User Emails.
    If an email is provided directly, return the email as the username.

    Consider a configuration in which:

    - There is a group MYGRP composed of three users:

      - ANNE (anne@a.com), BOB (bobby@a.com), CHRIS (cbinckly@a.com)

    - Other users are defined in Sage but are not members of the group.

      - DARREN (darren@a.com), ESTHER (esther@a.com), FRANK (frank@a.com)

    - And some clients are not in the Sage database at all:

      - user1@client.com, user2@client.com

    .. code-block:: python

        >>> resolve_users("MYGRP;DARREN;user1@client.com")
        [(ANNE, anne@a.com), (BOB, bobby@a.com), (CHRIS, cbinckly@a.com),
         (DARREN, darren@a.com), (user1@client.com, user1@client.com)]

    :param emails: ';' separated list
    :type emails: str
    :returns: list of (username, email) tuples
    :rtype: [(str, str)]
    """
    users = []
    emails = [e.strip() for e in emails.split(";") if e]

    for email in emails:
        if re.search(r'[^@]+@.+\.\w+', email):
            users.append((email, email, ))
        elif email:
            user = get_user(email)
            if user:
                users.append((user['USERID'], user['EMAIL1']))
            else:
                users += [(u['USERID'], u['EMAIL1'], ) for u in
                          get_users_for_group(email)]

    return users

def userid_for_email(email):
    """Find the userid for a given email.

    :param email: email address
    :type email: str
    :returns: userid or ''
    :rtype: str
    """
    try:
        with exview("AS0003") as users:
            users.browse("", 1)
            while users.fetch():
                if users.email1 == email or users.email2 == email:
                    return users.userid
    except ExViewError:
        pass
    return ''

def email_for_user(userid):
    """Find the email for the given user.

    :param user: Sage User ID
    :type user: str
    :return: User email
    :rtype: str
    """
    try:
        with exview("AS0003") as u:
            u.put("USERID", userid)
            u.read()
            return u.email1 or u.email2
    except ExViewError as err:
        pass
    return ''
