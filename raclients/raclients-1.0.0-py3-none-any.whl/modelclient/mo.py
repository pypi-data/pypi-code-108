#!/usr/bin/env python3
# --------------------------------------------------------------------------------------
# SPDX-FileCopyrightText: 2022 Magenta ApS <https://magenta.dk>
# SPDX-License-Identifier: MPL-2.0
# --------------------------------------------------------------------------------------
from typing import Any

from ramodels.mo import Employee
from ramodels.mo import FacetClass
from ramodels.mo import OrganisationUnit
from ramodels.mo._shared import MOBase
from ramodels.mo.details import Address
from ramodels.mo.details import Association
from ramodels.mo.details import Engagement
from ramodels.mo.details import EngagementAssociation
from ramodels.mo.details import ITUser
from ramodels.mo.details import Leave
from ramodels.mo.details import Manager
from ramodels.mo.details import Role

from raclients.modelclient.base import ModelBase
from raclients.modelclient.base import ModelClientBase


class ModelClient(ModelClientBase[MOBase]):
    upload_http_method = "POST"
    path_map = {
        Address: "/service/details/create",
        Association: "/service/details/create",
        Employee: "/service/e/create",
        Engagement: "/service/details/create",
        EngagementAssociation: "/service/details/create",
        FacetClass: "/service/f/{facet_uuid}/",
        ITUser: "/service/details/create",
        Leave: "/service/details/create",
        Manager: "/service/details/create",
        OrganisationUnit: "/service/ou/create",
        Role: "/service/details/create",
    }

    def __init__(self, force: bool = False, *args: Any, **kwargs: Any):
        """MO ModelClient.

        Args:
            force: Bypass MO API validation.
            *args: Positional arguments passed through to ModelClientBase.
            **kwargs: Keyword arguments passed through to ModelClientBase.

        Example usage::

            async with ModelClient(
                base_url="http://mo:5000",
                client_id="AzureDiamond",
                client_secret="hunter2",
                auth_server=parse_obj_as(AnyHttpUrl,"http://keycloak.example.org/auth"),
                auth_realm="mordor",
            ) as client:
                r = await client.upload(objects)
        """
        super().__init__(*args, **kwargs)
        self.force = force

    def get_object_url(self, obj: ModelBase) -> str:
        # Note that we additionally format the object's fields onto the path mapping to
        # support schemes such as /service/f/{facet_uuid}/, where facet_uuid is
        # retrieved from obj.facet_uuid.
        path = self.path_map[type(obj)].format_map(obj.dict())
        return f"{path}?force={int(self.force)}"
