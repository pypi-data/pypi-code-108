r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

Generates and retrieves the password for a given NDMP user in the SVM context.
### Examples
<br/>
```
GET "/api/protocols/ndmp/svms/ca8e29e0-e116-11ea-876c-0050568ea754/passwords/ndmpuser"
```
<br/>
"""

import asyncio
from datetime import datetime
import inspect
from typing import Callable, Iterable, List, Optional, Union

try:
    RECLINE_INSTALLED = False
    import recline
    from recline.arg_types.choices import Choices
    from recline.commands import ClicheCommandError
    from netapp_ontap.resource_table import ResourceTable
    RECLINE_INSTALLED = True
except ImportError:
    pass

from marshmallow import fields, EXCLUDE  # type: ignore

import netapp_ontap
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size
from netapp_ontap import NetAppResponse, HostConnection
from netapp_ontap.validations import enum_validation, len_validation, integer_validation
from netapp_ontap.error import NetAppRestError


__all__ = ["NdmpPassword", "NdmpPasswordSchema"]
__pdoc__ = {
    "NdmpPasswordSchema.resource": False,
    "NdmpPassword.ndmp_password_show": False,
    "NdmpPassword.ndmp_password_create": False,
    "NdmpPassword.ndmp_password_modify": False,
    "NdmpPassword.ndmp_password_delete": False,
}


class NdmpPasswordSchema(ResourceSchema):
    """The fields of the NdmpPassword object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ndmp_password. """

    password = fields.Str(
        data_key="password",
    )
    r""" NDMP Password """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the ndmp_password. """

    user = fields.Str(
        data_key="user",
    )
    r""" NDMP user """

    @property
    def resource(self):
        return NdmpPassword

    gettable_fields = [
        "links",
        "password",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "user",
    ]
    """links,password,svm.links,svm.name,svm.uuid,user,"""

    patchable_fields = [
        "password",
        "svm.name",
        "svm.uuid",
        "user",
    ]
    """password,svm.name,svm.uuid,user,"""

    postable_fields = [
        "password",
        "svm.name",
        "svm.uuid",
        "user",
    ]
    """password,svm.name,svm.uuid,user,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NdmpPassword.get_collection(fields=field)]
    return getter

async def _wait_for_job(response: NetAppResponse) -> None:
    """Examine the given response. If it is a job, asynchronously wait for it to
    complete. While polling, prints the current status message of the job.
    """

    if not response.is_job:
        return
    from netapp_ontap.resources import Job
    job = Job(**response.http_response.json()["job"])
    while True:
        job.get(fields="state,message")
        if hasattr(job, "message"):
            print("[%s]: %s" % (job.state, job.message))
        if job.state == "failure":
            raise NetAppRestError("NdmpPassword modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NdmpPassword(Resource):
    """Allows interaction with NdmpPassword objects on the host"""

    _schema = NdmpPasswordSchema
    _path = "/api/protocols/ndmp/svms/{svm[uuid]}/passwords"
    _keys = ["svm.uuid", "user"]







    def get(self, **kwargs) -> NetAppResponse:
        r"""Generates and retrieves the password for the specified NDMP user.
### Related ONTAP commands
* `vserver services ndmp generate-password`
### Learn more
* [`DOC /protocols/ndmp/svms/{svm.uuid}/passwords/{user}`](#docs-ndmp-protocols_ndmp_svms_{svm.uuid}_passwords_{user})
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ndmp password show")
        def ndmp_password_show(
            svm_uuid,
            password: Choices.define(_get_field_list("password"), cache_choices=True, inexact=True)=None,
            user: Choices.define(_get_field_list("user"), cache_choices=True, inexact=True)=None,
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single NdmpPassword resource

            Args:
                password: NDMP Password
                user: NDMP user
            """

            kwargs = {}
            if password is not None:
                kwargs["password"] = password
            if user is not None:
                kwargs["user"] = user
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = NdmpPassword(
                svm_uuid,
                **kwargs
            )
            resource.get()
            return [resource]





