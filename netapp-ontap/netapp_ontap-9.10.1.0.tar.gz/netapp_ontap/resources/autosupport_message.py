r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Use this API to invoke and retrieve AutoSupport messages from the nodes in the cluster.<p/>
This API supports POST and GET calls. Use a POST call to invoke AutoSupport and a GET call to retrieve AutoSupport messages.
---
## Examples
### Invoking an AutoSupport on all nodes in the cluster
The following example invokes an AutoSupport on every node in the cluster.
Note that AutoSupport is invoked on all nodes in the cluster if the `node` parameter is omitted. Also, note that the `subject` line is the same when invoking on all nodes.<p/>
By default, the response is an empty object. If `return_records=true` is passed in the request, the response includes information about the node and the index of the invoked AutoSupport message.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutosupportMessage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutosupportMessage()
    resource.message = "test_msg"
    resource.type = "all"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
AutosupportMessage(
    {
        "index": 4,
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/092e0298-f250-11e8-9a05-005056bb6666"
                }
            },
            "uuid": "092e0298-f250-11e8-9a05-005056bb6666",
            "name": "node1",
        },
    }
)

```
</div>
</div>

---
### Invoking an AutoSupport on a single node
The following examples invoke an AutoSupport on a single node in the cluster.
Note that AutoSupport is invoked on all nodes in the cluster if the `node` parameter is omitted. You can specify the node-name with either `node` or `node.name` parameter. You can also specify UUID of the node with the `node.uuid` parameter.<p/>
By default, the response is an empty object. If `return_records=true` is passed in the request, the response includes information about the node and the index of the invoked AutoSupport message.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutosupportMessage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutosupportMessage()
    resource.message = "test_msg"
    resource.type = "test"
    resource.node = {"name": "node1"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
AutosupportMessage(
    {
        "index": 8,
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/092e0298-f250-11e8-9a05-005056bb6666"
                }
            },
            "uuid": "092e0298-f250-11e8-9a05-005056bb6666",
            "name": "node1",
        },
    }
)

```
</div>
</div>

```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutosupportMessage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutosupportMessage()
    resource.message = "test_msg"
    resource.type = "test"
    resource.node.name = "node2"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
AutosupportMessage(
    {
        "index": 4,
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/e47d2630-f250-11e8-b186-005056bb5cab"
                }
            },
            "uuid": "e47d2630-f250-11e8-b186-005056bb5cab",
            "name": "node2",
        },
    }
)

```
</div>
</div>

```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutosupportMessage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutosupportMessage()
    resource.message = "test_msg"
    resource.type = "test"
    resource.node.uuid = "092e0298-f250-11e8-9a05-005056bb6666"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
AutosupportMessage(
    {
        "index": 5,
        "node": {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/092e0298-f250-11e8-9a05-005056bb6666"
                }
            },
            "uuid": "092e0298-f250-11e8-9a05-005056bb6666",
            "name": "node1",
        },
    }
)

```
</div>
</div>

---
### Retrieving AutoSupport messages from all nodes in the cluster
The following example retrieves AutoSupport messages from every node in the cluster.
Note that if the <i>fields=*</i> parameter is not specified, only node, index, and destination fields are returned.
Filters can be added on the fields to limit the results.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutosupportMessage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(AutosupportMessage.get_collection(fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
[
    AutosupportMessage(
        {
            "destination": "smtp",
            "generated_on": "2019-03-28T10:18:04-04:00",
            "state": "ignore",
            "index": 1,
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/092e0298-f250-11e8-9a05-005056bb6666"
                    }
                },
                "uuid": "092e0298-f250-11e8-9a05-005056bb6666",
                "name": "node1",
            },
            "subject": "USER_TRIGGERED (TEST:test_msg)",
        }
    ),
    AutosupportMessage(
        {
            "destination": "http",
            "generated_on": "2019-03-28T10:18:04-04:00",
            "state": "sent_successful",
            "index": 1,
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/092e0298-f250-11e8-9a05-005056bb6666"
                    }
                },
                "uuid": "092e0298-f250-11e8-9a05-005056bb6666",
                "name": "node1",
            },
            "subject": "USER_TRIGGERED (TEST:test_msg)",
        }
    ),
    AutosupportMessage(
        {
            "destination": "noteto",
            "generated_on": "2019-03-28T10:18:04-04:00",
            "state": "ignore",
            "index": 1,
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/092e0298-f250-11e8-9a05-005056bb6666"
                    }
                },
                "uuid": "092e0298-f250-11e8-9a05-005056bb6666",
                "name": "node1",
            },
            "subject": "USER_TRIGGERED (TEST:test_msg)",
        }
    ),
    AutosupportMessage(
        {
            "destination": "smtp",
            "generated_on": "2019-03-28T10:18:06-04:00",
            "state": "ignore",
            "index": 1,
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/e47d2630-f250-11e8-b186-005056bb5cab"
                    }
                },
                "uuid": "e47d2630-f250-11e8-b186-005056bb5cab",
                "name": "node2",
            },
            "subject": "USER_TRIGGERED (TEST:test_msg)",
        }
    ),
    AutosupportMessage(
        {
            "destination": "http",
            "generated_on": "2019-03-28T10:18:06-04:00",
            "state": "sent_successful",
            "index": 1,
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/e47d2630-f250-11e8-b186-005056bb5cab"
                    }
                },
                "uuid": "e47d2630-f250-11e8-b186-005056bb5cab",
                "name": "node2",
            },
            "subject": "USER_TRIGGERED (TEST:test_msg)",
        }
    ),
    AutosupportMessage(
        {
            "destination": "noteto",
            "generated_on": "2019-03-28T10:18:06-04:00",
            "state": "ignore",
            "index": 1,
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/e47d2630-f250-11e8-b186-005056bb5cab"
                    }
                },
                "uuid": "e47d2630-f250-11e8-b186-005056bb5cab",
                "name": "node2",
            },
            "subject": "USER_TRIGGERED (TEST:test_msg)",
        }
    ),
]

```
</div>
</div>

---
### Retrieving AutoSupport messages from a specific node and has 'sent_succesful' state
The following example retrieves AutoSupport messages from a specific node in the cluster.
Note that if the `fields=*` parameter is not specified, only node, index, and destination fields are returned.
This example uses a filter on the `node.name` and `state` fields. You can add filters to any fields in the response.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutosupportMessage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            AutosupportMessage.get_collection(
                state="sent_successful",
                fields="*",
                return_timeout=15,
                **{"node.name": "node1"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
[
    AutosupportMessage(
        {
            "destination": "http",
            "generated_on": "2019-03-28T10:18:04-04:00",
            "state": "sent_successful",
            "index": 1,
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/092e0298-f250-11e8-9a05-005056bb6666"
                    }
                },
                "uuid": "092e0298-f250-11e8-9a05-005056bb6666",
                "name": "node1",
            },
            "subject": "USER_TRIGGERED (TEST:test_msg)",
        }
    )
]

```
</div>
</div>

---
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


__all__ = ["AutosupportMessage", "AutosupportMessageSchema"]
__pdoc__ = {
    "AutosupportMessageSchema.resource": False,
    "AutosupportMessage.autosupport_message_show": False,
    "AutosupportMessage.autosupport_message_create": False,
    "AutosupportMessage.autosupport_message_modify": False,
    "AutosupportMessage.autosupport_message_delete": False,
}


class AutosupportMessageSchema(ResourceSchema):
    """The fields of the AutosupportMessage object"""

    destination = fields.Str(
        data_key="destination",
        validate=enum_validation(['smtp', 'http', 'noteto', 'retransmit']),
    )
    r""" Destination for the AutoSupport

Valid choices:

* smtp
* http
* noteto
* retransmit """

    error = fields.Nested("netapp_ontap.models.autosupport_message_error.AutosupportMessageErrorSchema", data_key="error", unknown=EXCLUDE)
    r""" The error field of the autosupport_message. """

    generated_on = ImpreciseDateTime(
        data_key="generated_on",
    )
    r""" Date and Time of AutoSupport generation in ISO-8601 format

Example: 2019-03-25T21:30:04.000+0000 """

    index = Size(
        data_key="index",
    )
    r""" Sequence number of the AutoSupport

Example: 9 """

    message = fields.Str(
        data_key="message",
    )
    r""" Message included in the AutoSupport subject

Example: invoked_test_autosupport_rest """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the autosupport_message. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['initializing', 'collection_failed', 'collection_in_progress', 'queued', 'transmitting', 'sent_successful', 'ignore', 're_queued', 'transmission_failed', 'ondemand_ignore', 'cancelled']),
    )
    r""" State of AutoSupport delivery

Valid choices:

* initializing
* collection_failed
* collection_in_progress
* queued
* transmitting
* sent_successful
* ignore
* re_queued
* transmission_failed
* ondemand_ignore
* cancelled """

    subject = fields.Str(
        data_key="subject",
    )
    r""" Subject line for the AutoSupport

Example: WEEKLY_LOG """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['test', 'performance', 'all']),
    )
    r""" Type of AutoSupport collection to issue

Valid choices:

* test
* performance
* all """

    uri = fields.Str(
        data_key="uri",
    )
    r""" Alternate destination for the AutoSupport

Example: http://1.2.3.4/delivery_uri """

    @property
    def resource(self):
        return AutosupportMessage

    gettable_fields = [
        "destination",
        "error",
        "generated_on",
        "index",
        "node.links",
        "node.name",
        "node.uuid",
        "state",
        "subject",
    ]
    """destination,error,generated_on,index,node.links,node.name,node.uuid,state,subject,"""

    patchable_fields = [
        "error",
    ]
    """error,"""

    postable_fields = [
        "error",
        "message",
        "node.name",
        "node.uuid",
        "type",
        "uri",
    ]
    """error,message,node.name,node.uuid,type,uri,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in AutosupportMessage.get_collection(fields=field)]
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
            raise NetAppRestError("AutosupportMessage modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class AutosupportMessage(Resource):
    """Allows interaction with AutosupportMessage objects on the host"""

    _schema = AutosupportMessageSchema
    _path = "/api/support/autosupport/messages"

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves AutoSupport message history from all nodes in the cluster.<p/>
There can be a short delay on invoked AutoSupport messages showing in history, dependent on processing of other AutoSupports in the queue.
### Related ONTAP commands
* `system node autosupport history show`
### Learn more
* [`DOC /support/autosupport/messages`](#docs-support-support_autosupport_messages)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="autosupport message show")
        def autosupport_message_show(
            fields: List[Choices.define(["destination", "generated_on", "index", "message", "state", "subject", "type", "uri", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of AutosupportMessage resources

            Args:
                destination: Destination for the AutoSupport
                generated_on: Date and Time of AutoSupport generation in ISO-8601 format
                index: Sequence number of the AutoSupport
                message: Message included in the AutoSupport subject
                state: State of AutoSupport delivery
                subject: Subject line for the AutoSupport
                type: Type of AutoSupport collection to issue
                uri: Alternate destination for the AutoSupport
            """

            kwargs = {}
            if destination is not None:
                kwargs["destination"] = destination
            if generated_on is not None:
                kwargs["generated_on"] = generated_on
            if index is not None:
                kwargs["index"] = index
            if message is not None:
                kwargs["message"] = message
            if state is not None:
                kwargs["state"] = state
            if subject is not None:
                kwargs["subject"] = subject
            if type is not None:
                kwargs["type"] = type
            if uri is not None:
                kwargs["uri"] = uri
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return AutosupportMessage.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all AutosupportMessage resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["AutosupportMessage"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["AutosupportMessage"], NetAppResponse]:
        r"""Creates and sends an AutoSupport message with the provided input parameters.<p/>
Important note:
* By default, the response is an empty object. If `return_records=true` is passed in the request, the response includes information about the node and the index of the invoked AutoSupport message.
### Recommended optional properties
* `message` - Message included in the AutoSupport subject. Use this to identify the generated AutoSupport message.
### Default property values
If not specified in POST, the following are the default property values:
* `type` - _all_
* `node.name` or `node.uuid` - Not specifying these properties invokes AutoSupport on all nodes in the cluster.
### Related ONTAP commands
* `system node autosupport invoke`
### Learn more
* [`DOC /support/autosupport/messages`](#docs-support-support_autosupport_messages)
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)


    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves AutoSupport message history from all nodes in the cluster.<p/>
There can be a short delay on invoked AutoSupport messages showing in history, dependent on processing of other AutoSupports in the queue.
### Related ONTAP commands
* `system node autosupport history show`
### Learn more
* [`DOC /support/autosupport/messages`](#docs-support-support_autosupport_messages)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)


    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates and sends an AutoSupport message with the provided input parameters.<p/>
Important note:
* By default, the response is an empty object. If `return_records=true` is passed in the request, the response includes information about the node and the index of the invoked AutoSupport message.
### Recommended optional properties
* `message` - Message included in the AutoSupport subject. Use this to identify the generated AutoSupport message.
### Default property values
If not specified in POST, the following are the default property values:
* `type` - _all_
* `node.name` or `node.uuid` - Not specifying these properties invokes AutoSupport on all nodes in the cluster.
### Related ONTAP commands
* `system node autosupport invoke`
### Learn more
* [`DOC /support/autosupport/messages`](#docs-support-support_autosupport_messages)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="autosupport message create")
        async def autosupport_message_create(
        ) -> ResourceTable:
            """Create an instance of a AutosupportMessage resource

            Args:
                destination: Destination for the AutoSupport
                error: 
                generated_on: Date and Time of AutoSupport generation in ISO-8601 format
                index: Sequence number of the AutoSupport
                message: Message included in the AutoSupport subject
                node: 
                state: State of AutoSupport delivery
                subject: Subject line for the AutoSupport
                type: Type of AutoSupport collection to issue
                uri: Alternate destination for the AutoSupport
            """

            kwargs = {}
            if destination is not None:
                kwargs["destination"] = destination
            if error is not None:
                kwargs["error"] = error
            if generated_on is not None:
                kwargs["generated_on"] = generated_on
            if index is not None:
                kwargs["index"] = index
            if message is not None:
                kwargs["message"] = message
            if node is not None:
                kwargs["node"] = node
            if state is not None:
                kwargs["state"] = state
            if subject is not None:
                kwargs["subject"] = subject
            if type is not None:
                kwargs["type"] = type
            if uri is not None:
                kwargs["uri"] = uri

            resource = AutosupportMessage(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create AutosupportMessage: %s" % err)
            return [resource]




