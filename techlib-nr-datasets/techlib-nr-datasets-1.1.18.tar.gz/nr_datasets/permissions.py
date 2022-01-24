# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Dataset permisssion factories."""

from invenio_access import Permission, ParameterizedActionNeed
from oarepo_communities.constants import COMMUNITY_READ, STATE_APPROVED
from oarepo_communities.permissions import read_object_permission_impl, require_action_allowed, owner_permission_impl, \
    community_member_permission_impl, community_publisher_permission_impl, community_curator_permission_impl
from oarepo_fsm.permissions import require_all, require_any, state_required

from nr_datasets.constants import open_access_slug, restricted_slug, embargoed_slug
from nr_datasets.utils import access_rights_factory


def access_rights_required(rights):
    rights = set(rights)

    def factory(record, *_args, **_kwargs):
        def can():
            current_rights = record.get('accessRights')
            if current_rights and len(current_rights) == 1:
                current_rights = current_rights[0]
            else:
                return False

            return current_rights['links']['self'] in rights

        return type('AccessRightsRequiredPermission', (), {'can': can})

    return factory


def community_read_permission_impl(record, *args, **kwargs):
    communities = [record.primary_community, *record.secondary_communities]
    return require_all(
        require_action_allowed(COMMUNITY_READ),
        require_any(
            #: Record AUTHOR can READ his own records
            owner_permission_impl,
            require_all(
                #: User's role has granted READ permissions in record's communities
                Permission(*[ParameterizedActionNeed(COMMUNITY_READ, x) for x in communities]),
                require_any(
                    #: Community MEMBERS can READ APPROVED community records
                    require_all(
                        state_required(STATE_APPROVED),
                        require_any(
                            community_member_permission_impl,
                            community_publisher_permission_impl
                        )
                    ),
                    #: Community CURATORS can READ ALL community records
                    community_curator_permission_impl
                )
            )
        )
    )


def files_read_permission_factory(record, *args, **kwargs):
    return require_any(
        require_all(
            community_read_permission_impl(record, *args, **kwargs),
            access_rights_required([
                access_rights_factory(embargoed_slug),
                access_rights_factory(restricted_slug)]),
        ),
        require_all(
            read_object_permission_impl,
            access_rights_required([access_rights_factory(open_access_slug)])
        )
    )(record, *args, **kwargs)
