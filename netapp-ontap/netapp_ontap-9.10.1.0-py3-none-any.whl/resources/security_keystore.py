r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A keystore describes a key-manager, specifically the type of key-manager.<p/>
## Examples
### Retrieving information for all configured key managers
The following example shows how to retrieve information about all configured key managers.
```
# The API:
GET /api/security/key-stores
# The call:
curl -X GET 'https://<mgmt-ip>/api/security/key-stores?fields=*' -H 'accept: application/hal+json'
# The response:
{
  "records": [
      {
      "uuid": "33421d82-0a8d-11ec-ae88-005056bb5955",
      "keystore": {
          "type": "akv"
      },
      "_links": {
          "self": {
          "href": "/api/security/key-stores/33421d82-0a8d-11ec-ae88-005056bb5955/akv"
          }
      }
  },
  {
      "uuid": "46a0b20a-0a8d-11ec-ae88-005056bb5955",
      "keystore": {
          "type": "okm"
  },
      "_links": {
          "self": {
          "href": "/api/security/key-stores/46a0b20a-0a8d-11ec-ae88-005056bb5955/okm"
          }
      }
      }
  ],
  "num_records": 2,
  "_links": {
      "self": {
      "href": "/api/security/key-stores"
      }
  }
}
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


__all__ = ["SecurityKeystore", "SecurityKeystoreSchema"]
__pdoc__ = {
    "SecurityKeystoreSchema.resource": False,
    "SecurityKeystore.security_keystore_show": False,
    "SecurityKeystore.security_keystore_create": False,
    "SecurityKeystore.security_keystore_modify": False,
    "SecurityKeystore.security_keystore_delete": False,
}


class SecurityKeystoreSchema(ResourceSchema):
    """The fields of the SecurityKeystore object"""

    location = fields.Str(
        data_key="location",
    )
    r""" Indicates whether the keystore is onboard or external. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the security_keystore. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['okm', 'kmip', 'akv', 'gcp', 'aws']),
    )
    r""" Type of keystore that is configured: * 'okm' - Onboard Key Manager * 'kmip' - External Key Manager * 'akv' - Azure Key Vault Key Management Service * 'gcp' - Google Cloud Platform Key Management Service * 'aws' - Amazon Web Service Key Management Service


Valid choices:

* okm
* kmip
* akv
* gcp
* aws """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The uuid field of the security_keystore. """

    @property
    def resource(self):
        return SecurityKeystore

    gettable_fields = [
        "location",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "uuid",
    ]
    """location,svm.links,svm.name,svm.uuid,type,uuid,"""

    patchable_fields = [
        "location",
        "svm.name",
        "svm.uuid",
        "type",
    ]
    """location,svm.name,svm.uuid,type,"""

    postable_fields = [
        "location",
        "svm.name",
        "svm.uuid",
        "type",
    ]
    """location,svm.name,svm.uuid,type,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SecurityKeystore.get_collection(fields=field)]
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
            raise NetAppRestError("SecurityKeystore modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SecurityKeystore(Resource):
    """Allows interaction with SecurityKeystore objects on the host"""

    _schema = SecurityKeystoreSchema
    _path = "/api/security/key-stores"

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves keystores.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `keystore.location`
* `svm.name`
* `svm.uuid`
### Related ONTAP commands
* `security key-manager show-key-store`

### Learn more
* [`DOC /security/key-stores`](#docs-security-security_key-stores)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security keystore show")
        def security_keystore_show(
            fields: List[Choices.define(["location", "type", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SecurityKeystore resources

            Args:
                location: Indicates whether the keystore is onboard or external.
                type: Type of keystore that is configured: * 'okm' - Onboard Key Manager * 'kmip' - External Key Manager * 'akv' - Azure Key Vault Key Management Service * 'gcp' - Google Cloud Platform Key Management Service * 'aws' - Amazon Web Service Key Management Service 
                uuid: 
            """

            kwargs = {}
            if location is not None:
                kwargs["location"] = location
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SecurityKeystore.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SecurityKeystore resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves keystores.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `keystore.location`
* `svm.name`
* `svm.uuid`
### Related ONTAP commands
* `security key-manager show-key-store`

### Learn more
* [`DOC /security/key-stores`](#docs-security-security_key-stores)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






