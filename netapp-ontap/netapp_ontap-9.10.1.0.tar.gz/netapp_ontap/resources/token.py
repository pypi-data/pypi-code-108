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


__all__ = ["Token", "TokenSchema"]
__pdoc__ = {
    "TokenSchema.resource": False,
    "Token.token_show": False,
    "Token.token_create": False,
    "Token.token_modify": False,
    "Token.token_delete": False,
}


class TokenSchema(ResourceSchema):
    """The fields of the Token object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the token. """

    expiry_time = fields.Nested("netapp_ontap.models.token_expiry_time.TokenExpiryTimeSchema", data_key="expiry_time", unknown=EXCLUDE)
    r""" The expiry_time field of the token. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the token. """

    reserve_size = Size(
        data_key="reserve_size",
    )
    r""" Specifies the available reserve in the file clone split load for the given token. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Token UUID. """

    @property
    def resource(self):
        return Token

    gettable_fields = [
        "links",
        "expiry_time",
        "node.links",
        "node.name",
        "node.uuid",
        "reserve_size",
        "uuid",
    ]
    """links,expiry_time,node.links,node.name,node.uuid,reserve_size,uuid,"""

    patchable_fields = [
        "expiry_time",
        "node.name",
        "node.uuid",
    ]
    """expiry_time,node.name,node.uuid,"""

    postable_fields = [
        "expiry_time",
        "node.name",
        "node.uuid",
        "reserve_size",
    ]
    """expiry_time,node.name,node.uuid,reserve_size,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Token.get_collection(fields=field)]
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
            raise NetAppRestError("Token modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Token(Resource):
    r""" token """

    _schema = TokenSchema
    _path = "/api/storage/file/clone/tokens"
    _keys = ["node.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves information for the specified token.
### Related Ontap command
* `volume file clone token show`
### Learn More
* [`DOC /storage/file/clone`]
### Retrieving information on clone tokens
```
# The API:
/api/storage/file/clone/tokens
# The call:
curl -X GET "https://<mgmt_ip>/api/storage/file/clone/tokens" -H "accept: application/hal+json"
# The response:
{
  "records": [
    {
      "node": {
        "uuid": "97255711-a1ad-11eb-92b2-0050568eb2ca",
        "name": "node1",
        "_links": {
          "self": {
            "href": "/api/cluster/nodes/97255711-a1ad-11eb-92b2-0050568eb2ca"
          }
        }
      },
      "uuid": "905c42ce-a74b-11eb-bd86-0050568ec7ae",
      "reserve_size": 10240,
      "expiry_time": {
        "limit": "PT1H10M",
        "left": "PT1H9M"
      },
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/905c42ce-a74b-11eb-bd86-0050568ec7ae"
        }
      }
    }
  ],
  "num_records": 1,
  "_links": {
    "self": {
      "href": "/api/storage/file/clone/tokens"
    }
  }
}
```
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="token show")
        def token_show(
            fields: List[Choices.define(["reserve_size", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Token resources

            Args:
                reserve_size: Specifies the available reserve in the file clone split load for the given token.
                uuid: Token UUID.
            """

            kwargs = {}
            if reserve_size is not None:
                kwargs["reserve_size"] = reserve_size
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Token.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Token resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Token"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a file clone token.
### Related Ontap commands
* `volume file clone token modify`
### Modify clone token
Use the PATCH API to update the expiry time associated with the clone token.<br\>
```
# The call:
curl -X PATCH "https://<mgmt_ip>/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/905c42ce-a74b-11eb-bd86-0050568ec7ae" -d '{"expiry_time": {"limit": "5400"} }'
# The response for successful PATCH is empty.
```
### Learn More
* [`DOC /storage/file/clone`]
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Token"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Token"], NetAppResponse]:
        r"""Creates a new token to reserve the split load.
### Required Properties
* `node.uuid`
* `reserve-size`
### Optional Propeties
* `expiry_time.limit`
* `expiry_time.left`
### Related Ontap Commands
* `volume file clone token create`
### Learn More
* [`DOC /storage/file/clone`]
### Creating clone tokens to reserve space for clone creation on the node
There is a limit on the amount of clone data that can undergo a split at a point of time on the node (clone split load). Clone tokens are used to reserve space from clone split load for clone creation. The POST operation is used to create clone tokens with `reserve-size` and `expiry-time.limit` in the body.<br\>
```
# The API
/api/storage/file/clone/tokens
# The call
curl -X POST "https://<mgmt_ip>/api/storage/file/clone/tokens" -H "accept: application/hal+json" -d '{"node": {"uuid": "97255711-a1ad-11eb-92b2-0050568eb2ca"}, "reserve_size": "40M", "expiry_time": { "limit": "4200"} }'
# The response
{
  "num_records": 1,
  "records": [
    {
      "node": {
        "name": "node1"
      },
      "uuid": "286f6ae4-c94d-11eb-adb5-005056bbeb0b",
      "reserve_size": 41943040,
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca"
        }
      }
    }
  ]
}
```
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["Token"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific file clone token.
### Related Ontap command
* `volume file clone token delete`
### Delete specific clone token.
```
# The API:
/api/storage/file/clone/tokens/{node.uuid}/{token.uuid}
# The call:
curl -X DELETE "https://<mgmt_ip>/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/909c42ce-a74b-11eb-bd86-0050568ec7ae"
# The successful response is empty body.
```
### Learn More
* [`DOC /storage/file/clone`]
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves information for the specified token.
### Related Ontap command
* `volume file clone token show`
### Learn More
* [`DOC /storage/file/clone`]
### Retrieving information on clone tokens
```
# The API:
/api/storage/file/clone/tokens
# The call:
curl -X GET "https://<mgmt_ip>/api/storage/file/clone/tokens" -H "accept: application/hal+json"
# The response:
{
  "records": [
    {
      "node": {
        "uuid": "97255711-a1ad-11eb-92b2-0050568eb2ca",
        "name": "node1",
        "_links": {
          "self": {
            "href": "/api/cluster/nodes/97255711-a1ad-11eb-92b2-0050568eb2ca"
          }
        }
      },
      "uuid": "905c42ce-a74b-11eb-bd86-0050568ec7ae",
      "reserve_size": 10240,
      "expiry_time": {
        "limit": "PT1H10M",
        "left": "PT1H9M"
      },
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/905c42ce-a74b-11eb-bd86-0050568ec7ae"
        }
      }
    }
  ],
  "num_records": 1,
  "_links": {
    "self": {
      "href": "/api/storage/file/clone/tokens"
    }
  }
}
```
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a file clone token
### Related Ontap command
* `volume file clone token show`
### Retrieve information for single token.
```
# The call:
curl -X GET "https://<mgmt_ip>/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/905c42ce-a74b-11eb-bd86-0050568ec7ae"
# The response:
{
  "node": {
    "uuid": "97255711-a1ad-11eb-92b2-0050568eb2ca",
    "name": "node1",
    "_links": {
      "self": {
        "href": "/api/cluster/nodes/97255711-a1ad-11eb-92b2-0050568eb2ca"
      }
    }
  },
  "uuid": "905c42ce-a74b-11eb-bd86-0050568ec7ae",
  "reserve_size": 41943040,
  "expiry_time": {
    "limit": "PT1H10M",
    "left": "PT1H9M"
  },
  "_links": {
    "self": {
      "href": "/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/905c42ce-a74b-11eb-bd86-0050568ec7ae"
    }
  }
}
```
### Learn More
* [`DOC /storage/file/clone`]
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a new token to reserve the split load.
### Required Properties
* `node.uuid`
* `reserve-size`
### Optional Propeties
* `expiry_time.limit`
* `expiry_time.left`
### Related Ontap Commands
* `volume file clone token create`
### Learn More
* [`DOC /storage/file/clone`]
### Creating clone tokens to reserve space for clone creation on the node
There is a limit on the amount of clone data that can undergo a split at a point of time on the node (clone split load). Clone tokens are used to reserve space from clone split load for clone creation. The POST operation is used to create clone tokens with `reserve-size` and `expiry-time.limit` in the body.<br\>
```
# The API
/api/storage/file/clone/tokens
# The call
curl -X POST "https://<mgmt_ip>/api/storage/file/clone/tokens" -H "accept: application/hal+json" -d '{"node": {"uuid": "97255711-a1ad-11eb-92b2-0050568eb2ca"}, "reserve_size": "40M", "expiry_time": { "limit": "4200"} }'
# The response
{
  "num_records": 1,
  "records": [
    {
      "node": {
        "name": "node1"
      },
      "uuid": "286f6ae4-c94d-11eb-adb5-005056bbeb0b",
      "reserve_size": 41943040,
      "_links": {
        "self": {
          "href": "/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca"
        }
      }
    }
  ]
}
```
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="token create")
        async def token_create(
        ) -> ResourceTable:
            """Create an instance of a Token resource

            Args:
                links: 
                expiry_time: 
                node: 
                reserve_size: Specifies the available reserve in the file clone split load for the given token.
                uuid: Token UUID.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if expiry_time is not None:
                kwargs["expiry_time"] = expiry_time
            if node is not None:
                kwargs["node"] = node
            if reserve_size is not None:
                kwargs["reserve_size"] = reserve_size
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = Token(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Token: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a file clone token.
### Related Ontap commands
* `volume file clone token modify`
### Modify clone token
Use the PATCH API to update the expiry time associated with the clone token.<br\>
```
# The call:
curl -X PATCH "https://<mgmt_ip>/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/905c42ce-a74b-11eb-bd86-0050568ec7ae" -d '{"expiry_time": {"limit": "5400"} }'
# The response for successful PATCH is empty.
```
### Learn More
* [`DOC /storage/file/clone`]
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="token modify")
        async def token_modify(
        ) -> ResourceTable:
            """Modify an instance of a Token resource

            Args:
                reserve_size: Specifies the available reserve in the file clone split load for the given token.
                query_reserve_size: Specifies the available reserve in the file clone split load for the given token.
                uuid: Token UUID.
                query_uuid: Token UUID.
            """

            kwargs = {}
            changes = {}
            if query_reserve_size is not None:
                kwargs["reserve_size"] = query_reserve_size
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if reserve_size is not None:
                changes["reserve_size"] = reserve_size
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(Token, "find"):
                resource = Token.find(
                    **kwargs
                )
            else:
                resource = Token()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Token: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific file clone token.
### Related Ontap command
* `volume file clone token delete`
### Delete specific clone token.
```
# The API:
/api/storage/file/clone/tokens/{node.uuid}/{token.uuid}
# The call:
curl -X DELETE "https://<mgmt_ip>/api/storage/file/clone/tokens/97255711-a1ad-11eb-92b2-0050568eb2ca/909c42ce-a74b-11eb-bd86-0050568ec7ae"
# The successful response is empty body.
```
### Learn More
* [`DOC /storage/file/clone`]
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="token delete")
        async def token_delete(
        ) -> None:
            """Delete an instance of a Token resource

            Args:
                reserve_size: Specifies the available reserve in the file clone split load for the given token.
                uuid: Token UUID.
            """

            kwargs = {}
            if reserve_size is not None:
                kwargs["reserve_size"] = reserve_size
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(Token, "find"):
                resource = Token.find(
                    **kwargs
                )
            else:
                resource = Token()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Token: %s" % err)


