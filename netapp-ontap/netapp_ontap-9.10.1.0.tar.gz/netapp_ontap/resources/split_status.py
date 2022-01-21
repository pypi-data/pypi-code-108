r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


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


__all__ = ["SplitStatus", "SplitStatusSchema"]
__pdoc__ = {
    "SplitStatusSchema.resource": False,
    "SplitStatus.split_status_show": False,
    "SplitStatus.split_status_create": False,
    "SplitStatus.split_status_modify": False,
    "SplitStatus.split_status_delete": False,
}


class SplitStatusSchema(ResourceSchema):
    """The fields of the SplitStatus object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the split_status. """

    pending_splits = Size(
        data_key="pending_splits",
    )
    r""" Specifies the number of pending file clone split operations in the volume. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the split_status. """

    unsplit_clone_size = Size(
        data_key="unsplit_clone_size",
    )
    r""" Specifies the space occupied by unsplit file clones in the volume. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the split_status. """

    @property
    def resource(self):
        return SplitStatus

    gettable_fields = [
        "links",
        "pending_splits",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "unsplit_clone_size",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,pending_splits,svm.links,svm.name,svm.uuid,unsplit_clone_size,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """svm.name,svm.uuid,volume.name,volume.uuid,"""

    postable_fields = [
        "svm.name",
        "svm.uuid",
        "volume.name",
        "volume.uuid",
    ]
    """svm.name,svm.uuid,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SplitStatus.get_collection(fields=field)]
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
            raise NetAppRestError("SplitStatus modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SplitStatus(Resource):
    """Allows interaction with SplitStatus objects on the host"""

    _schema = SplitStatusSchema
    _path = "/api/storage/file/clone/split-status"
    _keys = ["volume.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves file clone split status of all volumes in the node.
### Learn More
* [`DOC /storage/file/clone`]
```
# The API:
/api/storage/file/clone/split-status
# The call:
curl -X GET "https://<mgmt_ip>/api/storage/file/clone/split-status" -H "accept: application/hal+json"
# The response:
{
  "records": [
    {
      "volume": {
        "uuid": "ac559964-57a3-40cf-b5cb-f3cb99151a7d",
        "name": "vol1",
        "_links": {
          "self": {
            "href": "/api/storage/volumes/ac559964-57a3-40cf-b5cb-f3cb99151a7d"
          }
        }
      },
      "svm": {
        "name": "vs1"
      },
      "pending_splits": 0,
      "unsplit_clone_size": 0,
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/split-status/ac559964-57a3-40cf-b5cb-f3cb99151a7d"
        }
      }
    },
    {
      "volume": {
        "uuid": "32d95d48-d8b7-11eb-a41d-005056bb3837",
        "name": "vs1_root",
        "_links": {
          "self": {
            "href": "/api/storage/volumes/32d95d48-d8b7-11eb-a41d-005056bb3837"
          }
        }
      },
      "svm": {
        "name": "vs1"
      },
      "pending_splits": 0,
      "unsplit_clone_size": 0,
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/split-status/32d95d48-d8b7-11eb-a41d-005056bb3837"
        }
      }
    }
  ],
  "num_records": 2,
  "_links": {
    "self": {
      "href": "/api/storage/file/clone/split-status"
    }
  }
}
```
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="split status show")
        def split_status_show(
            fields: List[Choices.define(["pending_splits", "unsplit_clone_size", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SplitStatus resources

            Args:
                pending_splits: Specifies the number of pending file clone split operations in the volume.
                unsplit_clone_size: Specifies the space occupied by unsplit file clones in the volume.
            """

            kwargs = {}
            if pending_splits is not None:
                kwargs["pending_splits"] = pending_splits
            if unsplit_clone_size is not None:
                kwargs["unsplit_clone_size"] = unsplit_clone_size
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SplitStatus.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SplitStatus resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves file clone split status of all volumes in the node.
### Learn More
* [`DOC /storage/file/clone`]
```
# The API:
/api/storage/file/clone/split-status
# The call:
curl -X GET "https://<mgmt_ip>/api/storage/file/clone/split-status" -H "accept: application/hal+json"
# The response:
{
  "records": [
    {
      "volume": {
        "uuid": "ac559964-57a3-40cf-b5cb-f3cb99151a7d",
        "name": "vol1",
        "_links": {
          "self": {
            "href": "/api/storage/volumes/ac559964-57a3-40cf-b5cb-f3cb99151a7d"
          }
        }
      },
      "svm": {
        "name": "vs1"
      },
      "pending_splits": 0,
      "unsplit_clone_size": 0,
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/split-status/ac559964-57a3-40cf-b5cb-f3cb99151a7d"
        }
      }
    },
    {
      "volume": {
        "uuid": "32d95d48-d8b7-11eb-a41d-005056bb3837",
        "name": "vs1_root",
        "_links": {
          "self": {
            "href": "/api/storage/volumes/32d95d48-d8b7-11eb-a41d-005056bb3837"
          }
        }
      },
      "svm": {
        "name": "vs1"
      },
      "pending_splits": 0,
      "unsplit_clone_size": 0,
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/split-status/32d95d48-d8b7-11eb-a41d-005056bb3837"
        }
      }
    }
  ],
  "num_records": 2,
  "_links": {
    "self": {
      "href": "/api/storage/file/clone/split-status"
    }
  }
}
```
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves file clone split status of all volumes in the node.
### Related Ontap commands
* `volume file clone split status`
### Learn More
* [`DOC /storage/file/clone`]
### Retrieves the information of split status.
The GET operation retrieves information about split processes in the volume.<br\>
`pending-clone-splits` is the number of files for which file clone split is not yet completed.<br\>
`unsplit-size` is the sum of all sizes, in bytes in the volume that is not split.<br\>
```
# The API:
/api/storage/file/clone/split-status/{volume.uuid}
# The call:
curl -X GET "https://<mgmt_ip>/api/storage/file/clone/split-status/ac559964-57a3-40cf-b5cb-f3cb99151a7d" -H "accept: application/hal+json"
# The response:
{
  "volume": {
    "uuid": "ac559964-57a3-40cf-b5cb-f3cb99151a7d",
    "name": "vol1",
    "_links": {
      "self": {
        "href": "/api/storage/volumes/ac559964-57a3-40cf-b5cb-f3cb99151a7d"
      }
    }
  },
  "svm": {
    "name": "vs1"
  },
  "pending_splits": 0,
  "unsplit_clone_size": 0,
  "_links": {
    "self": {
      "href": "/api/storage/file/clone/split-status/ac559964-57a3-40cf-b5cb-f3cb99151a7d"
    }
  }
}
```
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





