r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to display and manage the login messages configuration. The GET request retrieves all of the login messages in the cluster. GET operations on /security/login/messages/{uuid} retrieve the login messages configuration by UUID. PATCH operations on /security/login/messages/{uuid} update the login messages configuration by UUID.
<br />
---
## Examples
### Retrieving all of the login messages in the cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LoginMessages.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LoginMessages(
        {
            "banner": "*** WARNING: DO NOT PROCEED IF YOU ARE NOT AUTHORIZED! ****\n",
            "message": "#### Welcome to Cluster X ####\n",
            "_links": {
                "self": {
                    "href": "/api/security/login/messages/2581e5aa-9fe3-11e8-b309-005056bbef18"
                }
            },
            "scope": "cluster",
            "uuid": "2581e5aa-9fe3-11e8-b309-005056bbef18",
            "show_cluster_message": True,
        }
    ),
    LoginMessages(
        {
            "message": "#### Welcome to SVM1 ####\n",
            "_links": {
                "self": {
                    "href": "/api/security/login/messages/7b1b3715-9ffa-11e8-a5dd-005056bbef18"
                }
            },
            "scope": "svm",
            "svm": {"uuid": "7b1b3715-9ffa-11e8-a5dd-005056bbef18", "name": "svm1"},
            "uuid": "7b1b3715-9ffa-11e8-a5dd-005056bbef18",
            "show_cluster_message": True,
        }
    ),
    LoginMessages(
        {
            "banner": "*** WARNING: This system is for the use of authorized users only. ****\n",
            "_links": {
                "self": {
                    "href": "/api/security/login/messages/8ddee11e-a58c-11e8-85e0-005056bbef18"
                }
            },
            "scope": "svm",
            "svm": {"uuid": "8ddee11e-a58c-11e8-85e0-005056bbef18", "name": "svm3"},
            "uuid": "8ddee11e-a58c-11e8-85e0-005056bbef18",
        }
    ),
    LoginMessages(
        {
            "_links": {
                "self": {
                    "href": "/api/security/login/messages/f7e41c99-9ffa-11e8-a5dd-005056bbef18"
                }
            },
            "scope": "svm",
            "svm": {"uuid": "f7e41c99-9ffa-11e8-a5dd-005056bbef18", "name": "svm2"},
            "uuid": "f7e41c99-9ffa-11e8-a5dd-005056bbef18",
        }
    ),
]

```
</div>
</div>

---
### Retrieving the login messages configuration at the cluster scope
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LoginMessages.get_collection(scope="cluster", fields="*")))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    LoginMessages(
        {
            "banner": "*** WARNING: DO NOT PROCEED IF YOU ARE NOT AUTHORIZED! ****\n",
            "message": "#### Welcome to Cluster X ####\n",
            "_links": {
                "self": {
                    "href": "/api/security/login/messages/2581e5aa-9fe3-11e8-b309-005056bbef18"
                }
            },
            "scope": "cluster",
            "uuid": "2581e5aa-9fe3-11e8-b309-005056bbef18",
            "show_cluster_message": True,
        }
    )
]

```
</div>
</div>

---
### Retrieving the login banner configured at the cluster scope
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LoginMessages.get_collection(scope="cluster", fields="banner")))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    LoginMessages(
        {
            "banner": "*** WARNING: DO NOT PROCEED IF YOU ARE NOT AUTHORIZED! ****\n",
            "_links": {
                "self": {
                    "href": "/api/security/login/messages/2581e5aa-9fe3-11e8-b309-005056bbef18"
                }
            },
            "scope": "cluster",
            "uuid": "2581e5aa-9fe3-11e8-b309-005056bbef18",
        }
    )
]

```
</div>
</div>

---
### Retrieving the login messages configuration of a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LoginMessages.get_collection(fields="*", **{"svm.name": "svm1"})))

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    LoginMessages(
        {
            "message": "#### Welcome to SVM1 ####\n",
            "_links": {
                "self": {
                    "href": "/api/security/login/messages/7b1b3715-9ffa-11e8-a5dd-005056bbef18"
                }
            },
            "scope": "svm",
            "svm": {"uuid": "7b1b3715-9ffa-11e8-a5dd-005056bbef18", "name": "svm1"},
            "uuid": "7b1b3715-9ffa-11e8-a5dd-005056bbef18",
            "show_cluster_message": True,
        }
    )
]

```
</div>
</div>

---
### Retrieving the login messages configuration by UUID, including all fields
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LoginMessages(uuid="7b1b3715-9ffa-11e8-a5dd-005056bbef18")
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
LoginMessages(
    {
        "message": "#### Welcome to SVM1 ####\n",
        "_links": {
            "self": {
                "href": "/api/security/login/messages/7b1b3715-9ffa-11e8-a5dd-005056bbef18"
            }
        },
        "scope": "svm",
        "svm": {"uuid": "7b1b3715-9ffa-11e8-a5dd-005056bbef18", "name": "svm1"},
        "uuid": "7b1b3715-9ffa-11e8-a5dd-005056bbef18",
        "show_cluster_message": True,
    }
)

```
</div>
</div>

---
### Configuring the login banner in a cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LoginMessages()
    resource.banner = "You are entering secure area."
    resource.patch(hydrate=True, scope="cluster")

```

---
### Configuring the message of the day (MOTD) in a cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LoginMessages()
    resource.message = "Welcome to Cluster X"
    resource.show_cluster_message = True
    resource.patch(hydrate=True, scope="cluster")

```

---
### Clearing the login banner and message of the day (MOTD) in a cluster
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LoginMessages()
    resource.banner = ""
    resource.message = ""
    resource.patch(hydrate=True, scope="cluster")

```

---
### Configuring the login messages for a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LoginMessages()
    resource.banner = "AUTHORIZED ACCESS ONLY"
    resource.message = "WELCOME!"
    resource.patch(hydrate=True, **{"svm.name": "svm1"})

```

---
### Configuring the login messages by UUID
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LoginMessages(uuid="7b1b3715-9ffa-11e8-a5dd-005056bbef18")
    resource.banner = "AUTHORIZED ACCESS ONLY"
    resource.message = "WELCOME!"
    resource.patch()

```

---
### Clearing the login messages configuration by UUID
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LoginMessages

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LoginMessages(uuid="7b1b3715-9ffa-11e8-a5dd-005056bbef18")
    resource.banner = ""
    resource.message = ""
    resource.patch()

```

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


__all__ = ["LoginMessages", "LoginMessagesSchema"]
__pdoc__ = {
    "LoginMessagesSchema.resource": False,
    "LoginMessages.login_messages_show": False,
    "LoginMessages.login_messages_create": False,
    "LoginMessages.login_messages_modify": False,
    "LoginMessages.login_messages_delete": False,
}


class LoginMessagesSchema(ResourceSchema):
    """The fields of the LoginMessages object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the login_messages. """

    banner = fields.Str(
        data_key="banner",
        validate=len_validation(minimum=0, maximum=2048),
    )
    r""" The login banner text. This message is displayed during SSH and console device
login just before the password prompt displays. When configured, a cluster-level
login banner is used for every incoming connection. Each data SVM can override
the cluster-level banner to instead display when you log into the SVM. To restore
the default setting for a data SVM, set the banner to an empty string.
New lines are supplied as either LF or CRLF but are always returned as LF.
Optional in the PATCH body. """

    message = fields.Str(
        data_key="message",
        validate=len_validation(minimum=0, maximum=2048),
    )
    r""" The message of the day (MOTD). This message appears just before the clustershell
prompt after a successful login. When configured, the cluster message
displays first. If you log in as a data SVM administrator, the
SVM message is then printed. The cluster-level MOTD can be disabled
for a given data SVM using the "show_cluster_message" property.
New lines are supplied as either LF or CRLF but are always returned as LF.
Optional in the PATCH body. """

    scope = fields.Str(
        data_key="scope",
    )
    r""" The scope field of the login_messages. """

    show_cluster_message = fields.Boolean(
        data_key="show_cluster_message",
    )
    r""" Specifies whether to show a cluster-level message before the SVM message
when logging in as an SVM administrator.
This setting can only be modified by the cluster administrator.
Optional in the PATCH body. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the login_messages. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier (ID) of the login messages configuration. """

    @property
    def resource(self):
        return LoginMessages

    gettable_fields = [
        "links",
        "banner",
        "message",
        "scope",
        "show_cluster_message",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,banner,message,scope,show_cluster_message,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "banner",
        "message",
        "scope",
        "show_cluster_message",
        "svm.name",
        "svm.uuid",
    ]
    """banner,message,scope,show_cluster_message,svm.name,svm.uuid,"""

    postable_fields = [
        "banner",
        "message",
        "scope",
        "show_cluster_message",
        "svm.name",
        "svm.uuid",
    ]
    """banner,message,scope,show_cluster_message,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LoginMessages.get_collection(fields=field)]
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
            raise NetAppRestError("LoginMessages modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LoginMessages(Resource):
    r""" The login banner and message of the day (MOTD) configuration. """

    _schema = LoginMessagesSchema
    _path = "/api/security/login/messages"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the login banner and messages of the day (MOTD) configured in the cluster
and in specific SVMs.

### Learn more
* [`DOC /security/login/messages`](#docs-security-security_login_messages)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="login messages show")
        def login_messages_show(
            fields: List[Choices.define(["banner", "message", "scope", "show_cluster_message", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LoginMessages resources

            Args:
                banner: The login banner text. This message is displayed during SSH and console device login just before the password prompt displays. When configured, a cluster-level login banner is used for every incoming connection. Each data SVM can override the cluster-level banner to instead display when you log into the SVM. To restore the default setting for a data SVM, set the banner to an empty string. New lines are supplied as either LF or CRLF but are always returned as LF. Optional in the PATCH body. 
                message: The message of the day (MOTD). This message appears just before the clustershell prompt after a successful login. When configured, the cluster message displays first. If you log in as a data SVM administrator, the SVM message is then printed. The cluster-level MOTD can be disabled for a given data SVM using the \"show_cluster_message\" property. New lines are supplied as either LF or CRLF but are always returned as LF. Optional in the PATCH body. 
                scope: 
                show_cluster_message: Specifies whether to show a cluster-level message before the SVM message when logging in as an SVM administrator. This setting can only be modified by the cluster administrator. Optional in the PATCH body. 
                uuid: The unique identifier (ID) of the login messages configuration. 
            """

            kwargs = {}
            if banner is not None:
                kwargs["banner"] = banner
            if message is not None:
                kwargs["message"] = message
            if scope is not None:
                kwargs["scope"] = scope
            if show_cluster_message is not None:
                kwargs["show_cluster_message"] = show_cluster_message
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LoginMessages.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LoginMessages resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["LoginMessages"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the login messages configuration.
There are no required fields. An empty body makes no modifications.

### Learn more
* [`DOC /security/login/messages`](#docs-security-security_login_messages)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the login banner and messages of the day (MOTD) configured in the cluster
and in specific SVMs.

### Learn more
* [`DOC /security/login/messages`](#docs-security-security_login_messages)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the login messages configuration by UUID.
### Learn more
* [`DOC /security/login/messages`](#docs-security-security_login_messages)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the login messages configuration.
There are no required fields. An empty body makes no modifications.

### Learn more
* [`DOC /security/login/messages`](#docs-security-security_login_messages)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="login messages modify")
        async def login_messages_modify(
        ) -> ResourceTable:
            """Modify an instance of a LoginMessages resource

            Args:
                banner: The login banner text. This message is displayed during SSH and console device login just before the password prompt displays. When configured, a cluster-level login banner is used for every incoming connection. Each data SVM can override the cluster-level banner to instead display when you log into the SVM. To restore the default setting for a data SVM, set the banner to an empty string. New lines are supplied as either LF or CRLF but are always returned as LF. Optional in the PATCH body. 
                query_banner: The login banner text. This message is displayed during SSH and console device login just before the password prompt displays. When configured, a cluster-level login banner is used for every incoming connection. Each data SVM can override the cluster-level banner to instead display when you log into the SVM. To restore the default setting for a data SVM, set the banner to an empty string. New lines are supplied as either LF or CRLF but are always returned as LF. Optional in the PATCH body. 
                message: The message of the day (MOTD). This message appears just before the clustershell prompt after a successful login. When configured, the cluster message displays first. If you log in as a data SVM administrator, the SVM message is then printed. The cluster-level MOTD can be disabled for a given data SVM using the \"show_cluster_message\" property. New lines are supplied as either LF or CRLF but are always returned as LF. Optional in the PATCH body. 
                query_message: The message of the day (MOTD). This message appears just before the clustershell prompt after a successful login. When configured, the cluster message displays first. If you log in as a data SVM administrator, the SVM message is then printed. The cluster-level MOTD can be disabled for a given data SVM using the \"show_cluster_message\" property. New lines are supplied as either LF or CRLF but are always returned as LF. Optional in the PATCH body. 
                scope: 
                query_scope: 
                show_cluster_message: Specifies whether to show a cluster-level message before the SVM message when logging in as an SVM administrator. This setting can only be modified by the cluster administrator. Optional in the PATCH body. 
                query_show_cluster_message: Specifies whether to show a cluster-level message before the SVM message when logging in as an SVM administrator. This setting can only be modified by the cluster administrator. Optional in the PATCH body. 
                uuid: The unique identifier (ID) of the login messages configuration. 
                query_uuid: The unique identifier (ID) of the login messages configuration. 
            """

            kwargs = {}
            changes = {}
            if query_banner is not None:
                kwargs["banner"] = query_banner
            if query_message is not None:
                kwargs["message"] = query_message
            if query_scope is not None:
                kwargs["scope"] = query_scope
            if query_show_cluster_message is not None:
                kwargs["show_cluster_message"] = query_show_cluster_message
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if banner is not None:
                changes["banner"] = banner
            if message is not None:
                changes["message"] = message
            if scope is not None:
                changes["scope"] = scope
            if show_cluster_message is not None:
                changes["show_cluster_message"] = show_cluster_message
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(LoginMessages, "find"):
                resource = LoginMessages.find(
                    **kwargs
                )
            else:
                resource = LoginMessages()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify LoginMessages: %s" % err)



