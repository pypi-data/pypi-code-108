r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

# Overview
You can use this API to create a cluster, update cluster-wide configurations, and retrieve the current configuration details.
## Creating a cluster
You can create a new cluster by issuing a POST request to /cluster. Parameters are provided in the body of the POST request to configure cluster-wide settings and add nodes during the cluster setup.
### Fields used for creating a cluster
The fields used for the cluster APIs fall into the following categories:

* Required cluster-wide configuration
* Optional cluster-wide configuration
### Required cluster-wide configuration
The following fields are always required for any POST /cluster request:

* name
* password
### Optional cluster-wide configuration
The following fields are used to set up additional cluster-wide configurations:

* location
* contact
* dns_domains
* name_servers
* ntp_servers
* timezone
* license
* configuration_backup
* management_interface
* nodes
### Nodes field
The nodes field specifies the nodes to join to the cluster. To use this API, all nodes must run the same version of ONTAP. If you do not specify a node, the cluster is configured with one node added. The REST request is issued to the node that is added to the cluster. If you specify one node, do not use the "node.cluster_interface.ip.address" field. If you specify multiple nodes, specify the node to which the REST request is issued in addition to the remote nodes. Use the "node.cluster_interface.ip.address" field to identify each node. All other node fields are optional in all cases. If you provide a field for one node, you need to provide the same field for all nodes.
### Node networking fields
The cluster management interface and each node management interface use the cluster management interface subnet mask and gateway. For advanced configurations in which the cluster and node management interfaces are on different subnets, use the /network/ip/interface APIs to configure network interfaces after setup is complete.
The management interfaces are used to communicate with the name servers and NTP servers. The address family of the name servers and NTP servers must match the management interfaces address family.
### Single node cluster field
When the "single_node_cluster" field is set to "true", the cluster is created in single node cluster mode. You can provide a node field for this node for node-specific configuration but do not use the "node.cluster_interface.ip.address" field. Storage failover is configured to non-HA mode, and ports used for cluster ports are moved to the default IPspace. This might cause the node to reboot during setup. While a node reboots, the RESTful interface might not be available. See "Connection failures during cluster create" for more information.
### Create recommended aggregates parameter
When the "create_recommended_aggregates" parameter is set to "true", aggregates based on an optimal layout recommended by the system are created on each of the nodes in the cluster. The default setting is "false".
<br/>
---
## Performance monitoring
Performance of the cluster can be monitored by the `metric.*` and `statistics.*` fields. These fields show the performance of the cluster in terms of IOPS, latency and throughput. The `metric.*` fields denote an average, whereas the `statistics.*` fields denote a real-time monotonically increasing value aggregated across all nodes.
<br/>
---
## Monitoring cluster create status
### Errors before the job starts
Configuration in the POST /cluster request is validated before the cluster create job starts. If an invalid configuration is found, an HTTP error code in the 4xx range is returned. No cluster create job is started.
### Polling on the job
After a successful POST /cluster request is issued, an HTTP error code of 202 is returned along with a job UUID and link in the body of the response. The cluster create job continues asynchronously and is monitored with the job UUID using the /cluster/jobs API. The "message" field in the response of the GET /cluster/jobs/{uuid} request shows the current step in the job, and the "state" field shows the overall state of the job.
### Errors during the job
If a failure occurs during the cluster create job, the job body provides details of the error along with error code fields. See the error table under "Responses" in the POST /cluster documentation for common error codes and descriptions.
### Rerunning POST /cluster
The POST /cluster request can be rerun if errors occur. When rerunning the request, use the same body and query parameters. You can change the value of any field in the original body or query, but you cannot change the provided fields. For example, an initial request might have a body section as follows:
<br />
```
body =
{
  "name": "clusCreateRerun",
  "password": "openSesame",
  "nodes": [
    {
      "cluster_interface": {
        "ip": {
          "address": "1.1.1.1"
        }
      }
    },
    {
      "cluster_interface": {
        "ip": {
          "address": "2.2.2.2"
        }
      }
    }
  ]
}
```
A rerun request updates the body details to:
<br />
```
body =
{
  "name": "clusCreateRerun",
  "password": "openSesame",
  "nodes": [
    {
      "cluster_interface": {
        "ip": {
          "address": "3.3.3.3"
        }
      }
    },
    {
      "cluster_interface": {
        "ip": {
          "address": "4.4.4.4"
        }
      }
    }
  ]
}
```
A rerun request with the following body details is invalid:
<br />
```
body =
{
  "name": "clusCreateRerun",
  "password": "openSesame",
  "nodes": [
    {
      "cluster_interface": {
        "ip": {
          "address": "3.3.3.3"
        }
      }
    }
  ]
}
```
Note that the password might already be configured. If a password is already configured and then a new password is provided, the new request overwrites the existing password. If a password is already configured either by another interface or by a previous POST request to /cluster, authenticate any future REST requests with that password. If a POST request to /cluster with the default return_timeout of 0 returns an error, then the password was not changed.
### Connection failures during cluster create
A request to poll the job status might fail during a cluster create job in the following two cases. In these cases, programmatic use of the RESTful interface might be resilient to these connection failures.
1. When the "single_node_cluster" flag is set to "true", the node might reboot. During this time, the RESTful interface might refuse connections and return errors on a GET request, or connection timeouts might occur. Programmatic use of the RESTful interface during reboots must consider these effects while polling a cluster create job.
2. The "mgmt_auto" LIF is removed during the cluster create job. A POST /cluster request might be issued on the "mgmt_auto" LIF. However, requests to poll the job status might fail during cluster create when the "mgmt_auto" LIF is removed. The "mgmt_auto" LIF is only removed if a cluster management interface is provided as an argument to POST /cluster, and only after the cluster management interface is created. Programmatic use of the POST /cluster API on the "mgmt_auto" LIF should be configured to dynamically switch to polling the job on the cluster management LIF.
<br/>
---
## Modifying cluster configurations
The following fields can be used to modify a cluster-wide configuration:

* name
* location
* contact
* dns_domains
* name_servers
* timezone
* certificate
<br/>
---
# Examples
### Minimally configuring a 2-node setup
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Cluster

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Cluster()
    resource.name = "clusCreateExample1"
    resource.password = "openSesame"
    resource.nodes = [
        {"cluster_interface": {"ip": {"address": "1.1.1.1"}}},
        {"cluster_interface": {"ip": {"address": "2.2.2.2"}}},
    ]
    resource.post(hydrate=True)
    print(resource)

```

---
### Setting up a single node with additional node configuration and auto aggregate creation
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Cluster

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Cluster()
    resource.name = "clusCreateExample2"
    resource.password = "openSesame"
    resource.nodes = [{"name": "singleNode", "location": "Sunnyvale"}]
    resource.post(
        hydrate=True, single_node_cluster=True, create_recommended_aggregates=True
    )
    print(resource)

```

---
### Modifying a cluster-wide configuration
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Cluster

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Cluster()
    resource.contact = "it@company.com"
    resource.certificate = {"uuid": "1cd8a442-86d1-11e0-ae1c-123478563412"}
    resource.patch()

```

---
## Creating a cluster using the cluster "create" operation
This example shows how to create a cluster using the cluster APIs. Specifically, this example shows the creation of a two-node cluster and uses information from the nodes themselves combined with user supplied information to configure the cluster.
### Preparing for setup
Before the REST APIs can be issued to create the cluster, the cluster must be wired up and powered on. The network connections between the nodes for the cluster interconnect and the connections to the management network must be completed.  After the nodes are powered on, the nodes automatically configure interfaces on the platform's default cluster ports to allow the nodes to discover each other during setup and expansion workflows. You must configure a management interface on one node or use the mgmt_auto LIF, which is assigned an IP address using DHCP, to start using the REST APIs.  By making a console connection to a node, the cluster setup wizard guides you through the configuration of the initial node managment interface to which the REST calls can be sent.  Once this step is completed, exit the wizard by typing "exit". You can then issue REST API requests.
1.  Wire and power on the nodes.
2.  Make a console connection to one node to access the cluster setup wizard.
3.  Enter node management interface information to enable REST API requests to be sent to the node.
```
Welcome to the cluster setup wizard.
You can enter the following commands at any time:
  "help" or "?" - if you want to have a question clarified,
  "back" - if you want to change previously answered questions, and
  "exit" or "quit" - if you want to quit the cluster setup wizard.
  Any changes you made before quitting will be saved.
  You can return to cluster setup at any time by typing "cluster setup".
  To accept a default or omit a question, do not enter a value.
  This system will send event messages and periodic reports to NetApp Technical
  Support. To disable this feature, enter
  autosupport modify -support disable
  within 24 hours.
  Enabling AutoSupport can significantly speed problem determination and
  resolution should a problem occur on your system.
  For further information on AutoSupport, see:
    http://support.netapp.com/autosupport/
    Type yes to confirm and continue {yes}: yes
    Enter the node management interface port [e0c]:
      Enter the node management interface IP address: 10.224.82.249
      Enter the node management interface netmask: 255.255.192.0
      Enter the node management interface default gateway: 10.224.64.1
      A node management interface on port e0c with IP address 10.224.82.249 has been created.
      Use your web browser to complete cluster setup by accessing
      https://10.224.82.249
      Otherwise, press Enter to complete cluster setup using the command line
      interface: exit
      Exiting the cluster setup wizard. Any changes you made have been saved.
      The cluster administrator's account (username "admin") password is set to the system default.
      Warning: You have exited the cluster setup wizard before completing all
      of the tasks. The cluster is not configured. You can complete cluster setup by typing
      "cluster setup" in the command line interface.
```
---
### Discovering the nodes
If you issue a GET /api/cluster/nodes request when the nodes are not in a cluster, the API returns a list of nodes that were discovered on the cluster interconnect.  Information returned includes the node's serial number, model, software version, UUID, and cluster interface address.  The number of nodes returned should be the same as the number of nodes expected to be in the cluster.  If too many nodes are discovered, remove the nodes that should not be part of the cluster.  If not enough nodes are discovered, verify all the nodes are powered on, that the connections to the cluster interconnect are complete, and retry the command.
<br />
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Node

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Node.get_collection(fields="state,uptime")))

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    Node(
        {
            "_links": {
                "self": {
                    "href": "/api/cluster/nodes/6dce4710-c860-11e9-b5bc-005056bb6135"
                }
            },
            "state": "up",
            "uuid": "6dce4710-c860-11e9-b5bc-005056bb6135",
            "uptime": 134555,
            "name": "cluster1",
        }
    )
]

```
</div>
</div>

---
### Creating the cluster
When the node information is available, including each node's cluster interface address, you can assemble the information for creating the cluster.  Provide the cluster name and the password for the admin account.  The rest of the information is optional and can be configured later using other APIs.  Provide the cluster interface address for each node to be included in the cluster so that you can connect to it while adding it to the cluster. In addition to the cluster interface address, you can provide the optional node name, location, and management interface information. If you do not provide node names, nodes are named based on the cluster name. The nodes' managment interface subnet mask and gateway values are omitted and must be the same as the cluster management interface's subnet mask and gateway.
<br />
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Cluster

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Cluster()
    resource.name = "cluster1"
    resource.location = "datacenter1"
    resource.contact = "me"
    resource.dns_domains = ["example.com"]
    resource.name_servers = ["10.224.223.130", "10.224.223.131", "10.224.223.132"]
    resource.ntp_servers = ["time.nist.gov"]
    resource.management_interface = {
        "ip": {
            "address": "10.224.82.25",
            "netmask": "255.255.192.0",
            "gateway": "10.224.64.1",
        }
    }
    resource.password = "mypassword"
    resource.license = {"keys": ["AMEPOSOIKLKGEEEEDGNDEKSJDE"]}
    resource.nodes = [
        {
            "cluster_interface": {"ip": {"address": "169.254.245.113"}},
            "name": "node1",
            "management_interface": {"ip": {"address": "10.224.82.29"}},
        },
        {
            "cluster_interface": {"ip": {"address": "169.254.217.95"}},
            "name": "node2",
            "management_interface": {"ip": {"address": "10.224.82.31"}},
        },
    ]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
Cluster(
    {
        "name_servers": ["10.224.223.130", "10.224.223.131", "10.224.223.132"],
        "contact": "me",
        "management_interface": {
            "ip": {
                "gateway": "10.224.64.1",
                "netmask": "255.255.192.0",
                "address": "10.224.82.25",
            }
        },
        "license": {"keys": ["AMEPOSOIKLKGEEEEDGNDEKSJDE"]},
        "password": "mypassword",
        "dns_domains": ["example.com"],
        "ntp_servers": ["time.nist.gov"],
        "location": "datacenter1",
        "nodes": [
            {
                "management_interface": {"ip": {"address": "10.224.82.29"}},
                "cluster_interface": {"ip": {"address": "169.254.245.113"}},
                "name": "node1",
            },
            {
                "management_interface": {"ip": {"address": "10.224.82.31"}},
                "cluster_interface": {"ip": {"address": "169.254.217.95"}},
                "name": "node2",
            },
        ],
        "name": "cluster1",
    }
)

```
</div>
</div>

---
### Monitoring the progress of cluster creation
To monitor the progress of the cluster create operation, poll the returned job link until the state value is no longer "running" or "queued".
<br />
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="b5bc07e2-1e9-11e9-a751-005056bbd95f")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
Job(
    {
        "message": "success",
        "code": 0,
        "uuid": "b5bc07e2-19e9-11e9-a751-005056bbd95f",
        "state": "success",
        "description": "POST /api/cluster",
        "_links": {
            "self": {"href": "/api/cluster/jobs/b5bc07e2-19e9-11e9-a751-005056bbd95f"}
        },
    }
)

```
</div>
</div>

---
### Verifying the cluster information
After the cluster is created, you can verify the information applied using a number of APIs. You can retrieve most of the information provided using the /api/cluster and /api/cluster/nodes APIs. In addition, you can view the network interface and route information using the /api/network APIs. The following example shows how to retrieve the cluster information:
<br />
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Cluster

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Cluster()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example6_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example6_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example6_result" class="try_it_out_content">
```
Cluster(
    {
        "version": {
            "major": 10,
            "generation": 9,
            "full": "NetApp Release 9.10.1: Mon May 24 08:07:35 UTC 2021",
            "minor": 1,
        },
        "name_servers": ["10.224.223.131", "10.224.223.130"],
        "san_optimized": False,
        "_links": {"self": {"href": "/api/cluster"}},
        "management_interfaces": [
            {
                "_links": {
                    "self": {
                        "href": "/api/network/ip/interfaces/beef2db7-bd67-11eb-95f4-005056a7b9b1"
                    }
                },
                "ip": {"address": "10.236.153.229"},
                "uuid": "beef2db7-bd67-11eb-95f4-005056a7b9b1",
                "name": "clus_mgmt",
            },
            {
                "_links": {
                    "self": {
                        "href": "/api/network/ip/interfaces/cb63e02c-bd72-11eb-95f4-005056a7b9b1"
                    }
                },
                "ip": {"address": "fd20:8b1e:b255:9051::a02"},
                "uuid": "cb63e02c-bd72-11eb-95f4-005056a7b9b1",
                "name": "sti44-vsim-ucs515w_cluster_mgmt_inet6",
            },
            {
                "_links": {
                    "self": {
                        "href": "/api/network/ip/interfaces/ea13dec1-bd72-11eb-bd00-005056a7f50e"
                    }
                },
                "ip": {"address": "fd20:8b1e:b255:9051::a0a"},
                "uuid": "ea13dec1-bd72-11eb-bd00-005056a7f50e",
                "name": "sti44-vsim-ucs515x_cluster_mgmt_inet6",
            },
        ],
        "contact": "divyabha",
        "certificate": {
            "uuid": "b282f3d1-bd67-11eb-95f4-005056a7b9b1",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/b282f3d1-bd67-11eb-95f4-005056a7b9b1"
                }
            },
        },
        "statistics": {
            "iops_raw": {"total": 0, "write": 0, "read": 0, "other": 0},
            "status": "ok",
            "timestamp": "2021-05-26T20:36:25+00:00",
            "latency_raw": {"total": 0, "write": 0, "read": 0, "other": 0},
            "throughput_raw": {"total": 0, "write": 0, "read": 0, "other": 0},
        },
        "metric": {
            "status": "ok",
            "timestamp": "2021-05-26T20:36:15+00:00",
            "latency": {"total": 0, "write": 0, "read": 0, "other": 0},
            "throughput": {"total": 0, "write": 0, "read": 0, "other": 0},
            "duration": "PT15S",
            "iops": {"total": 0, "write": 0, "read": 0, "other": 0},
        },
        "peering_policy": {
            "encryption_required": False,
            "authentication_required": True,
            "minimum_passphrase_length": 8,
        },
        "uuid": "5f7f57c7-bd67-11eb-95f4-005056a7b9b1",
        "dns_domains": [
            "ctl.gdl.englab.netapp.com",
            "gdl.englab.netapp.com",
            "rtp.netapp.com",
            "eng.netapp.com",
            "netapp.com",
        ],
        "ntp_servers": ["10.235.48.111"],
        "location": "sti",
        "timezone": {"name": "America/New_York"},
        "name": "C1_sti44-vsim-ucs515w_1621957038",
    }
)

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


__all__ = ["Cluster", "ClusterSchema"]
__pdoc__ = {
    "ClusterSchema.resource": False,
    "Cluster.cluster_show": False,
    "Cluster.cluster_create": False,
    "Cluster.cluster_modify": False,
    "Cluster.cluster_delete": False,
}


class ClusterSchema(ResourceSchema):
    """The fields of the Cluster object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cluster. """

    certificate = fields.Nested("netapp_ontap.resources.security_certificate.SecurityCertificateSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the cluster. """

    configuration_backup = fields.Nested("netapp_ontap.resources.configuration_backup.ConfigurationBackupSchema", data_key="configuration_backup", unknown=EXCLUDE)
    r""" The configuration_backup field of the cluster. """

    contact = fields.Str(
        data_key="contact",
    )
    r""" The contact field of the cluster.

Example: support@company.com """

    dns_domains = fields.List(fields.Str, data_key="dns_domains")
    r""" A list of DNS domains.
Domain names have the following requirements:

* The name must contain only the following characters: A through Z, a through z, 0 through 9, ".", "-" or "_".
* The first character of each label, delimited by ".", must be one of the following characters: A through Z or a through z or 0 through 9.
* The last character of each label, delimited by ".", must be one of the following characters: A through Z, a through z, or 0 through 9.
* The top level domain must contain only the following characters: A through Z, a through z.
* The system reserves the following names:"all", "local", and "localhost".


Example: ["example.com","example2.example3.com"] """

    license = fields.Nested("netapp_ontap.models.license_keys.LicenseKeysSchema", data_key="license", unknown=EXCLUDE)
    r""" The license field of the cluster. """

    location = fields.Str(
        data_key="location",
    )
    r""" The location field of the cluster.

Example: building 1 """

    management_interface = fields.Nested("netapp_ontap.models.cluster_management_interface.ClusterManagementInterfaceSchema", data_key="management_interface", unknown=EXCLUDE)
    r""" The management_interface field of the cluster. """

    management_interfaces = fields.List(fields.Nested("netapp_ontap.resources.ip_interface.IpInterfaceSchema", unknown=EXCLUDE), data_key="management_interfaces")
    r""" The management_interfaces field of the cluster. """

    metric = fields.Nested("netapp_ontap.resources.performance_metric.PerformanceMetricSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the cluster. """

    name = fields.Str(
        data_key="name",
    )
    r""" The name field of the cluster.

Example: cluster1 """

    name_servers = fields.List(fields.Str, data_key="name_servers")
    r""" The list of IP addresses of the DNS servers. Addresses can be either
IPv4 or IPv6 addresses.


Example: ["10.224.65.20","2001:db08:a0b:12f0::1"] """

    nodes = fields.List(fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE), data_key="nodes")
    r""" The nodes field of the cluster. """

    ntp_servers = fields.List(fields.Str, data_key="ntp_servers")
    r""" Host name, IPv4 address, or IPv6 address for the external NTP time servers.

Example: ["time.nist.gov","10.98.19.20","2610:20:6F15:15::27"] """

    password = fields.Str(
        data_key="password",
    )
    r""" Initial admin password used to create the cluster.

Example: mypassword """

    peering_policy = fields.Nested("netapp_ontap.models.cluster_peering_policy.ClusterPeeringPolicySchema", data_key="peering_policy", unknown=EXCLUDE)
    r""" The peering_policy field of the cluster. """

    san_optimized = fields.Boolean(
        data_key="san_optimized",
    )
    r""" Specifies if this cluster is an All SAN Array. """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw.PerformanceMetricRawSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the cluster. """

    timezone = fields.Nested("netapp_ontap.models.timezone_cluster.TimezoneClusterSchema", data_key="timezone", unknown=EXCLUDE)
    r""" The timezone field of the cluster. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The uuid field of the cluster.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    version = fields.Nested("netapp_ontap.models.version.VersionSchema", data_key="version", unknown=EXCLUDE)
    r""" The version field of the cluster. """

    @property
    def resource(self):
        return Cluster

    gettable_fields = [
        "links",
        "certificate.links",
        "certificate.name",
        "certificate.uuid",
        "contact",
        "dns_domains",
        "location",
        "management_interfaces.links",
        "management_interfaces.ip",
        "management_interfaces.name",
        "management_interfaces.uuid",
        "metric",
        "name",
        "name_servers",
        "ntp_servers",
        "peering_policy",
        "san_optimized",
        "statistics.iops_raw",
        "statistics.latency_raw",
        "statistics.status",
        "statistics.throughput_raw",
        "statistics.timestamp",
        "timezone",
        "uuid",
        "version",
    ]
    """links,certificate.links,certificate.name,certificate.uuid,contact,dns_domains,location,management_interfaces.links,management_interfaces.ip,management_interfaces.name,management_interfaces.uuid,metric,name,name_servers,ntp_servers,peering_policy,san_optimized,statistics.iops_raw,statistics.latency_raw,statistics.status,statistics.throughput_raw,statistics.timestamp,timezone,uuid,version,"""

    patchable_fields = [
        "certificate.name",
        "certificate.uuid",
        "contact",
        "dns_domains",
        "location",
        "name",
        "name_servers",
        "peering_policy",
        "timezone",
    ]
    """certificate.name,certificate.uuid,contact,dns_domains,location,name,name_servers,peering_policy,timezone,"""

    postable_fields = [
        "configuration_backup",
        "contact",
        "dns_domains",
        "license",
        "location",
        "management_interface",
        "name",
        "name_servers",
        "nodes",
        "ntp_servers",
        "password",
        "peering_policy",
        "timezone",
    ]
    """configuration_backup,contact,dns_domains,license,location,management_interface,name,name_servers,nodes,ntp_servers,password,peering_policy,timezone,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Cluster.get_collection(fields=field)]
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
            raise NetAppRestError("Cluster modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Cluster(Resource):
    r""" Complete cluster information """

    _schema = ClusterSchema
    _path = "/api/cluster"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the cluster configuration.
### Learn more
* [`DOC /cluster`](#docs-cluster-cluster)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster show")
        def cluster_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single Cluster resource

            Args:
                contact: 
                dns_domains: A list of DNS domains. Domain names have the following requirements: * The name must contain only the following characters: A through Z,   a through z, 0 through 9, \".\", \"-\" or \"_\". * The first character of each label, delimited by \".\", must be one   of the following characters: A through Z or a through z or 0   through 9. * The last character of each label, delimited by \".\", must be one of   the following characters: A through Z, a through z, or 0 through 9. * The top level domain must contain only the following characters: A   through Z, a through z. * The system reserves the following names:\"all\", \"local\", and \"localhost\". 
                location: 
                name: 
                name_servers: The list of IP addresses of the DNS servers. Addresses can be either IPv4 or IPv6 addresses. 
                ntp_servers: Host name, IPv4 address, or IPv6 address for the external NTP time servers.
                password: Initial admin password used to create the cluster.
                san_optimized: Specifies if this cluster is an All SAN Array.
                uuid: 
            """

            kwargs = {}
            if contact is not None:
                kwargs["contact"] = contact
            if dns_domains is not None:
                kwargs["dns_domains"] = dns_domains
            if location is not None:
                kwargs["location"] = location
            if name is not None:
                kwargs["name"] = name
            if name_servers is not None:
                kwargs["name_servers"] = name_servers
            if ntp_servers is not None:
                kwargs["ntp_servers"] = ntp_servers
            if password is not None:
                kwargs["password"] = password
            if san_optimized is not None:
                kwargs["san_optimized"] = san_optimized
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = Cluster(
                **kwargs
            )
            resource.get()
            return [resource]

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a cluster.
### Required properties
* `name`
* `password`
### Recommended optional properties
* `location`
* `contact`
* `dns_domains`
* `name_servers`
* `ntp_servers`
* `license`
* `configuration_backup`
* `management_interface`
* `nodes`
* `timezone`
### Learn more
* [`DOC /cluster`](#docs-cluster-cluster)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster create")
        async def cluster_create(
        ) -> ResourceTable:
            """Create an instance of a Cluster resource

            Args:
                links: 
                certificate: 
                configuration_backup: 
                contact: 
                dns_domains: A list of DNS domains. Domain names have the following requirements: * The name must contain only the following characters: A through Z,   a through z, 0 through 9, \".\", \"-\" or \"_\". * The first character of each label, delimited by \".\", must be one   of the following characters: A through Z or a through z or 0   through 9. * The last character of each label, delimited by \".\", must be one of   the following characters: A through Z, a through z, or 0 through 9. * The top level domain must contain only the following characters: A   through Z, a through z. * The system reserves the following names:\"all\", \"local\", and \"localhost\". 
                license: 
                location: 
                management_interface: 
                management_interfaces: 
                metric: 
                name: 
                name_servers: The list of IP addresses of the DNS servers. Addresses can be either IPv4 or IPv6 addresses. 
                nodes: 
                ntp_servers: Host name, IPv4 address, or IPv6 address for the external NTP time servers.
                password: Initial admin password used to create the cluster.
                peering_policy: 
                san_optimized: Specifies if this cluster is an All SAN Array.
                statistics: 
                timezone: 
                uuid: 
                version: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if certificate is not None:
                kwargs["certificate"] = certificate
            if configuration_backup is not None:
                kwargs["configuration_backup"] = configuration_backup
            if contact is not None:
                kwargs["contact"] = contact
            if dns_domains is not None:
                kwargs["dns_domains"] = dns_domains
            if license is not None:
                kwargs["license"] = license
            if location is not None:
                kwargs["location"] = location
            if management_interface is not None:
                kwargs["management_interface"] = management_interface
            if management_interfaces is not None:
                kwargs["management_interfaces"] = management_interfaces
            if metric is not None:
                kwargs["metric"] = metric
            if name is not None:
                kwargs["name"] = name
            if name_servers is not None:
                kwargs["name_servers"] = name_servers
            if nodes is not None:
                kwargs["nodes"] = nodes
            if ntp_servers is not None:
                kwargs["ntp_servers"] = ntp_servers
            if password is not None:
                kwargs["password"] = password
            if peering_policy is not None:
                kwargs["peering_policy"] = peering_policy
            if san_optimized is not None:
                kwargs["san_optimized"] = san_optimized
            if statistics is not None:
                kwargs["statistics"] = statistics
            if timezone is not None:
                kwargs["timezone"] = timezone
            if uuid is not None:
                kwargs["uuid"] = uuid
            if version is not None:
                kwargs["version"] = version

            resource = Cluster(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Cluster: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the cluster configuration after the cluster is created.
### Related ONTAP commands * `cluster identity modify` * `system node modify` * `vserver services dns modify` * `vserver services name-service dns modify` * `timezone` * `security ssl modify`
### Learn more
* [`DOC /cluster`](#docs-cluster-cluster)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster modify")
        async def cluster_modify(
        ) -> ResourceTable:
            """Modify an instance of a Cluster resource

            Args:
                contact: 
                query_contact: 
                dns_domains: A list of DNS domains. Domain names have the following requirements: * The name must contain only the following characters: A through Z,   a through z, 0 through 9, \".\", \"-\" or \"_\". * The first character of each label, delimited by \".\", must be one   of the following characters: A through Z or a through z or 0   through 9. * The last character of each label, delimited by \".\", must be one of   the following characters: A through Z, a through z, or 0 through 9. * The top level domain must contain only the following characters: A   through Z, a through z. * The system reserves the following names:\"all\", \"local\", and \"localhost\". 
                query_dns_domains: A list of DNS domains. Domain names have the following requirements: * The name must contain only the following characters: A through Z,   a through z, 0 through 9, \".\", \"-\" or \"_\". * The first character of each label, delimited by \".\", must be one   of the following characters: A through Z or a through z or 0   through 9. * The last character of each label, delimited by \".\", must be one of   the following characters: A through Z, a through z, or 0 through 9. * The top level domain must contain only the following characters: A   through Z, a through z. * The system reserves the following names:\"all\", \"local\", and \"localhost\". 
                location: 
                query_location: 
                name: 
                query_name: 
                name_servers: The list of IP addresses of the DNS servers. Addresses can be either IPv4 or IPv6 addresses. 
                query_name_servers: The list of IP addresses of the DNS servers. Addresses can be either IPv4 or IPv6 addresses. 
                ntp_servers: Host name, IPv4 address, or IPv6 address for the external NTP time servers.
                query_ntp_servers: Host name, IPv4 address, or IPv6 address for the external NTP time servers.
                password: Initial admin password used to create the cluster.
                query_password: Initial admin password used to create the cluster.
                san_optimized: Specifies if this cluster is an All SAN Array.
                query_san_optimized: Specifies if this cluster is an All SAN Array.
                uuid: 
                query_uuid: 
            """

            kwargs = {}
            changes = {}
            if query_contact is not None:
                kwargs["contact"] = query_contact
            if query_dns_domains is not None:
                kwargs["dns_domains"] = query_dns_domains
            if query_location is not None:
                kwargs["location"] = query_location
            if query_name is not None:
                kwargs["name"] = query_name
            if query_name_servers is not None:
                kwargs["name_servers"] = query_name_servers
            if query_ntp_servers is not None:
                kwargs["ntp_servers"] = query_ntp_servers
            if query_password is not None:
                kwargs["password"] = query_password
            if query_san_optimized is not None:
                kwargs["san_optimized"] = query_san_optimized
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if contact is not None:
                changes["contact"] = contact
            if dns_domains is not None:
                changes["dns_domains"] = dns_domains
            if location is not None:
                changes["location"] = location
            if name is not None:
                changes["name"] = name
            if name_servers is not None:
                changes["name_servers"] = name_servers
            if ntp_servers is not None:
                changes["ntp_servers"] = ntp_servers
            if password is not None:
                changes["password"] = password
            if san_optimized is not None:
                changes["san_optimized"] = san_optimized
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(Cluster, "find"):
                resource = Cluster.find(
                    **kwargs
                )
            else:
                resource = Cluster()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Cluster: %s" % err)



