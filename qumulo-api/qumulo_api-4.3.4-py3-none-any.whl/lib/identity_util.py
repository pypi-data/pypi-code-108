# Copyright (c) 2019 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import re

from typing import Optional, Union

from typing_extensions import TypedDict

from qumulo.lib.obj import Object

# Well known identifiers used internally by QSFS
ADMIN_USER_ID = '500'
ADMINS_GROUP_ID = '512'
USERS_GROUP_ID = '513'
GUEST_USER_ID = '501'
GUESTS_GROUP_ID = '514'
EVERYONE_ID = str(0x200000000)
CREATOR_GROUP_ID = str(0xFFFFFFFF00000001)
CREATOR_OWNER_ID = str(0xFFFFFFFF00000000)
OWNER_RIGHTS_ID = str(0xFFFFFFFF00000004)
FILE_OWNER_ID = str(0xFFFFFFFE00000001)
FILE_GROUP_OWNER_ID = str(0xFFFFFFFE00000002)

#   ____                              _
#  / ___|___  _ ____   _____ _ __ ___(_) ___  _ __  ___
# | |   / _ \| '_ \ \ / / _ \ '__/ __| |/ _ \| '_ \/ __|
# | |__| (_) | | | \ V /  __/ |  \__ \ | (_) | | | \__ \
#  \____\___/|_| |_|\_/ \___|_|  |___/_|\___/|_| |_|___/
#  FIGLET: Conversions
#

POSIX_USER_SID_PREFIX = 'S-1-5-88-1'  # Used as S-1-5-88-1-uid
POSIX_GROUP_SID_PREFIX = 'S-1-5-88-2'  # Used as S-1-5-88-2-gid


def sid_from_posix_uid(uid: int) -> str:
    """
    Produce the sid that qsfs uses to represent a given NFS uid.
    """
    return f'{POSIX_USER_SID_PREFIX}-{uid}'


def sid_from_posix_gid(gid: int) -> str:
    """
    Produce the sid that qsfs uses to represent a given NFS gid.
    """
    return f'{POSIX_GROUP_SID_PREFIX}-{gid}'


def auth_id_from_posix_uid(uid: int) -> str:
    """
    Produce the auth_id that qsfs uses internally to represent a given NFS uid.
    """
    return str((3 << 32) + uid)


def auth_id_from_posix_gid(gid: int) -> str:
    """
    Produces the auth_id that qsfs uses internally to represent a given NFS gid.
    """
    return str((4 << 32) + gid)


# Typical NT SIDs are of the form S-1-5-21-X-Y-Z-RID, where 5 is the NT authority, 21 is the
# "non-unique" sub-authority, and X, Y, and Z are random numbers that identify a domain / machine.
NT_SID_REGEX = re.compile(r'^S-1-5-21-[0-9]+-[0-9]+-[0-9]+-([0-9]+)$')


def rid_from_nt_authority_sid(sid: str) -> int:
    """
    Extract the RID from a SID that would be generated for a domain /
    qfsd local / windwos local user.
    """
    m = NT_SID_REGEX.match(sid)
    assert m is not None, f'{sid!r} does not appear to be a valid SID'
    return int(m.group(1))


# Well-known RIDs. See https://docs.microsoft.com/en-us/windows/desktop/secauthz/well-known-sids
ADMIN_RID = 500
GUEST_RID = 501
ADMINS_RID = 512
USERS_RID = 513
GUESTS_RID = 514

#  ___    _            _   _ _
# |_ _|__| | ___ _ __ | |_(_) |_ _   _
#  | |/ _` |/ _ \ '_ \| __| | __| | | |
#  | | (_| |  __/ | | | |_| | |_| |_| |
# |___\__,_|\___|_| |_|\__|_|\__|\__, |
#                                |___/
#  FIGLET: Identity
#

# A SID starts with S, followed by hyphen separated version, authority, and at least one
# sub-authority
SID_REGEXP = re.compile(r'S-[0-9]+-[0-9]+(?:-[0-9]+)+$')

EVERYONE_NAME = 'Everyone'
GUEST_NAME = 'Guest'

LOCAL_DOMAIN = 'LOCAL'
WORLD_DOMAIN = 'WORLD'
POSIX_USER_DOMAIN = 'POSIX_USER'
POSIX_GROUP_DOMAIN = 'POSIX_GROUP'
AD_DOMAIN = 'ACTIVE_DIRECTORY'
CREATOR_DOMAIN = 'API_CREATOR_DOMAIN'
INTERNAL_DOMAIN = 'API_INTERNAL_DOMAIN'
NULL_DOMAIN = 'API_NULL_DOMAIN'

VALID_DOMAIN_PREFIXES = ('local', 'world', 'ldap_user', 'ldap_group', 'ad')
VALID_IDENTITY_PREFIXES = VALID_DOMAIN_PREFIXES + ('name', 'sid', 'uid', 'gid', 'auth_id')


class ApiIdentity(TypedDict, total=False):
    domain: str  # @see api_identity_domain_encode_json
    auth_id: str  # @see auth_id_encode_json
    uid: int
    gid: int
    sid: str
    name: str


def build_api_identity(id_spec: str) -> ApiIdentity:
    # Attempt to split by type or domain prefix (e.g. uid:, local:)
    identity_pair = [i.strip() for i in id_spec.split(':', 1)]
    if len(identity_pair) == 1:
        # If prefix-less, assume identity is a name or SID
        if len(identity_pair[0]) == 0:
            raise ValueError('Identity specifiers cannot be empty')

        identity_capitalized = identity_pair[0].capitalize()
        if SID_REGEXP.match(identity_capitalized):
            return ApiIdentity(sid=identity_capitalized)
        else:
            return ApiIdentity(name=identity_pair[0])

    prefix, identity = identity_pair
    prefix = prefix.lower()
    if prefix == 'uid':
        return ApiIdentity(uid=int(identity))
    elif prefix == 'gid':
        return ApiIdentity(gid=int(identity))
    elif prefix == 'auth_id':
        # NB: validate int, and allow hex if desired:
        return ApiIdentity(auth_id=str(int(identity, base=0)))
    elif prefix == 'sid':
        return ApiIdentity(sid=identity)
    elif prefix == 'name':
        return ApiIdentity(name=identity)
    elif prefix == 'world':
        if identity.lower() != EVERYONE_NAME.lower():
            raise ValueError(
                'Identity prefix "world" may only be used '
                'with the Everyone identity (i.e. world:Everyone)'
            )

        return ApiIdentity(domain=WORLD_DOMAIN, name=EVERYONE_NAME)
    elif prefix == 'local':
        return ApiIdentity(domain=LOCAL_DOMAIN, name=identity)
    elif prefix == 'ldap_user':
        return ApiIdentity(domain=POSIX_USER_DOMAIN, name=identity)
    elif prefix == 'ldap_group':
        return ApiIdentity(domain=POSIX_GROUP_DOMAIN, name=identity)
    elif prefix == 'ad':
        return ApiIdentity(domain=AD_DOMAIN, name=identity)
    elif '=' in prefix:
        # Assume we are dealing with a distinguished name that happens to contain a ':'
        return ApiIdentity(name=id_spec)
    else:
        raise ValueError(
            'Identity prefix must be '
            + ', '.join(['"%s"' % v for v in VALID_IDENTITY_PREFIXES[:-1]])
            + ', or "%s"' % VALID_IDENTITY_PREFIXES[-1]
        )


class Identity(Object):
    """
    Convenience for interacting with APIs which use @ref api_identity.
    """

    def __init__(self, id_spec: Union[ApiIdentity, 'Identity', str]):
        r"""
        Parse a dict or string representation of an Identity.

        As a string, an Identity can be represented via SID, UID, GID, or QSFS
        auth_id using a type prefix, e.g.:

            sid:S-1-5-88-1
            uid:1001
            gid:2001
            auth_id:12884901889

        Alternatively, a name can be specified. Note that the name might be ambiguous
        (e.g. same name exists in multiple identity sources, like QSFS and AD).

        To reduce the likelihood of ambiguity when specifying a name, use a domain prefix to declare
        the identity source, e.g.:

            local:alice
            world:Everyone
            ldap_user:bob
            ldap_group:researchers
            ad:MYDOMAIN\Marketing

        Domain prefixes are optional.
        """
        if isinstance(id_spec, dict):
            super().__init__(d=id_spec)
        elif isinstance(id_spec, Identity):
            super().__init__(d=id_spec.dictionary())
        else:
            super().__init__(d=build_api_identity(id_spec))

    def __eq__(self, other: object) -> bool:
        """
        Two identities are considered equal if they share at least one common
        attribute.

        N.B. This assumes that names are unique across identity sources, which
        is not guaranteed, but should be very uncommon (see @ref api_identity).

        It is also assumed that @ref self and @ref other are constructed either
        from an API response or string representation of an identity.
        """
        if not isinstance(other, Object):
            return False

        common = set(other.dictionary().keys())
        common = common.intersection(self.dictionary().keys())
        if 'domain' in common:
            # Unlike the other attributes, domain being equal doesn't imply
            # all other attributes must be equal. If, however, domain is not
            # equal, then the IDs are different (even if, for example, they
            # have the same unqualified name attributes.)
            if self['domain'] != other['domain']:
                return False
            common.discard('domain')
        comp = [other[k] == self[k] for k in common]
        res = all(comp) and (len(comp) > 0)
        assert all(c == res for c in comp)
        return res

    def __str__(self) -> str:
        """
        @return A string representation of the Identity, optimized for legibility.
        The returned representation can be parsed into an equivalent Identity.
        """
        attrs = self.dictionary()

        if attrs.get('auth_id') == EVERYONE_ID:
            return EVERYONE_NAME

        if attrs.get('auth_id') == GUEST_USER_ID:
            return GUEST_NAME

        if attrs.get('name') is not None:
            return attrs['name']

        return self.numeric_str()

    def numeric_str(self, preferred_type: Optional[str] = None) -> str:
        """
        @p preferred_type Can be specified to override the default preference
            order of identity types.
        @return A string represention of the preferred numeric form of an
            Identity (i.e. what would be displayed if a name is unknown).
        The returned representation can be parsed into an equivalent Identity.
        """
        attrs = self.dictionary()
        if preferred_type is not None and attrs.get(preferred_type) is not None:
            if preferred_type == 'sid':
                return attrs['sid']
            else:
                return f'{preferred_type}:{attrs.get(preferred_type)}'

        if attrs.get('uid') is not None:
            return 'uid:{}'.format(attrs['uid'])

        if attrs.get('gid') is not None:
            return 'gid:{}'.format(attrs['gid'])

        if attrs.get('sid') is not None:
            if attrs.get('domain') != LOCAL_DOMAIN:
                return attrs['sid']

        if attrs.get('auth_id') is not None:
            return 'auth_id:{}'.format(attrs['auth_id'])

        # At least one field must be present, so by process of elimination, there must be a SID.
        return str(attrs['sid'])

    def has_name(self) -> bool:
        attrs = self.dictionary()
        return attrs.get('name') is not None

    def pretty_domain(self) -> Optional[str]:
        # Don't pretty print World because it's only for Everyone
        attrs = self.dictionary()

        if attrs.get('domain') == LOCAL_DOMAIN:
            return 'local'

        if attrs.get('domain') == POSIX_USER_DOMAIN:
            return 'ldap_user'

        if attrs.get('domain') == POSIX_GROUP_DOMAIN:
            return 'ldap_group'

        if attrs.get('domain') == AD_DOMAIN:
            return 'ad'

        return None
