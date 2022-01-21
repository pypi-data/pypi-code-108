# pylint: disable=line-too-long
# pylint: disable=trailing-whitespace
# pylint: disable=too-many-lines
"""

# NetApp ONTAP
The Python client library is a package you can use when writing scripts to access the
ONTAP REST API. It provides support for several underlying services, including connection
management, asynchronous request processing, and exception handling. By using the Python
client library, you can quickly develop robust code to support the automation of your ONTAP
deployments.

# Getting started
The Python client library is available as the package **netapp_ontap** at the Python Package
Index (PyPi) web site at https://pypi.org/project/netapp-ontap

## Software requirements
Before installing the Python client library, you must make sure the following packages are
installed on your system:  

* python 3.6 or later    
* requests 2.26.0 or later   
* requests-toolbelt 0.9.1 or later
* marshmallow 3.2.1 or later  

The library requires version 1.26.7 or later of urllib3 due to outstanding CVEs against
older versions. However, it will still work with older versions of urllib3 as long as
that version of urllib3 is compatible with the requests package.

## Installing and importing the package
You must install the package using the pip utility:

```
pip install netapp-ontap
```

After installing the package, you can import the objects you need into your application:

```python
from netapp_ontap.resources import Volume, Snapshot
```

## Creating an object

You can create an object in several different ways. Here are three examples of
creating an equivalent `Volume` object.

```python
from netapp_ontap.resources import Volume

# Example 1 - keyword arguments
volume = Volume(name='vol1', svm={'name': 'vs1'}, aggregates=[{'name': 'aggr1'}])

# Example 2 - dict as keyword arguments
data = {
    'name': 'vol1',
    'svm': {'name': 'vs1'},
    'aggregates': [{'name': 'aggr1'}],
}
volume = Volume(**data)

# Example 3 - using the from_dict() method
volume = Volume.from_dict({
    'name': 'vol1',
    'svm': {'name': 'vs1'},
    'aggregates': [{'name': 'aggr1'}],
})
```

## Performing actions on an object

After you create an object, you can perform actions on the object based
on the purpose and design of your application. The example below illustrates
how to create a new volume and then take a snapshot.

Note that when using the library, in all cases you must first establish a
connection to the management LIF of the ONTAP system using the
`netapp_ontap.host_connection.HostConnection` object. In the example below,
the connection is created and then set as the global default.
This means that all objects and the associated actions reuse
this same connection. See *Host connections* for more information.

```python
from netapp_ontap import config, HostConnection
from netapp_ontap.resources import Volume, Snapshot

config.CONNECTION = HostConnection('myhost.mycompany.com', 'username', 'password')

volume = Volume(name='vol1', svm={'name': 'vs1'}, aggregates=[{'name': 'aggr1'}])
volume.post()
snapshot = Snapshot.from_dict({
    'name': '%s_snapshot' % volume.name,
    'comment': 'A snapshot of %s' % volume.name,
    'volume': volume.to_dict(),
})
snapshot.post()
```

# Host connections

The `netapp_ontap.host_connection.HostConnection` object allows a client application
to store credentials once and reuse them for each subsequent operation.
You can do this in any of the following ways:

* Use the connection object as a context manager with the **with** keyword.

* Call the function `set_connection()` on a specific resource so the connection is used for
all actions on the resource.

* Set the `netapp_ontap.config.CONNECTION` variable to establish a single connection instance for all
operations within the scope of that block. This allows you to connect to ONTAP once
and use the same connection everywhere, instead of providing credentials every time you make a
request.

Note that you can call `get_connection()` to get the connection used by an object and use it for
subsequent operations.

By default, every operation attempts to verify the SSL certificate for the connection. If a
certificate cannot be verified, the **SSLError** exception is thrown. You can disable this
verification by setting `netapp_ontap.host_connection.HostConnection.verify` to false when creating the
`netapp_ontap.host_connection.HostConnection` instance.

## Custom headers

In some cases, you might want to set and send custom headers with the REST request.
This can be done at the connection level. For a specific connection, you can pass in
the headers you would like to send for each request within the scope of that connection object.
The library provides full access to the request headers so that you can update, add, or delete
headers from the same connection object at any point. If a header is not recognized by ONTAP,
it is ignored.

```python
from netapp_ontap import config, HostConnection
headers = {'my-header1':'my-header-value1', 'my-header2':'my-header-value2'}

# Initialize a connection object with custom headers
config.CONNECTION = HostConnection('myhost.mycompany.com', 'username', 'password', headers=headers)

# Delete a header from a connection object
conn = HostConnection('myhost.mycompany.com', 'username', 'password', headers=headers)
del conn.request_headers['my-header1']

# Add a header to a connection object using the assignment operator
conn = HostConnection('myhost.mycompany.com', 'username', 'password', headers=headers)
conn.request_headers['mynew-header'] = 'mynew-header-value'

# Add headers to a connection object
config.CONNECTION = HostConnection('myhost.mycompany.com', 'username' 'password')
config.CONNECTION.request_headers = headers

# Update an existing header using the assignment operator
config.CONNECTION = HostConnection('myhost.mycompany.com','username','password', headers=headers)
config.CONNECTION.request_headers['my-header1'] = 'my-new-header'
```

# Asynchronous processing and jobs

All POST, PATCH, and DELETE requests that can take more than two seconds to complete are
designed to run asynchronously as non-blocking operations. These operations are executed
as background jobs at the ONTAP cluster. The HTTP response generated by an
asynchronous request always contains a link to the associated job object. By default, an
asynchronous request automatically polls the job using the unique job identifier in the link.
Control is returned to your script when a terminal state is reached (success or failure) or
the configured timeout value expires. However, you can override this behavior by setting the
**poll** value to false when calling the function, causing control to return before the job
completes. Forcing an immediate return can be useful when a job might take a long time to
complete and you want to continute execution of the script.

# Responses

A request always returns a `netapp_ontap.response.NetAppResponse` object which contains the details
of the HTTP response. It contains information such as whether the response is an error
or a job. Refer to `netapp_ontap.response.NetAppResponse` for further information on how
to check the details of the response.

# Exception handling

By default, an exception is returned if a request returns an HTTP status code of 400 or greater.
The exception object, which is of type `netapp_ontap.error.NetAppRestError`,
holds the HTTP response object so that the exception can be handled in the client code.
If you wish not to raise exceptions, you can set `netapp_ontap.config.RAISE_API_ERRORS` to false. In this case,
it is up to the client to check the HTTP response from the `netapp_ontap.response.NetAppResponse`
object and handle any errors. Refer to `netapp_ontap.error.NetAppRestError` for further information.

```python
# Set RAISE_API_ERRORS to False and check the HTTP response.
config.RAISE_API_ERRORS = False
response = Svm.find(name="nonexistent_vs")
assert "entry doesn't exist" in response.http_response.text
```

# Debugging

While writing your application, it can often be useful to see the raw HTTP request and response
text that the library is sending to and from the server. There are two flags that can be set
to help with this.

## DEBUG flag

The first is the DEBUG flag. This can be set either by setting DEBUG=1 in the environment prior
to executing your application or by setting `netapp_ontap.utils.DEBUG` to 1 inside of your application.
This flag, when set, will cause the library to log the request and response for any failed
API call. This will be logged at DEBUG level (see the section on logging for setting up your
application). Here's an example of setting this value inside of your application:

```python
import logging

from netapp_ontap import HostConnection, NetAppRestError, config, utils
from netapp_ontap.resources import Volume

logging.basicConfig(level=logging.DEBUG)
config.CONNECTION = HostConnection('10.100.200.50', username='admin', password='password', verify=False)

# Set the DEBUG flag to 1
utils.DEBUG = 1

# this API call will fail with a 404
try:
    volume = Volume(uuid="1", name='does_not_exist')
    volume.get()
except NetAppRestError:
    print('We got an expected exception')
```

Here is what the output would look like:

```
$ python test_debug.py
DEBUG:urllib3.util.retry:Converted retries value: 5 -> Retry(total=5, connect=None, read=None, redirect=None, status=None)
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): 10.100.200.50:443
DEBUG:urllib3.connectionpool:https://10.100.200.50:443 "GET /api/storage/volumes/1 HTTP/1.1" 404 130
DEBUG:netapp_ontap.utils:
-----------REQUEST-----------
GET https://10.100.200.50:443/api/storage/volumes/1
Accept: */*
User-Agent: python-requests/2.21.0
Connection: keep-alive
Accept-Encoding: gzip, deflate
X-Dot-Client-App: netapp-ontap-python-9.8.0
Authorization: Basic YWRtaW46cGFzc3dvcmQK
None
-----------------------------

-----------RESPONSE-----------
404 Not Found
Date:Tue, 12 Nov 2019 13:00:24 GMT
Server:libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 130
Content-Type: application/hal+json
Keep-Alive: timeout=5, max=100
Connection:Keep-Alive
{
  "error": {
    "message": "\"1\" is an invalid value for field \"uuid\" (<UUID>)",
    "code": "2",
    "target": "uuid"
  }
}
------------------------------
We got an expected exception
$
```

## LOG_ALL_API_CALLS flag

There is also a LOG_ALL_API_CALLS flag which can be set in the same ways. You can
set it in the environment or during script execution by setting `netapp_ontap.utils.LOG_ALL_API_CALLS`
to 1. This flag will produce the same output as above, but it will log the call no
matter if there was a failure or not. Here's an example of what that would look
like if we got an existing volume:

```python
import logging

from netapp_ontap import HostConnection, config, utils
from netapp_ontap.resources import Volume

logging.basicConfig(level=logging.DEBUG)
config.CONNECTION = HostConnection('10.100.200.50', username='admin', password='password', verify=False)

# Set the LOG_ALL_API_CALLS flag to 1
utils.LOG_ALL_API_CALLS = 1

# this API call will succeed and be logged
volume = list(Volume.get_collection())[0]
```

Here is what the output would look like:

```
$ python test_debug.py
DEBUG:urllib3.util.retry:Converted retries value: 5 -> Retry(total=5, connect=None, read=None, redirect=None, status=None)
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): 10.100.200.50:443
DEBUG:urllib3.connectionpool:https://10.100.200.50:443 "GET /api/storage/volumes HTTP/1.1" 200 567
DEBUG:netapp_ontap.utils:
-----------REQUEST-----------
GET https://10.100.200.50:443/api/storage/volumes
User-Agent: python-requests/2.21.0
Connection: keep-alive
Accept: */*
Accept-Encoding: gzip, deflate
X-Dot-Client-App: netapp-ontap-python-9.8.0
Authorization: Basic YWRtaW46cGFzc3dvcmQK
None
-----------------------------

-----------RESPONSE-----------
200 OK
Date:Tue, 12 Nov 2019 13:14:01 GMT
Server:libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 567
Content-Type: application/hal+json
Keep-Alive: timeout=5, max=100
Connection:Keep-Alive
{
  "records": [
    {
      "uuid": "c68bdca8-d090-11e9-bb29-005056bb7f42",
      "name": "vs0_root",
      "_links": {
        "self": {
          "href": "/api/storage/volumes/c68bdca8-d090-11e9-bb29-005056bb7f42"
        }
      }
    },
    {
      "uuid": "ed3b6ebf-d48e-11e9-bb29-005056bb7f42",
      "name": "vs1_root",
      "_links": {
        "self": {
          "href": "/api/storage/volumes/ed3b6ebf-d48e-11e9-bb29-005056bb7f42"
        }
      }
    }
  ],
  "num_records": 2,
  "_links": {
    "self": {
      "href": "/api/storage/volumes"
    }
  }
}
------------------------------
$
```

# Additional considerations

In most cases, the objects and actions in the library can be mapped directly
to equivalent cURL commands run against the ONTAP REST interface. However, there are a few
exceptions you should be aware of.

## Property names

If a property of a resource is named the same as one of the Python reserved names,
the name is transposed when accessing the member of the resource. For example,
if there is a resource named "Foo" that has a property defined in the API named "class",
the property name would instead be "class_" when using the library. For example:

```python
from netapp_ontap.resources import Foo

foo = Foo()
foo.class_ = "high"
```

# Documentation

To view the latest documentation, visit https://devnet.netapp.com/restapi.php , click on the
"Python Client Library" tab, and then choose the latest version of the docs. You can also view
the ONTAP REST API docs linked from the same page under the "Overview" tab.

If you want to view this library's docs offline, then you can locate the copy installed in
`<python_environment>/lib/<python_version>/site_packages/netapp_ontap/docs`.

# Compatibility

The version assigned to the library consists of the major ONTAP release it is generated
from and a minor version for the library within that release. For example: within the
ONTAP 9.7 product family, the library may ship several fix releases by incrementing the
minor index: 9.7.0, 9.7.1, 9.7.2. The minor version
allows the library to be updated at a cadence separate from ONTAP.

Client libraries that have the same major version as ONTAP are completely compatible.
For example, the libraries netapp-ontap-9.6.1 and netapp-ontap-9.6.4 are fully
compatible with both ONTAP 9.6 and ONTAP 9.6P1.

A client library will support N-1 major versions of ONTAP with full backwards compatiblity
of all APIs and fields. For example, a program written using client library 9.6.1 and
talking to ONTAP 9.6 will continue to function consistently when the client library is
updated to 9.7.0.

A client library with a major version less than the ONTAP release can still be
used, however it will not be able to access any of the new REST APIs. For example, the library
netapp-ontap-9.6.4 is only partially compatible with ONTAP 9.7. In this case, the library will
not have access to the newer APIs or fields offered by ONTAP, but scripts can continue to
access any of the same 9.6 fields they were before without issue.

For example a new property **volume.is_svm_root** was added with ONTAP 9.7.
The following behaviors would be seen with different libraries and ONTAP combinations:

* library 9.6.0 would ignore the value coming from an ONTAP 9.7 response

* library 9.7.0 would fully support the property coming from an ONTAP 9.7+ response

* library 9.7.0 would not produce any errors fro that property coming from an ONTAP 9.6 response

# Changelog

There are several changes to the Python Client Library and the ONTAP REST API, which are organized by release below.
## 9.10.1 library updates  
(2022-01-21)

No changes between RC1 and this GA release


## 9.10.1 RC1  library updates  
(2021-11-05)

** New endpoints **

* Endpoint: /cluster/metrocluster/interconnects/{node.uuid}/{partner_type}/{adapter}  
  HTTP methods: PATCH  
  This API updates a MetroCluster interconnect interface.  

* Endpoint: /cluster/web  
  HTTP methods: GET, PATCH  
  These APIs are for web services configuration.  

* Endpoint: /svm/migrations  
  HTTP methods: GET, POST  
  These APIs allow creation and observation of the SVM migrations.  

* Endpoint: /svm/migrations/{uuid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs allow management of a single SVM migration.  

* Endpoint: /svm/migrations/{svm_migration.uuid}/volumes  
  HTTP methods: GET  
  This API retrieves the transfer status of the volumes in the SVM.  

* Endpoint: /svm/migrations/{svm_migration.uuid}/volumes/{volume.uuid}  
  HTTP methods: GET  
  This API retrieves the transfer status for the specified volume.  

* Endpoint: /svm/svms/{svm.uuid}/web  
  HTTP methods: GET, PATCH  
  These APIs manage the web services security configuration.  

* Endpoint: /name-services/host-record/{svm.uuid}/host  
  HTTP methods: GET  
  This API retrieves the IP address of the specified hostname.  

* Endpoint: /name-services/local-hosts  
  HTTP methods: GET, POST  
  These APIs are for managing IP to hostname mappings.  

* Endpoint: /name-services/local-hosts/{owner.uuid}/{address}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage a specified SVM and IP address.  

* Endpoint: /name-services/unix-groups/{svm.uuid}/{unix_group.name}/users  
  HTTP methods: GET  
  This API retrieves users to the specified UNIX group and SVM.  

* Endpoint: /name-services/unix-groups/{svm.uuid}/{unix_group.name}/users/{name}  
  HTTP methods: GET  
  This API retrieves a user from the specified UNIX group.  

* Endpoint: /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes  
  HTTP methods: GET, POST  
  These APIs are for managing LUN map reporting nodes.  

* Endpoint: /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes/{uuid}  
  HTTP methods: GET, DELETE  
  These APIs manage Lun map reports for the specified node.  

* Endpoint: /protocols/san/vvol-bindings  
  HTTP methods: GET, POST  
  These APIs are for vVol bindings.  

* Endpoint: /protocols/san/vvol-bindings/{protocol_endpoint.uuid}/{vvol.uuid}  
  HTTP methods: GET, DELETE  
  These APIs manage vVol bindings per vvol uuid.  

* Endpoint: /storage/luns/{lun.uuid}/attributes  
  HTTP methods: GET, POST  
  These APIs are for LUN attributes.  

* Endpoint: /storage/luns/{lun.uuid}/attributes/{name}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage LUN attributes for the specific lun and name.  

* Endpoint: /application/consistency-groups  
  HTTP methods: GET, POST  
  These APIs manage details of a collection or a specific consistency group.  

* Endpoint: /application/consistency-groups/{uuid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage consistency groups.  

* Endpoint: /application/consistency-groups/{uuid}/{consistency_group.uuid}/snapshots  
  HTTP methods: GET, POST  
  These APIs manage snapshot copies of a collection or a specific consistency group.  

* Endpoint: /application/consistency-groups/{uuid}/{consistency_group.uuid}/snapshots/{uuid}  
  HTTP methods: GET, DELETE  
  These APIs manage details of a specific snapshot for a consistency group.  

* Endpoint: /support/auto-update  
  HTTP methods: GET, PATCH  
  These APIs manage the current status of the automatic update feature and the End User License Agreement (EULA).  

* Endpoint: /support/auto-update/configurations  
  HTTP methods: GET  
  This API retrieves the configuration for automatic updates.  

* Endpoint: /support/auto-update/configurations/{uuid}  
  HTTP methods: GET, PATCH  
  These APIs manage the configuration for a specified automatic update.  

* Endpoint: /support/auto-update/updates  
  HTTP methods: GET  
  This API retrieves the status of all updates.  

* Endpoint: /support/auto-update/updates/{uuid}  
  HTTP methods: GET, PATCH  
  These APIs manage the status of an update.  

* Endpoint: /support/coredump/coredumps  
  HTTP methods: GET  
  This API retrieves a collection of coredumps.  

* Endpoint: /support/coredump/coredumps/{node.uuid}/{name}  
  HTTP methods: GET, DELETE  
  These APIs manage a specific core dump.  

* Endpoint: /security/anti-ransomware/suspects  
  HTTP methods: GET  
  This API retrieves information on the suspects generated by the anti-ransomware analytics.  

* Endpoint: /security/anti-ransomware/suspects/{volume.uuid}  
  HTTP methods: DELETE  
  This API clears either all the suspect files of a volume or suspect files of a volume based on file format or suspect time provided.  

* Endpoint: /security/azure-key-vaults/{uuid}/rekey-internal  
  HTTP methods: POST  
  This API rekeys the internal key in the key hierarchy for an SVM with an AKV configuration.  

* Endpoint: /security/azure-key-vaults/{uuid}/restore  
  HTTP methods: POST  
  This API restores the keys for an SVM from a configured AKV.  

* Endpoint: /security/gcp-kms/{uuid}/rekey-internal  
  HTTP methods: POST  
  This API rekeys the internal key in the key hierarchy for an SVM with a Google Cloud KMS configuration.  

* Endpoint: /security/gcp-kms/{uuid}/restore  
  HTTP methods: POST  
  This API restores the keys for an SVM from a configured Google Cloud KMS.  

* Endpoint: /security/ipsec/ca-certificates  
  HTTP methods: GET, POST  
  These APIs are for the collection of IPsec CA certificates configured for all SVMs.  

* Endpoint: /security/ipsec/ca-certificates/{svm.uuid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage the IPsec CA certificates configured for the specified SVM.  

* Endpoint: /security/key-manager-configs  
  HTTP methods: GET, PATCH  
  These APIs are used for key manager configurations.  

* Endpoint: /security/key-stores  
  HTTP methods: GET  
  This API retrieves keystores.  

* Endpoint: /security/ssh/svms  
  HTTP methods: GET  
  This API retrieves the SSH server configuration for all the SVMs.  

* Endpoint: /security/ssh/svms/{svm.uuid}  
  HTTP methods: GET, PATCH  
  These APIs manage the SSH server configuration for the specified SVM.  

* Endpoint: /storage/file/clone/split-loads  
  HTTP methods: GET  
  This API retrieves the clone split load of a node.  

* Endpoint: /storage/file/clone/split-loads/{node.uuid}  
  HTTP methods: GET, PATCH  
  These APIs manage Volume File Clone Split Load.  

* Endpoint: /storage/file/clone/split-status  
  HTTP methods: GET  
  This API retrieves file clone split status of all volumes in the node.  

* Endpoint: /storage/file/clone/split-status/{volume.uuid}  
  HTTP methods: GET  
  This API retrieves file clone split status of provided volume in the node.  

* Endpoint: /storage/file/clone/tokens  
  HTTP methods: GET, POST  
  These APIs manage tokens to reserve the split load.  

* Endpoint: /storage/file/clone/tokens/{node.uuid}/{uuid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage file clone tokens for the specified node.  

* Endpoint: /storage/ports/{node.uuid}/{name}  
  HTTP methods: PATCH  
  This API updates a storage port.  

* Endpoint: /storage/qos/workloads  
  HTTP methods: GET  
  This API retrieves a collection of QoS workloads.  

* Endpoint: /storage/qos/workloads/{uuid}  
  HTTP methods: GET  
  This API retrieves a specific QoS workload.  

* Endpoint: /storage/shelves/{uid}  
  HTTP methods: PATCH  
  This API updates a shelf location LED.  

* Endpoint: /storage/volumes/{volume.uuid}/top-metrics/clients  
  HTTP methods: GET  
  This API retrieves a list of clients with the most IO activity.  

* Endpoint: /storage/volumes/{volume.uuid}/top-metrics/directories  
  HTTP methods: GET  
  This API retrieves a list of directories with the most IO activity.  

* Endpoint: /storage/volumes/{volume.uuid}/top-metrics/files  
  HTTP methods: GET  
  This API retrieves a list of files with the most IO activity.  

* Endpoint: /storage/volumes/{volume.uuid}/top-metrics/users  
  HTTP methods: GET  
  This API retrieves a list of users with the most IO activity.  

* Endpoint: /storage/snaplock/compliance-clocks  
  HTTP methods: POST  
  This API initializes the SnapLock ComplianceClock.  

* Endpoint: /protocols/cifs/domains  
  HTTP methods: GET  
  This API retrieves the CIFS domain-related information of all SVMs.  

* Endpoint: /protocols/cifs/domains/{svm.uuid}  
  HTTP methods: GET  
  This API retrieves the CIFS domain-related information for the specified SVM.  

* Endpoint: /protocols​/cifs​/domains​/{svm.uuid}​/preferred-domain-controllers  
  HTTP methods: GET, POST  
  These APIs are for the CIFS domain preferred DC configuration of an SVM.  

* Endpoint: /protocols/cifs/domains/{svm.uuid}/preferred-domain-controllers/{fqdn}/{server_ip}  
  HTTP methods: GET, DELETE  
  These APIs manage the CIFS domain preferred DC configuration for the specified SVM and domain.  

* Endpoint: /protocols/cifs/local-groups/{svm.uuid}/{sid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage local group information for the specified group and SVM.  

* Endpoint: /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members  
  HTTP methods: GET, POST, DELETE  
  These APIs manage local users, Active Directory users and Active Directory groups which are members of the specified local group and SVM.  

* Endpoint: /protocols/cifs/local-groups/{svm.uuid}/{local_cifs_group.sid}/members/{name}  
  HTTP methods: GET, DELETE  
  These APIs manage the local user, Active Directory user and/or Active Directory group from the specified local group and SVM.  

* Endpoint: /protocols/cifs/local-users/{svm.uuid}/{sid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage local user information for the specified user and SVM.  

* Endpoint: /protocols/cifs/users-and-groups/bulk-import/{svm.uuid}  
  HTTP methods: GET, POST, PATCH  
  These APIs manage CIFS local users,groups and group memberships file from the specified URL.  

* Endpoint: /protocols/event-selectors  
  HTTP methods: GET, POST  
  These APIs manage S3 audit event-selector configurations for all SVMs.  

* Endpoint: /protocols/event-selectors/{svm.uuid}/{bucket}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage an S3 audit event selector configuration for an SVM.  

* Endpoint: /protocols/file-security/permissions/{svm.uuid}/{path}  
  HTTP methods: DELETE  
  This API removes all SLAG ACLs for specified path. Bulk deletion is supported only for SLAG.  

* Endpoint: /protocols/fpolicy/{svm.uuid}/connections  
  HTTP methods: GET  
  This API retrieves the statuses of FPolicy servers.  

* Endpoint: /protocols/fpolicy/{svm.uuid}/connections/{node.uuid}/{policy.name}/{server}  
  HTTP methods: GET, PATCH  
  These APIs manage the status of an FPolicy server.  

* Endpoint: /protocols/locks  
  HTTP methods: GET  
  This API retrieves locks details.  

* Endpoint: /protocols/locks/{uuid}  
  HTTP methods: GET, DELETE  
  These APIs manage locks for the specified Lock ID.  

* Endpoint: /protocols/s3audits  
  HTTP methods: GET, POST  
  These APIs manage S3 audit configuration.  

* Endpoint: /protocols/s3audits/{svm.uuid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage an S3 audit configuration for an SVM.  


## 9.9.1.0 library updates  
(2021-06-25)

** New endpoints **

* Endpoint: /name-services/unix-groups  
  HTTP methods: GET, POST  
  These APIs allow management of the UNIX groups for all of the SVMs.  

* Endpoint: /name-services/unix-groups/{svm.uuid}/{name}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage UNIX group information for the specified group and SVM.  

* Endpoint: /name-services/unix-groups/{svm.uuid}/{unix_group.name}/users  
  HTTP methods: POST  
  This API adds users to the specified UNIX group and SVM.  

* Endpoint: /name-services/unix-groups/{svm.uuid}/{unix_group.name}/users/{name}  
  HTTP methods: DELETE  
  This API deletes a user from the specified UNIX group.  

* Endpoint: /name-services/unix-users  
  HTTP methods: GET, POST  
  These APIs manage all local UNIX users and configuration for SVMs.  

* Endpoint: /name-services/unix-users/{svm.uuid}/{name}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage UNIX user information for the specified user and SVM.  

* Endpoint: /protocols/san/igroups/{igroup.uuid}/igroups  
  HTTP methods: GET,POST  
  These APIs manage nested initiator groups of an initiator group.  

* Endpoint: /protocols/san/igroups/{igroup.uuid}/igroups/{uuid}  
  HTTP methods: GET, DELETE  
  These APIs manage a nested initiator group of an initiator group.  

* Endpoint: /protocols/san/igroups/{igroup.uuid}/initiators/{name}  
  HTTP methods: PATCH  
  Updates an initiator of an initiator group. This API only supports modification of initiators owned directly by the initiator group. Initiators of nested initiator groups must be modified on the initiator group that directly owns the initiator.  

* Endpoint: /protocols/san/portsets  
  HTTP methods: GET, POST  
  These APIs are for portsets.  

* Endpoint: /protocols/san/portsets/{uuid}  
  HTTP methods: GET, DELETE  
  These APIs used for a portset.  

* Endpoint: /protocols/san/portsets/{portset.uuid}/interfaces  
  HTTP methods: GET, POST  
  These APIs are for interfaces of a portset.  

* Endpoint: /protocols/san/portsets/{portset.uuid}/interfaces/{uuid}  
  HTTP methods: GET, DELETE  
  These APIs are for a network interface of a portset.  

* Endpoint: /security/gcp-kms  
  HTTP methods: GET, POST  
  These APIs manage Google Cloud KMS configurations for all clusters and SVMs.  

* Endpoint: /security/gcp-kms/{uuid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs are for managing the Google Cloud KMS configuration for the SVM specified by the UUID.  

* Endpoint: /security/gcp-kms/{gcp_kms.uuid}/rekey-internal  
  HTTP methods: POST  
  This API rekeys the internal key in the key hierarchy for an SVM with a Google Cloud KMS configuration.  

* Endpoint: /security/gcp-kms/{gcp_kms.uuid}/restore  
  HTTP methods: POST  
  This API restores the keys for an SVM from a configured Google Cloud KMS.  

* Endpoint: /storage/bridges  
  HTTP methods: GET  
  This API retrieves a collection of bridges.  

* Endpoint: /storage/bridges/{wwn}  
  HTTP methods: GET  
  This API retrieves a specific bridge  

* Endpoint: /storage/flexcache/origins/{uuid}  
  HTTP methods: PATCH  
  This API modifies origin options for a origin volume in the cluster.  

* Endpoint: /storage/switches  
  HTTP methods: GET  
  This API retrieves a collection of storage switches.  

* Endpoint: /storage/switches/{name}  
  HTTP methods: GET  
  This API retrieves a specific storage switch.  

* Endpoint: /storage/tape-devices  
  HTTP methods: GET  
  This API retrieves a collection of tape devices.  

* Endpoint: /storage/tape-devices/{node.uuid}/{device_id}  
  HTTP methods: GET  
  This API retrieves a specific tape.  

* Endpoint: /protocols/ndmp/svms/{svm.uuid}/passwords/{user}  
  HTTP methods: GET  
  This API generates and retrieves the password for the specified NDMP user.  

* Endpoint: /protocols/cifs/local-groups  
  HTTP methods: GET, POST  
  These APIs are for the local groups for all of the SVMs.  

* Endpoint: /protocols/cifs/local-groups/{svm.uuid}/{group_sid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs are for local group information of the specified group and SVM.  

* Endpoint: /protocols/cifs/local-groups/{svm.uuid}/{local_group.group_sid}/members  
  HTTP methods: GET, POST, DELETE  
  These APIs manage local users, Active Directory users and Active Directory groups which are members of the specified local group and SVM.  

* Endpoint: /protocols/cifs/local-groups/{svm.uuid}/{local_group.group_sid}/members/{name}  
  HTTP methods: GET, DELETE  
  These APIs are for the local user, Active Directory user and/or Active Directory group from the specified local group and SVM.  

* Endpoint: /protocols/cifs/local-users  
  HTTP methods: GET, POST  
  These APIs are for local users of all of the SVMs.  

* Endpoint: /protocols/cifs/local-users/{svm.uuid}/{user_sid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage local user information for the specified user and SVM.  

* Endpoint: /protocols/cifs/sessions/{node.uuid}/{svm.uuid}/{identifier}/{connection_id}  
  HTTP methods: DELETE  
  This API deletes SMB session information on a node for an SVM.  

* Endpoint: /protocols/cifs/users-and-groups/privileges  
  HTTP methods: GET, POST  
  These APIs manage privileges of the specified local or Active Directory user or group and SVM.  

* Endpoint: /protocols/cifs/users-and-groups/privileges/{svm.uuid}/{name}  
  HTTP methods: GET, PATCH  
  These APIs are for privileges of the specified local or Active Directory user or group and SVM.  

* Endpoint: /protocols/file-security/permissions/{svm.uuid}/{path}  
  HTTP methods: GET, POST, PATCH  
  These APIs manage file permissions  

* Endpoint: /protocols/file-security/permissions/{svm.uuid}/{path}/acl  
  HTTP methods: POST, PATCH, DELETE  
  These APIs manage the new SACL/DACL ACL.  


## 9.8.0 RC1 library updates  
(2020-11-09)

** New **
** Fixed issues **

* [Bug ID 1349122](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1349122)

Due to a type mismatch between documentation and implementation, some endpoints were failing because of a validation error.

## ONTAP 9.8 REST API updates ##
All new ONTAP APIs have corresponding library resource objects which can be used
to perform the operations. See the `netapp_ontap.resources` package for details
about each of the objects and their fields.

For a summary of the changes in the ONTAP REST API between versions of ONTAP 9, see the [ONTAP 9 Release Notes](https://library.netapp.com/ecmdocs/ECMLP2492508/html/frameset.html).

** New endpoints **

* Endpoint: /cluster/firmware/history  
  HTTP methods: GET  
  This API retrieves the details history of firmware update requests for the cluster.  

* Endpoint: /cluster/licensing/capacity-pools  
  HTTP methods: GET  
  This API retrieves information about associations between ONTAP nodes in the cluster and capacity pool licenses. It can also report how much capacity each node is consuming from the pool.  

* Endpoint: /cluster/licensing/license-managers  
  HTTP methods: GET, PATCH  
  These APIs allow for managing information about the license manager associated with the cluster.  

* Endpoint: /cluster/mediators  
  HTTP methods: GET, POST, DELETE  
  These APIs allow for adding or removing a mediator to MetroCluster over IP configuration as well as retrieving the status of the existing mediator.  

* Endpoint: /cluster/metrocluster  
  HTTP methods: GET, POST, PATCH  
  These APIs allows for creating, performing operations, and retrieving relevant information pertaining to MetroCluster.  

* Endpoint: /cluster/metrocluster/diagnostics  
  HTTP methods: GET, POST
  This API can be used to initiate a MetroCluster diagnostics operation and fetch the results of a completed diagnostic operation.  

* Endpoint: /cluster/metrocluster/dr-groups  
  HTTP methods: GET, POST, DELETE  
  These APIs allow for creating, performing operations, and retrieving relevant information about MetroCluster DR groups.  

* Endpoint: /cluster/metrocluster/interconnects  
  HTTP methods: GET  
  This API retrieves information pertaining to MetroCluster interconnect status.  

* Endpoint: /cluster/metrocluster/nodes  
  HTTP methods: GET  
  This API retrieves details about MetroCluster nodes.  

* Endpoint: /cluster/metrocluster/operations  
  HTTP methods: GET  
  This API retrieves the list of MetroCluster operations on the local cluster.  

* Endpoint: /cluster/nodes/{uuid}/metrics  
  HTTP methods: GET  
  This API retrieves historical performance metrics for a node.  

* Endpoint: /cluster/software/upload  
  HTTP methods: POST  
  This API uploads a software or firmware package located on the local filesystem.  

* Endpoint: /network/ethernet/ports/{uuid}/metrics  
  HTTP methdos: GET  
  This API retrieves historical performance metrics for a port.  

* Endpoint: /network/ethernet/switch/ports  
  HTTP methods: GET  
  This API can be used to get the port information for an ethernet switch used in a cluster or storage networks. 

* Endpoint: /network/ethernet/switches  
  HTTP methods: GET, PATCH  
  These APIs can be used to retrieve and modify ethernet switches used for the cluster and/or storage networks.  

* Endpoint: /network/fc/interfaces/{uuid}/metrics  
  HTTP methods: GET  
  This API retrieves historical performance metrics for an FC interface.  

* Endpoint: /network/fc/ports/{uuid}/metrics  
  HTTP methods: GET  
  This API retrieves historical performance metrics for an FC port.  

* Endpoint: /network/ip/interfaces/{uuid}/metrics  
  HTTP methods: GET  
  This API retrieves historical performance metrics for an interface.  

* Endpoint: /network/ip/service-policies  
  HTTP methods: POST, PATCH, DELETE  
  These APIs allow for creating, modifying, and deleting a servicy policy for network interfaces.  

* Endpoint: /storage/namespaces/{uuid}/metrics  
  HTTP methods: GET  
  This API retrieves historical performance metrics for an NVMe namespace.  

* Endpoint: /security  
  HTTP methods: PATCH  
  This API updates the software FIPS mode or enables conversion of non-encrypted metadata volumes to encrypted metadata volumes and non-NAE aggregates to NAE aggregates.  

* Endpoint: /security/azure-key-vaults  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs allow for managing Azure Key Vaults on a cluster.  

* Endpoint: /security/azure-key-vaults/{azure_key_vault.uuid}/rekey-internal  
  HTTP methods: POST  
  This API rekeys the internal key in the key hierarchy for an SVM with and AKV configuration.  

* Endpoint: /security/azure-key-vaults/{azure_key_vault.uuid}/restore  
  HTTP methods: POST  
  This API restores the keys for an SVM from a configures AKV.  

* Endpoint: /security/certificate-signing-request  
  HTTP methods: POST  
  This API generates a Certificate Signing Request and a private key pair.  

* Endpoint: /security/gcp-kms  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs allow ONTAP to store encryption keys using Google Cloud Key Management Services.  

* Endpoint: /security/gcp-kms/{gcp_kms.uuid}/restore  
  HTTP methods: POST  
  This API restores the keys for an SVM from a configure Google Cloud Key Management Service.  

* Endpoint: /security/ipsec  
  HTTP methods: GET, PATCH  
  These APIs allow for retrieving and updating IPsec status.  

* Endpoint: /security/ipsec/policies  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs allow for creating, retrieving information about, and updating IPsec policies.  

* Endpoint: /security/ipsec/security-associations  
  HTTP methods: GET  
  This API retrieves the IPsec and IKE(Internet Key Exchange) security associations.  

* Endpoint: /storage/file/copy  
  HTTP methods: POST  
  This API starts a file copy operations which is only supported on flexible volumes.  

* Endpoint: /storage/file/move  
  HTTP methods: POST  
  This API starts a file move operation which is only supported on flexible volumes.  

* Endpoint: /storage/flexcache/flexcaches/{uuid}  
  HTTP methods: PATCH  
  This API prepopulates a FlexCache volume in the cluster.  

* Endpoint: /storage/monitored-files  
  HTTP methods: GET, POST, DELETE  
  These APIs allow for creating, deleting, and retrieving information about monitored files.  

* Endpoint: /storage/monitored-files/{monitored_file.uuid}/metrics  
  HTTP methods: GET  
  This API retrieves historical performance metrics for the monitored file.  

* Endpoint: /storage/snapshot-policies/{snapshot_policy.uuid}/schedules  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs perform operations related to Snapshot copy policy schedules.  

* Endpoint: /storage/volume-efficiency-policies  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs allow for configuring volume efficiency policies on a cluster.  

* Endpoint: /storage/volumes/{volume.uuid}/files/{path}  
  HTTP methods: POST, PATCH, DELETE  
  These APIs allow for creating files, modifying files, and deleting files on a volume.  

* Endpoint: /private/protocols/audit/audit-log-redirect  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs can be used to specify a dedicated SVM for all NAS auditing event log to reside in.  

* Endpoint: /protocols/cifs/sessions  
  HTTP methods: GET  
  This API retrieves the CIFS sessions information for all SVMs.  

* Endpoint: /protocols/cifs/sessions/{node.uuid}/{svm.uuid}/{identifier}/{connection_id}  
  HTTP methods: GET  
  This API retrieves SMB session information for a specific SMF connection of a SVM in a node.  
* Endpoint: /protocols/file-access-tracing/events  
  HTTP methods: GET, DELETE  
  These APIs retrieves or delete trace results for access allowed or denied events.  

* Endpoint: /protocols/file-access-tracing/filters  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs manage security trace filter entries.  

* Endpoint: /protocols/file-security/effective-permissions/{svm.uuid}/{path}  
  HTTP methods: GET  
  This API displays the effective permissions granted to a Windows or UNIX user on the specified file or folder path.  

* Endpoint: /private/manage/event-remediations  
  HTTP methods: GET, PATCH  
  These APIs allow for retrieving about and performing event management actions.  

* Endpoint: /protocols/s3/buckets  
  HTTP methods: POST    
  This API creates the S3 bucket configuration for an SVM.  

* Endpoint: /protocols/s3/buckets/{svm.uuid}/{uuid}  
  HTTP methods: GET, PATCH, DELETE  
  These APIs manage S3 bucket configurations for the specified SVM.  

* Endpoint: /protocols/s3/services/{svm.uuid}/groups  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs manage S3 group configurations for the specified SVM.  

* Endpoint: /protocols/s3/services/{svm.uuid}/metrics  
  HTTP methods: GET  
  This API retrieves historical performance metrics for the S3 protocol of an SVM.  

* Endpoint: /protocols/s4/services/{svm.uuid}/policies  
  HTTP methods: GET, POST, PATCH, DELETE  
  These APIs allow for configuring S3 policies for the specified SVM.  


## 9.7.3 library updates  
(2020-07-21)

**Fixed issues**

* [Bug ID 1322090](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1322090)  
  When polling jobs, the certificate verification setting was hard-coded to False, so it would behave the same regardless of how the user set it.

* [Bug ID 1322095](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1322095) 
  The get_collection() call using the connection parameter was not correctly setting the connection on the returned resource objects.


## 9.7.1 library updates  
(2020-04-06)

**New**

* A `count_collection()` method is now available on all resources which have a `get_collection()`. This method is a shortcut for getting only the number of items matching a query. For example: `Volume.count_collection(name="backup_vol*")` is roughly equivalent to `len(list(Volume.get_collection(name="backup_vol*")))`.

## 9.7.0 GA library updates  
(2020-01-23)

**Fixed issues**

* [Bug ID 1279507](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1279507)  
  When doing a find() with the fields query parameter, the library was not returning the specified fields, instead, all fields were being returned.

* [Bug ID 1291333](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1291333)  
  When 0 records are found in a Resource.find() call and LOG_ALL_API_CALLS is set to True, then an uncaught exception is raised.


## 9.7.0 RC1 library updates  
(2019-11-20)

**New**

* The application can now add its own custom headers for each request as part of the `netapp_ontap.host_connection.HostConnection` object.
* When passing verify=False to the HostConnection, the library will now disable urllib3's InsecureRequestWarning from logging messages.

**Incompatibilities**

* In prior versions, Resource.find() would raise an exception if no results were found as well as when more than one was found. In this version, when no results are found, None is returned instead of raising an exception. An exception is still raised when more than one result is found.

**Fixed issues**

* [Bug ID 1271450](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1271450)  
  The library doesn't allow sending a body in a DELETE request.

* [Bug ID 1263312](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1263312)  
  When POSTing or PATCHing some objects with embeded objects, fields might incorrectly be dropped from the request.

* [Bug ID 1275238](https://mysupport.netapp.com/NOW/cgi-bin/bol?Type=Detail&Display=1275238)  
  Retrieving and setting the "from" field of Autosupport object fails.

##ONTAP 9.7 REST API updates

All new ONTAP APIs have corresponding library resource objects which can be used
to perform the operations. See the `netapp_ontap.resources` package for details
about each of the objects and their fields.

For a summary of the changes in the ONTAP REST API between versions of ONTAP 9, see the [ONTAP 9 Release Notes](https://library.netapp.com/ecmdocs/ECMLP2492508/html/frameset.html).

**New endpoints** 

* Endpoint: /cluster/nodes/{uuid}  
    HTTP methods: DELETE  
    This API will remove a node from the cluster. 

* Endpoint: /cluster/ntp/keys/{id}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs allow for management of NTP server shared keys.

* Endpoint: /cluster/ntp/servers/{server}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs allow for management of keyed NTP servers.

* Endpoint: /cluster/software/download    
    HTTP methods: GET  
    This API allows monitoring the status of the image package download progress.

* Endpoint: /network/http-proxy/{uuid}  
    HTTP methods: GET, POST, PATCH, DELETE  
    This API allow configuration of an HTTP proxy for the cluster of SVM IP spaces.

* Endpoint: /network/ip/bgp/peer-groups/{uuid}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs manage information pertaining to the BGP peer-groups configured in the cluster.

* Endpoint: /protocols/san/fcp/services/{svm.uuid}/metrics  
    HTTP methods: GET  
    This API retrieves historical performance metrics for the FC Protocols service of an SVM.

* Endpoint: /protocos/san/iscsi/services/{svm.uuid}/metrics  
    HTTP methods: GET   
    This API retrieves history performance metrics for the iSCSI protocol of an SVM.

* Endpoint: /storage/luns/{uuid}/metrics  
    HTTP methods: GET  
    This API retrieves history performance metrics for a LUN.

* Endpoint: /protocls/nvme/services/{svm.uuid}/metrics 
    HTTP methods: GET  
    This API retrieve historical performance metrics for NVME protocol of an SVM.

* Endpoint: /support/configuration-backup/{node.uuid}/name  
    HTTP methods: GET, POST, DELETE  
    These APIs create, retrieve, and delete backup configuraiton for the cluster.

* Endpoint: /support/snmp/traphosts/{host}  
    HTTP methods: GET, POST, DELETE  
    These APIs configure SNMP traphosts which will receive SNMP traps from ONTAP.

* Endpoint: /support/snmp/users/{engine_id}/{name}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs configure SNMP users that are able to query for the ONTAP SNMP server.

* Endpoint: /security  
    HTTP methods: GET  
    This API retrieves information about the security configured on the cluster.

* Endpoint: /security/authentication/cluster/ad-proxy  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs configure which data SVM will be use to proxy cluster management AD authentication.

* Endpoint: /security/authentiation/publickeys/{owner.uuid}/{account.name}/{index}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs configure the public keys for user accounts.

* Endpoint: /security/key-managers/{source.uuid}/migrate  
    HTTP methods: POST  
    This API migrates the keys belonging to an SVM between the cluster's key manager and the SVM's key manager.

* Endpoint: /security/ssh  
    HTTP methods: GET, PATCH  
    This API manages the SSH server running in ONTAP.

* Endpoint: /storage/aggregates/{uuid}/metrics  
    HTTP methods: GET  
    This API provide historical performance metrics for the specified aggregate.

* Endpoint: /storage/disks  
    HTTP methods: PATCH  
    This API updates the encryption controls of self-encrypting disks.

* Endpoint: /storage/snapshot-policies/{snapshot-policy.uuid}/schedules/{uuid}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs manage the policies reqarding when snapshots are taken.

* Endpoint: /protocols/ndmp  
    HTTP methods: GET, PATCH  
    This API manages NDMP mode at either SVM-scope or node-scope.

* Endpoint: /protocols/ndmp/{node.uuid}  
    HTTP methods: GET, PATCH  
    This API manages node-scoped NDMP settings.

* Endpoint: /protocols/ndmp/sessions/{owner.uuid}/{session.id}  
    HTTP methods: GET, DELETE  
    These APIs manage diagnostics information on NDMP settings belonging to a specific SVM in the case of SVM-scope or to a specific node in the case of node-scope.

* Endpoint: /protocols/ndmp/svms/{svm.uuid}  
    HTTP methods: GET, PATCH  
    These APIs manage SVM-scoped NDMP settings.

* Endpoint: /storage/snaplock/audit-logs/{svm.uuid}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs manage the loggin policies for a snaplock volume.

* Endpoint: /storage/snaplock/compliance-clocks/{node.uuid}  
    HTTP methods: GET  
    This API manages the Compliance Clock of the system which determines the expiry time of the SnapLock objects in the system.

* Endpoint: /storage/snaplock/event-retention/operations/{id}  
    HTTP methods: GET, POST  
    These APIs display all Event Based Retentions (EBR) operations and allow for applying an EBR policy on a specified volume.

* Endpoint: /storage/snaplock/event-retention/policies/{policy.name}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs manage retention policies for snaplock files and directories.

* Endpoint: /storage/snaplock/files/{volume.uuid}/{path}  
    HTTP methods: GET, PATCH, DELETE  
    These APIs manage the SnapLock retention time of a file.

* Endpoint: /storage/snaplock/file-fingerprints/{id}  
    HTTP methods: GET, POST, DELETE  
    These APIs manage key information about snaplock files and volumes.

* Endpoint: /storage/snaplock/litigations/{id}  
    HTTP methods: GET, POST, DELETE  
    These APIs retain Compliance-mode WORM files for the duration of a litigation.

* Endpoint: /storage/snaplock/litigations/{litigation.id/files  
    HTTP methods: GET  
    This API displays the list of files under the specified litigation ID.

* Endpoint: /storage/snaplock/litigations/{litigation.id}/operations/{id}  
    HTTP methods: GET, POST, DELETE  
    This API manages the legal-hold operations for the specified litigation ID.

* Endpoint: /protocols/cifs/services/{svm.uuid}/metrics  
    HTTP methods: GET  
    This API retrieves history performance metrics for the CIFS protocol of an SVM.

* Endpoint: /protocols/nfs/connected-clients  
    HTTP methods: GET  
    This API provides a list of currently connected NFS clients or clients that can be connected but are currently idle.

* Endpoint: /protocols/nfs/services/{svm.uuid}/metrics  
    HTTP methods: GET  
    This API retrieves historical performance metrics for the NFS protocol of an SVM.

* Endpoint: /protocols/s3/buckets  
    HTTP methods: GET  
    This API retrieves all S3 buckets for all SVMs.

* Endpoint: /protocols/s3/services/{svm.uuid}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs manage S3 servers which will allow you to store objects in ONTAP using Amazon S3 protocol.

* Endpoint: /protocols/s3/services/{svm.uuid}/buckets/{uuid}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs manage S3 buckets which are a container of objects.

* Endpoint: /protocols/s3/services/{svm.uuid}/users/{name}  
    HTTP methods: GET, POST, PATCH, DELETE  
    These APIs manage S3 user accounts on the server. Buckets that are created are associate with a user.

## 9.6.0  
(2019-07-16)

Initial release of the library

# Copyright, trademarks, and feedback
## Copyright information
Copyright &copy; 2021 NetApp, Inc. All Rights Reserved. Printed in the U.S.

No part of this document covered by copyright may be reproduced in any form or by any means—graphic,
electronic, or mechanical, including photocopying, recording, taping, or storage in an electronic
retrieval system—without prior written permission of the copyright owner.

Software derived from copyrighted NetApp material is subject to the following license
and disclaimer:

THIS SOFTWARE IS PROVIDED BY NETAPP "AS IS" AND WITHOUT ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE, WHICH ARE HEREBY DISCLAIMED. IN NO EVENT SHALL NETAPP BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

NetApp reserves the right to change any products described herein at any time, and without notice.
NetApp assumes no responsibility or liability arising from the use of products described herein,
except as expressly agreed to in writing by NetApp. The use or purchase of this product does not
convey a license under any patent rights, trademark rights, or any other intellectual property
rights of NetApp. The product described in this manual may be protected by one or more U.S.
patents, foreign patents, or pending applications.

RESTRICTED RIGHTS LEGEND: Use, duplication,or disclosure by the government is subject to
restrictions as set forth in subparagraph (c)(1)(ii) of the Rights in Technical Data and
Computer Software clause at DFARS 252.277-7103 (October 1988) and FAR 52-227-19 (June 1987).

## Trademark information
NETAPP, the NETAPP logo, and the marks listed on the NetApp Trademarks page are trademarks of
NetApp, Inc. Other company and product names may be trademarks of their respective owners.
http://www.netapp.com/us/legal/netapptmlist.aspx

## Feedback
If you have questions about the library, suggestions, or find a bug, you may contact
by email.

<ng-ontap-rest-python-lib@netapp.com>

You can help us to improve the quality of our documentation by sending us your feedback.
If you have suggestions for improving this document, send us your comments by email.

<doccomments@netapp.com>

To help us direct your comments to the correct division, include in the subject line
the product name, version, and operating system.

If you want to be notified automatically when production-level documentation is released
or important changes are made to existing production-level documents,
follow Twitter account @NetAppDoc.

You can also contact us in the following ways:

NetApp, Inc., 1395 Crossman Ave, Sunnyvale, CA 94089 U.S.

Telephone: +1 (408) 822-6000

Fax: +1 (408) 822-4501

Support telephone: +1 (888) 463-8277
"""

from netapp_ontap.error import NetAppRestError
from netapp_ontap.host_connection import HostConnection
from netapp_ontap.response import NetAppResponse

__version__ = "9.10.1.0"
