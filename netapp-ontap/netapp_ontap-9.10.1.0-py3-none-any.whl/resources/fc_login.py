r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Fibre Channel (FC) logins represent connections formed by FC initiators that have successfully logged in to ONTAP. This represents the FC login on which higher-level protocols such as Fibre Channel Protocol and NVMe over FC (NVMe/FC) rely.<br/>
The Fibre Channel logins REST API provides information about active FC logins.
## Examples
### Retrieving all FC logins
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcLogin

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcLogin.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    FcLogin(
        {
            "interface": {
                "uuid": "01056403-1383-bc4b-786a-93e8ea35969d",
                "name": "lif1",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/interfaces/01056403-1383-bc4b-786a-93e8ea35969d"
                    }
                },
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/056403da-83a7-4b13-bc78-6a93e8ea3596"
                    }
                },
                "uuid": "056403da-83a7-4b13-bc78-6a93e8ea3596",
                "name": "svm1",
            },
            "initiator": {"wwpn": "8b:21:2f:07:00:00:00:00"},
            "_links": {
                "self": {
                    "href": "/api/network/fc/logins/01056403-1383-bc4b-786a-93e8ea35969d/8b%3A21%3A2f%3A07%3A00%3A00%3A00%3A00"
                }
            },
        }
    ),
    FcLogin(
        {
            "interface": {
                "uuid": "02056403-1383-bc4b-786a-93e8ea35969d",
                "name": "lif2",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/interfaces/02056403-1383-bc4b-786a-93e8ea35969d"
                    }
                },
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/056403da-83a7-4b13-bc78-6a93e8ea3596"
                    }
                },
                "uuid": "056403da-83a7-4b13-bc78-6a93e8ea3596",
                "name": "svm1",
            },
            "initiator": {"wwpn": "8c:21:2f:07:00:00:00:00"},
            "_links": {
                "self": {
                    "href": "/api/network/fc/logins/02056403-1383-bc4b-786a-93e8ea35969d/8c%3A21%3A2f%3A07%3A00%3A00%3A00%3A00"
                }
            },
        }
    ),
    FcLogin(
        {
            "interface": {
                "uuid": "03056403-1383-bc4b-786a-93e8ea35969d",
                "name": "lif3",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/interfaces/00056403-1383-bc4b-786a-93e8ea35969d"
                    }
                },
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/156403da-83a7-4b13-bc78-6a93e8ea3596"
                    }
                },
                "uuid": "156403da-83a7-4b13-bc78-6a93e8ea3596",
                "name": "svm2",
            },
            "initiator": {"wwpn": "8a:21:2f:07:00:00:00:00"},
            "_links": {
                "self": {
                    "href": "/api/network/fc/logins/00056403-1383-bc4b-786a-93e8ea35969d/8a%3A21%3A2f%3A07%3A00%3A00%3A00%3A00"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving all FC logins with data protocol _fcp_ in SVM _svm1_
The `svm.name` and `protocol` query parameters are used to perform the query.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcLogin

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcLogin.get_collection(protocol="fcp", **{"svm.name": "svm1"})))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    FcLogin(
        {
            "interface": {
                "uuid": "01056403-1383-bc4b-786a-93e8ea35969d",
                "name": "lif2",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/interfaces/01056403-1383-bc4b-786a-93e8ea35969d"
                    }
                },
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/056403da-83a7-4b13-bc78-6a93e8ea3596"
                    }
                },
                "uuid": "056403da-83a7-4b13-bc78-6a93e8ea3596",
                "name": "svm1",
            },
            "protocol": "fcp",
            "initiator": {"wwpn": "8b:21:2f:07:00:00:00:00"},
            "_links": {
                "self": {
                    "href": "/api/network/fc/logins/01056403-1383-bc4b-786a-93e8ea35969d/8b%3A21%3A2f%3A07%3A00%3A00%3A00%3A00"
                }
            },
        }
    ),
    FcLogin(
        {
            "interface": {
                "uuid": "02056403-1383-bc4b-786a-93e8ea35969d",
                "name": "lif3",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/interfaces/02056403-1383-bc4b-786a-93e8ea35969d"
                    }
                },
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/056403da-83a7-4b13-bc78-6a93e8ea3596"
                    }
                },
                "uuid": "056403da-83a7-4b13-bc78-6a93e8ea3596",
                "name": "svm1",
            },
            "protocol": "fcp",
            "initiator": {"wwpn": "8c:21:2f:07:00:00:00:00"},
            "_links": {
                "self": {
                    "href": "/api/network/fc/logins/02056403-1383-bc4b-786a-93e8ea35969d/8c%3A21%3A2f%3A07%3A00%3A00%3A00%3A00"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving all FC logins for initiators belonging to _igroup1_ and returning all of their properties
The `igroups.name` query parameter is used to perform the query. The `fields` query parameter is used to return all of the properties.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FcLogin

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FcLogin.get_collection(fields="*", **{"igroups.name": "igroup1"})))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    FcLogin(
        {
            "interface": {
                "uuid": "01056403-1383-bc4b-786a-93e8ea35969d",
                "wwpn": "8b:21:2f:07:00:00:00:00",
                "name": "lif2",
                "_links": {
                    "self": {
                        "href": "/api/network/fc/interfaces/01056403-1383-bc4b-786a-93e8ea35969d"
                    }
                },
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/056403da-83a7-4b13-bc78-6a93e8ea3596"
                    }
                },
                "uuid": "056403da-83a7-4b13-bc78-6a93e8ea3596",
                "name": "svm1",
            },
            "protocol": "fcp",
            "initiator": {
                "wwpn": "8b:21:2f:07:00:00:00:00",
                "comment": "Example information about this initiator",
                "wwnn": "95:21:2f:07:00:00:00:00",
            },
            "igroups": [
                {
                    "uuid": "243bbb8a-46e9-4b2d-a508-a62dc93df9d1",
                    "name": "igroup1",
                    "_links": {
                        "self": {
                            "href": "/api/protocols/san/igroups/243bbb8a-46e9-4b2d-a508-a62dc93df9d1"
                        }
                    },
                }
            ],
            "_links": {
                "self": {
                    "href": "/api/network/fc/logins/01056403-1383-bc4b-786a-93e8ea35969d/8b%3A21%3A2f%3A07%3A00%3A00%3A00%3A00"
                }
            },
        }
    )
]

```
</div>
</div>

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


__all__ = ["FcLogin", "FcLoginSchema"]
__pdoc__ = {
    "FcLoginSchema.resource": False,
    "FcLogin.fc_login_show": False,
    "FcLogin.fc_login_create": False,
    "FcLogin.fc_login_modify": False,
    "FcLogin.fc_login_delete": False,
}


class FcLoginSchema(ResourceSchema):
    """The fields of the FcLogin object"""

    links = fields.Nested("netapp_ontap.models.collection_links.CollectionLinksSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the fc_login. """

    igroups = fields.List(fields.Nested("netapp_ontap.resources.igroup.IgroupSchema", unknown=EXCLUDE), data_key="igroups")
    r""" The initiator groups in which the initiator is a member. """

    initiator = fields.Nested("netapp_ontap.models.fc_login_initiator.FcLoginInitiatorSchema", data_key="initiator", unknown=EXCLUDE)
    r""" The initiator field of the fc_login. """

    interface = fields.Nested("netapp_ontap.resources.fc_interface.FcInterfaceSchema", data_key="interface", unknown=EXCLUDE)
    r""" The interface field of the fc_login. """

    protocol = fields.Str(
        data_key="protocol",
        validate=enum_validation(['fc_nvme', 'fcp']),
    )
    r""" The data protocol used to perform the login.


Valid choices:

* fc_nvme
* fcp """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the fc_login. """

    @property
    def resource(self):
        return FcLogin

    gettable_fields = [
        "links",
        "igroups.links",
        "igroups.name",
        "igroups.uuid",
        "initiator",
        "interface.links",
        "interface.name",
        "interface.uuid",
        "interface.wwpn",
        "protocol",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,igroups.links,igroups.name,igroups.uuid,initiator,interface.links,interface.name,interface.uuid,interface.wwpn,protocol,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FcLogin.get_collection(fields=field)]
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
            raise NetAppRestError("FcLogin modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FcLogin(Resource):
    r""" A Fibre Channel (FC) login represents a connection formed by an FC initiator that has successfully logged in to ONTAP. This represents the FC login on which higher-level protocols such as Fibre Channel Protocol and NVMe over Fibre Channel (NVMe/FC) rely. """

    _schema = FcLoginSchema
    _path = "/api/network/fc/logins"
    _keys = ["interface.uuid", "initiator.wwpn"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FC logins.
### Related ONTAP commands
* `vserver fcp initiator show`
### Learn more
* SAN: [`DOC /network/fc/logins`](#docs-SAN-network_fc_logins)
* NVMe: [`DOC /network/fc/logins`](#docs-NVMe-network_fc_logins)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fc login show")
        def fc_login_show(
            fields: List[Choices.define(["protocol", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FcLogin resources

            Args:
                protocol: The data protocol used to perform the login. 
            """

            kwargs = {}
            if protocol is not None:
                kwargs["protocol"] = protocol
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FcLogin.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FcLogin resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FC logins.
### Related ONTAP commands
* `vserver fcp initiator show`
### Learn more
* SAN: [`DOC /network/fc/logins`](#docs-SAN-network_fc_logins)
* NVMe: [`DOC /network/fc/logins`](#docs-NVMe-network_fc_logins)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an FC login.
### Related ONTAP commands
* `vserver fcp initiator show`
### Learn more
* SAN: [`DOC /network/fc/logins`](#docs-SAN-network_fc_logins)
* NVMe: [`DOC /network/fc/logins`](#docs-NVMe-network_fc_logins)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





