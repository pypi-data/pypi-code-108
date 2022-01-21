"""

Copyright &copy; 2021 NetApp Inc.
All rights reserved.

## Overview
This module is the implementation of the CLI resource. This resource is used as
an advanced way to send commands to the host system. These commands may or may
not have equivalent method of operation in the other resource sets.

## Examples
### Show command

```python
import json

from netapp_ontap import HostConnection
from netapp_ontap.resources import CLI

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    response = CLI().execute("vserver services web show")
    print(json.dumps(response.http_response.json(), indent=4))
```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
{
    "records": [
        {
            "vserver": "mycluster",
            "name": "FW_BMC"
        },
        {
            "vserver": "mycluster",
            "name": "backups"
        },
        {
            "vserver": "mycluster",
            "name": "disco"
        },
        {
            "vserver": "mycluster",
            "name": "docs"
        },
        {
            "vserver": "mycluster",
            "name": "docs-api"
        },
        {
            "vserver": "mycluster",
            "name": "docs-dev-api"
        },
        {
            "vserver": "mycluster",
            "name": "fud"
        },
        {
            "vserver": "mycluster",
            "name": "ontapi"
        },
        {
            "vserver": "mycluster",
            "name": "portal"
        },
        {
            "vserver": "mycluster",
            "name": "rest"
        },
        {
            "vserver": "mycluster",
            "name": "saml"
        },
        {
            "vserver": "mycluster",
            "name": "saml-sp"
        },
        {
            "vserver": "mycluster",
            "name": "security"
        },
        {
            "vserver": "mycluster",
            "name": "spi"
        },
        {
            "vserver": "mycluster",
            "name": "supdiag"
        },
        {
            "vserver": "mycluster",
            "name": "sysmgr"
        },
        {
            "vserver": "vs1",
            "name": "backups"
        },
        {
            "vserver": "vs1",
            "name": "docs-api"
        },
        {
            "vserver": "vs1",
            "name": "docs-dev-api"
        },
        {
            "vserver": "vs1",
            "name": "ontapi"
        },
        {
            "vserver": "vs1",
            "name": "rest"
        },
        {
            "vserver": "vs1",
            "name": "security"
        }
    ],
    "num_records": 23
}
```
</div>
</div>

### Show command with query

```python
import json

from netapp_ontap import HostConnection
from netapp_ontap.resources import CLI

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    response = CLI().execute("vserver services web show", vserver="vs1")
    print(json.dumps(response.http_response.json(), indent=4))
```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
{
    "records": [
        {
            "vserver": "vs1",
            "name": "backups"
        },
        {
            "vserver": "vs1",
            "name": "docs-api"
        },
        {
            "vserver": "vs1",
            "name": "docs-dev-api"
        },
        {
            "vserver": "vs1",
            "name": "ontapi"
        },
        {
            "vserver": "vs1",
            "name": "rest"
        },
        {
            "vserver": "vs1",
            "name": "security"
        }
    ],
    "num_records": 6
}
```
</div>
</div>

### Modify command with query

```python
import json

from netapp_ontap import HostConnection
from netapp_ontap.resources import CLI

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    response = CLI().execute(
        "vserver services web modify", body={"enabled": False}, vserver="vs1",
        name="ontapi",
    )
    print(json.dumps(response.http_response.json(), indent=4))
```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
{
    "num_records": 1
}
```
</div>
</div>

### Create command

```python
import json

from netapp_ontap import HostConnection
from netapp_ontap.resources import CLI

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    response = CLI().execute(
        "volume create",
        body={"volume": "vol1", "vserver": "vs1", "aggregate": "aggr1"},
        poll=False,
    )
    print(json.dumps(response.http_response.json(), indent=4))
    print(json.dumps(response.poll().http_response.json(), indent=4))
```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
{
    "job": {
        "uuid": "bce9cad6-afbe-11ea-8a81-005056bbe450",
        "_links": {
            "self": {
                "href": "/api/cluster/jobs/bce9cad6-afbe-11ea-8a81-005056bbe450"
            }
        }
    },
    "cli_output": "[Job 325] Job is queued: Create vol1."
}
{
    "uuid": "bce9cad6-afbe-11ea-8a81-005056bbe450",
    "description": "Create vol1",
    "state": "success",
    "message": "Complete: Successful [0]",
    "code": 0,
    "start_time": "2020-06-16T06:47:13-04:00",
    "end_time": "2020-06-16T06:47:13-04:00",
    "_links": {
        "self": {
            "href": "/api/cluster/jobs/bce9cad6-afbe-11ea-8a81-005056bbe450"
        }
    }
}

```
</div>
</div>

"""

import logging
from typing import Tuple

from netapp_ontap import utils
from netapp_ontap.error import NetAppRestError
from netapp_ontap.resource import Resource
from netapp_ontap.response import NetAppResponse


LOGGER = logging.getLogger(__name__)


class CLI(Resource):
    """To help CLI and ONTAP users transition to the ONTAP REST API, ONTAP 9.6
    provides a private REST API endpoint that can be used to access any CLI command.
    Usage of this API call is recorded and returned in the AutoSupport data
    collection so that NetApp can identify usablity and functionality improvements
    in the REST API for future releases. There is no per-API documentation for the
    REST API access for each CLI command. Unlike the documented REST APIs, the API
    paths and properties for the CLI passthrough correspond very closely to the
    CLI. There are several rules that govern all the differences between a CLI
    command and the REST API mirroring the CLI command.
    """

    _path = "/api/private/cli"

    # pylint: disable=bad-continuation
    @utils.api
    def execute(
        self, command, body: dict = None, privilege_level: str = "admin",
        poll: bool = True, **kwargs
    ) -> NetAppResponse:
        """Execute a command on the CLI and return the result

        Args:
            command: A string representing the command to execute. This should
                not include any input or query parameters. Only the base command.
                E.g.: "volume show", "system node coredump delete", etc.
            body: Any input parameters required to execute the command. These
                would be passed to the API in the body and used as the required
                or optional command input.
            privilege_level: If the command needs to be run at a particular
                privilege level, it can be specified here. The options are
                "admin" (default), "advanced", "diagnostic".
            poll: If the command starts a job, it will be tracked until it is
                complete. If this is not desired, set this value to False.
            kwargs: Any parameters needed to filter the objects on which the
                command will operate.

        Returns:
            Returns a `netapp_ontap.response.NetAppResponse` object containing the
            details of the HTTP response.

        Raises:
            `netapp_ontap.error.NetAppRestError`: If the API call returned a status
                code >= 400
        """

        verb, url = _parse_command(command)
        if verb == "post" and kwargs:
            verb = "patch"
        elif verb == "get" and body:
            verb = "post"

        kwargs["privilege_level"] = privilege_level
        url = f"{self.get_connection().origin}{self._path}/{url}"
        response = getattr(self.get_connection().session, verb)(url, params=kwargs, json=body)
        response.raise_for_status()
        self._set_last_state()
        self._last_response = NetAppResponse(response)
        if not self._last_response.is_job:
            # log CLI output if it exists
            response_body = self._last_response.http_response.json()
            if response_body.get("cli_output"):
                LOGGER.info(response_body.get("cli_output"))
        elif poll:
            return self._poll()
        return self._last_response


def _parse_command(command) -> Tuple[str, str]:
    """Return the path for a particular CLI command

    Here are several examples of mappings from the ONTAP CLI to the ONTAP
    REST API for the /api/private/cli path:
        * volume show → GET /api/private/cli/volume
        * volume create → POST /api/private/cli/volume
        * volume modify → PATCH /api/private/cli/volume
        * volume delete → DELETE /api/private/cli/volume
        * volume restrict → POST /api/private/cli/volume/restrict
        * volume show-space → GET /api/private/cli/volume/space
        * volume show-footprint → GET /api/private/cli/volume/footprint
        * cluster add-node → POST /api/private/cli/cluster/add-node
        * cluster add-node-status → GET /api/private/cli/system/node/add-node-status
        * system node coredump show → GET /api/private/cli/system/node/coredump
        * system node coredump delete → DELETE /api/private/cli/system/node/coredump
        * system node coredump delete-all → DELETE /api/private/cli/system/node/coredump/all

    Args:
        command: A string representing the command to execute. This should
            not include any input or query parameters. Only the base command.
            E.g.: "volume show", "system node coredump delete", etc.

    Returns:
        A tuple of URL and verb to use to make a request with.

    Raises:
        `netapp_ontap.error.NetAppRestError`: If the command could not be parsed.
    """

    if not command:
        raise NetAppRestError(
            message="The command must be provided to call any actions."
        )

    try:
        pieces = command.split(" ")
    except Exception:
        raise NetAppRestError(message="Unable to parse the command.")

    action_word = pieces[-1]
    everything_else = pieces[:-1]

    if "show" in action_word or "status" in action_word:
        verb = "get"
        if action_word.startswith("show-"):
            everything_else.append("-".join(action_word.split("-")[1:]))
        elif action_word != "show":
            everything_else.append(action_word)
    elif "modify" in action_word:
        verb = "patch"
    elif "delete" in action_word:
        verb = "delete"
        if action_word.startswith("delete-"):
            everything_else.append("-".join(action_word.split("-")[1:]))
    else:
        verb = "post"
        if action_word != "create":
            everything_else.append(action_word)

    return verb, "/".join(everything_else)
