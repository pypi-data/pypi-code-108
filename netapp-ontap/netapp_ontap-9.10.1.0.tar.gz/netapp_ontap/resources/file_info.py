r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API is used to read a file, write to a file, retrieve a list of files and directories, and retrieve or modify certain properties of files and directories. The path field is used to specify the path to the directory or file to be acted on. The path field requires using "%2E" to represent "." and "%2F" to represent "/" for the path provided.
## File data
Read and write data from/to a named file. To read a file, the Accept request HTTP header must be specified as multipart/form-data, and a value for the `length` query property, which represents the number of bytes to be read, must be specified. The API will fail if the length of data being read/written exceeds 1 MB. This API should only be used on normal files or streams associated with files. The results for other file types, such as LUNs is undefined.<br/>
The following APIs are used to read or write data to a file:

* GET     /api/storage/volumes/{volume.uuid}/files/{path}?byte_offset=0&length=40 -H "Accept: multipart/form-data"
* POST    /api/storage/volumes/{volume.uuid}/files/{path} -H "Content-Type: multipart/form-data" --form "file=the data to be written to the new file"
* PATCH   /api/storage/volumes/{volume.uuid}/files/{path}?byte_offset=10 -H "Content-Type: multipart/form-data" --form "file=the new data to be written or overwritten to the existing file starting at byte_offset"
## Listing directories and files
A list of files and directories and their properties can be retrieved for a specified path.<br/>
The following APIs are used to view a list of files and directories:

* GET       /api/storage/volumes/{volume.uuid}/files
* GET       /api/storage/volumes/{volume.uuid}/files/{path}
* GET       /api/storage/volumes/{volume.uuid}/files/{path}?fields=*
## File information
The metadata and detailed information about a single directory or file can be retrieved by setting the `return_metadata` query property to `true`. The information returned includes type, creation_time, modified_time, changed_time, accessed_time, unix_permissions, ownder_id, group_id, size, hard_links_count, inode_number, is_empty, bytes_used, unique_bytes, inode_generation, is_vm_aligned, is_junction, links, and analytics (if requested).<br/>
The following API is used to view the properties of a single file or directory:

* GET       /api/storage/volumes/{volume.uuid}/files/{path}?return_metadata=true
## File usage
Custom details about the usage of a file can be retrieved by specifying a value for the `byte_offset` and `length` query properties.<br/>
The following API is used to view the unique bytes, and bytes used, by a file based on the range defined by `byte_offset` and `length`:

* GET       /api/storage/volumes/{volume.uuid}/files/{path}?return_metadata=true&byte_offset={int}&length={int}
## Create a directory
The following API is used to create a directory:

* POST    /api/storage/volumes/{volume.uuid}/files/{path} -d '{ "type" : "directory", "unix-permissions" : "644"}'
## Delete an entire directory
A directory can be deleted. The behavior of this call is equivalent to rm -rf.<br/>
The following API is used to delete an entire directory:

* DELETE    /api/storage/volumes/{volume.uuid}/files/{path}?recurse=true
## Delete a file or an empty directory
The following API is used to delete a file or an empty directory:

* DELETE    /api/storage/volumes/{volume.uuid}/files/{path}
* DELETE    /api/storage/volumes/{volume.uuid}/files/{path}?recurse=false
## File system analytics
File system analytics provide a quick method for obtaining information summarizing properties of all files within any directory tree of a volume. When file system analytics are enabled on a volume, `analytics.*` fields may be requested, and will be populated in the response records corresponding to directories. The API does not support file system analytics for requests that are made beyond the boundary of the specified `volume.uuid`.<br/>
The following APIs are used to obtain analytics information for a directory:

* GET    /api/storage/volumes/{volume.uuid}/files/{path}?fields=analytics
* GET    /api/storage/volumes/{volume.uuid}/files/{path}?fields=**
## QoS
QoS policies and settings enforce Service Level Objectives (SLO) on a file. A pre-created QoS policy can be used by specifying the `qos.name` or `qos.uuid` properties.</br>
The following APIs are used to assign a QoS policy to a file:

* PATCH   /api/storage/volumes/{volume.uuid}/files/{path} -d '{ "qos_policy.name" : "policy" }'
* PATCH   /api/storage/volumes/{volume.uuid}/files/{path} -d '{ "qos_policy.uuid" : "b89bc5dd-94a3-11e8-a7a3-0050568edf84" }'
## Symlinks
The following APIs are used to create a symlink and read the contents of a symlink:

* POST   /api/storage/volumes/{volume.uuid}/files/{path}  -d '{ "target" : "directory2/file1" }'
* GET    /api/storage/volumes/{volume.uuid}/files/{path}?return_metadata=true&fields=target
## Rename a file or a directory
The following API can be used to rename a file or a directory. Note that you need to provide the path relative to the root of the volume in the `path` body parameter.

* PATCH   /api/storage/volumes/{volume.uuid}/files/{path} -d '{ "path" : "directory1/directory2" }'
* PATCH   /api/storage/volumes/{volume.uuid}/files/{path} -d '{ "path" : "directory1/directory2/file1" }'
## Examples
### Writing to a new file
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("54c06ce2-5430-11ea-90f9-005056a73aff")
    resource.post(hydrate=True, data="the data to be written to the new file")
    print(resource)

```

### Writing to an existing file
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("54c06ce2-5430-11ea-90f9-005056a73aff", path="aNewFile")
    resource.patch(hydrate=True, data="*here is a little more data", byte_offset=39)

```

### Reading a file
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("54c06ce2-5430-11ea-90f9-005056a73aff", path="aNewFile")
    resource.get(byte_offset=0, length=100)
    print(resource)

```

###  Creating a directory
You can use the POST request to create a directory.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658")
    resource.type = "directory"
    resource.unix_permissions = "644"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
FileInfo({"path": "dir1", "unix_permissions": 644, "type": "directory"})

```
</div>
</div>

### Creating a stream on a file
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("54c06ce2-5430-11ea-90f9-005056a73aff")
    resource.post(
        hydrate=True,
        data="the data to be written to the new file",
        overwrite=True,
        byte_offset=-1,
        stream_name="someStream",
    )
    print(resource)

```

###  Retrieving the list of files in a directory
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="d1/d2/d3")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d1%2Fd2%2Fd3%2F%2E"
                },
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2F%2E?return_metadata=true"
                },
            },
            "type": "directory",
            "name": ".",
        }
    ),
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d1%2Fd2%2Fd3%2F%2E%2E"
                },
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2F%2E%2E?return_metadata=true"
                },
            },
            "type": "directory",
            "name": "..",
        }
    ),
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2File1?return_metadata=true"
                }
            },
            "type": "file",
            "name": "f1",
        }
    ),
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d1%2Fd2%2Fd3%2Fd5"
                },
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2Fd5?return_metadata=true"
                },
            },
            "type": "directory",
            "name": "d5",
        }
    ),
]

```
</div>
</div>

###  Retrieving a list of files based on file type
You can filter the list of files you retrieve based on multiple file types by including a query parameter in the following format type="file|symlink"
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="d1/d2/d3")
    resource.get(type="file|directory")
    print(resource)

```
<div class="try_it_out">
<input id="example6_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example6_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example6_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d1%2Fd2%2Fd3%2F%2E"
                },
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2F%2E?return_metadata=true"
                },
            },
            "type": "directory",
            "name": ".",
        }
    ),
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d1%2Fd2%2Fd3%2F%2E%2E"
                },
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2F%2E%2E?return_metadata=true"
                },
            },
            "type": "directory",
            "name": "..",
        }
    ),
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2File1?return_metadata=true"
                }
            },
            "type": "file",
            "name": "f1",
        }
    ),
    FileInfo(
        {
            "path": "d1/d2/d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d1%2Fd2%2Fd3%2Fd5"
                },
                "metadata": {
                    "href": "/api/storage/volumes/e8274d79-3bba-11ea-b780-005056a7d72a/files/d1%2Fd2%2Fd3%2Fd5?return_metadata=true"
                },
            },
            "type": "directory",
            "name": "d5",
        }
    ),
]

```
</div>
</div>

###  Retrieving the properties of a directory or a file
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="d1/d2/d3/f1")
    resource.get(return_metadata=True)
    print(resource)

```
<div class="try_it_out">
<input id="example7_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example7_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example7_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "path": "d1/d2/d3/f1",
            "unique_bytes": 4096,
            "inode_generation": 214488325,
            "is_vm_aligned": False,
            "group_id": 30,
            "modified_time": "2019-06-12T21:27:28-04:00",
            "owner_id": 54738,
            "creation_time": "2019-06-12T21:27:28-04:00",
            "size": 200,
            "unix_permissions": 644,
            "inode_number": 1233,
            "accessed_time": "2019-06-12T21:27:28-04:00",
            "changed_time": "2019-06-12T21:27:28-04:00",
            "hard_links_count": 1,
            "bytes_used": 4096,
            "type": "file",
            "is_junction": False,
            "name": "",
        }
    )
]

```
</div>
</div>

###  Creating a symlink to a relative path
You can use the POST request to create a symlink.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658")
    resource.target = "d1/f1"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example8_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example8_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example8_result" class="try_it_out_content">
```
FileInfo({"path": "symlink1", "target": "d1/f1"})

```
</div>
</div>

###  Retrieving the target of a symlink
You can use the GET request to view the target of a symlink.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="symlink1")
    resource.get(return_metadata=True, fields="target")
    print(resource)

```
<div class="try_it_out">
<input id="example9_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example9_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example9_result" class="try_it_out_content">
```
[FileInfo({"path": "symlink1", "target": "d1/f1"})]

```
</div>
</div>

###  Retrieving the usage information for a file
You can use the GET request to retrieve the unique bytes held in a file with or without specifing the offset.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="f1")
    resource.get(return_metadata=True, byte_offset=100, length=200)
    print(resource)

```
<div class="try_it_out">
<input id="example10_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example10_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example10_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "path": "d1/d2/d3/f1",
            "unique_bytes": 4096,
            "inode_generation": 214488325,
            "is_vm_aligned": False,
            "group_id": 30,
            "modified_time": "2019-06-12T21:27:28-04:00",
            "owner_id": 54738,
            "creation_time": "2019-06-12T21:27:28-04:00",
            "size": 200,
            "unix_permissions": 644,
            "inode_number": 1233,
            "accessed_time": "2019-06-12T21:27:28-04:00",
            "changed_time": "2019-06-12T21:27:28-04:00",
            "hard_links_count": 1,
            "bytes_used": 4096,
            "type": "file",
            "is_junction": False,
        }
    )
]

```
</div>
</div>

###  Retrieving all information (including analytics) for a directory
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("1ef5d1b2-f9d7-11e9-8043-00505682f860", path="d1")
    resource.get(return_metadata=True, fields="**")
    print(resource)

```
<div class="try_it_out">
<input id="example11_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example11_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example11_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "analytics": {
                "subdir_count": 18,
                "by_modified_time": {
                    "bytes_used": {
                        "labels": [
                            "2019-W42",
                            "2019-W41",
                            "2019-W40",
                            "2019-W39",
                            "2019-W38",
                            "2019-10",
                            "2019-09",
                            "2019-08",
                            "2019-Q4",
                            "2019-Q3",
                            "2019-Q2",
                            "2019-Q1",
                            "2019",
                            "2018",
                            "2017",
                            "2016",
                            "--2015",
                            "unknown",
                        ],
                        "percentages": [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            1.48,
                            0.0,
                            6.7,
                            9.8,
                            0.0,
                            27.63,
                            29.55,
                            32.82,
                            90.0,
                            0.0,
                            0.0,
                            0.0,
                            10.0,
                            0.0,
                        ],
                        "values": [
                            0,
                            0,
                            0,
                            0,
                            3112960,
                            0,
                            14041088,
                            20545536,
                            0,
                            57933824,
                            61947904,
                            68804608,
                            188686336,
                            0,
                            0,
                            0,
                            20971520,
                            0,
                        ],
                    }
                },
                "by_accessed_time": {
                    "bytes_used": {
                        "labels": [
                            "2019-W42",
                            "2019-W41",
                            "2019-W40",
                            "2019-W39",
                            "2019-W38",
                            "2019-10",
                            "2019-09",
                            "2019-08",
                            "2019-Q4",
                            "2019-Q3",
                            "2019-Q2",
                            "2019-Q1",
                            "2019",
                            "2018",
                            "2017",
                            "2016",
                            "--2015",
                            "unknown",
                        ],
                        "percentages": [
                            49.01,
                            0.89,
                            0.59,
                            1.04,
                            0.74,
                            50.5,
                            4.31,
                            3.86,
                            50.5,
                            11.43,
                            15.45,
                            12.62,
                            90.0,
                            0.0,
                            0.0,
                            0.0,
                            10.0,
                            0.0,
                        ],
                        "values": [
                            102760448,
                            1867776,
                            1245184,
                            2179072,
                            1556480,
                            105873408,
                            9027584,
                            8093696,
                            105873408,
                            23969792,
                            32382976,
                            26460160,
                            188686336,
                            0,
                            0,
                            0,
                            20971520,
                            0,
                        ],
                    }
                },
                "bytes_used": 209657856,
                "file_count": 668,
            },
            "path": "d1",
            "inode_generation": 214514951,
            "is_vm_aligned": False,
            "group_id": 65533,
            "modified_time": "2019-10-28T23:10:30+00:00",
            "owner_id": 1002,
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/1ef5d1b2-f9d7-11e9-8043-00505682f860"
                    }
                },
                "uuid": "1ef5d1b2-f9d7-11e9-8043-00505682f860",
            },
            "creation_time": "2019-10-28T23:04:13+00:00",
            "size": 4096,
            "unix_permissions": 755,
            "is_empty": False,
            "inode_number": 96,
            "accessed_time": "2019-10-28T23:10:38+00:00",
            "changed_time": "2019-10-28T23:10:30+00:00",
            "hard_links_count": 5,
            "bytes_used": 4096,
            "type": "directory",
            "is_junction": False,
        }
    )
]

```
</div>
</div>

### Retrieving file system analytics information for a set of histogram buckets
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="d3")
    resource.get(
        type="directory",
        fields="analytics",
        **{"analytics.histogram_by_time_labels": "2019-Q3,2019-Q2,2019-Q1,2018-Q4"}
    )
    print(resource)

```
<div class="try_it_out">
<input id="example12_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example12_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example12_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "analytics": {
                "subdir_count": 14,
                "by_modified_time": {
                    "bytes_used": {
                        "percentages": [0.02, 12.17, 80.31, 0.02],
                        "values": [57344, 29720576, 196141056, 57344],
                    }
                },
                "by_accessed_time": {
                    "bytes_used": {
                        "percentages": [0.03, 99.97, 0.0, 0.0],
                        "values": [69632, 244170752, 0, 0],
                    }
                },
                "bytes_used": 244240384,
                "file_count": 44,
            },
            "path": "d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d3%2F%2E"
                },
                "metadata": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d3%2F%2E?return_metadata=true"
                },
            },
            "type": "directory",
            "name": ".",
        }
    ),
    FileInfo(
        {
            "analytics": {
                "subdir_count": 23,
                "by_modified_time": {
                    "bytes_used": {
                        "percentages": [0.0, 57.88, 7.07, 0.04],
                        "values": [61440, 1756479488, 214622208, 1191936],
                    }
                },
                "by_accessed_time": {
                    "bytes_used": {
                        "percentages": [0.01, 99.99, 0.0, 0.0],
                        "values": [282624, 3034292224, 0, 0],
                    }
                },
                "bytes_used": 3034574848,
                "file_count": 515,
            },
            "path": "d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d3%2F%2E%2E"
                },
                "metadata": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d3%2F%2E%2E?return_metadata=true"
                },
            },
            "type": "directory",
            "name": "..",
        }
    ),
    FileInfo(
        {
            "analytics": {
                "subdir_count": 4,
                "by_modified_time": {
                    "bytes_used": {
                        "percentages": [0.0, 62.2, 0.0, 0.0],
                        "values": [0, 29638656, 0, 0],
                    }
                },
                "by_accessed_time": {
                    "bytes_used": {
                        "percentages": [0.0, 100.0, 0.0, 0.0],
                        "values": [0, 47648768, 0, 0],
                    }
                },
                "bytes_used": 47648768,
                "file_count": 10,
            },
            "path": "d3",
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d3%2Fd5"
                },
                "metadata": {
                    "href": "/api/storage/volumes/cb6b1b39-8d21-11e9-b926-005056aca658/files/d3%2Fd5?return_metadata=true"
                },
            },
            "type": "directory",
            "name": "d5",
        }
    ),
]

```
</div>
</div>

### Identifying the largest subdirectories
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("1ef5d1b2-f9d7-11e9-8043-00505682f860", path="d1")
    resource.get(
        fields="analytics.bytes_used",
        type="directory",
        order_by="analytics.bytes_used desc",
    )
    print(resource)

```
<div class="try_it_out">
<input id="example13_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example13_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example13_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "analytics": {"bytes_used": 56623104},
            "path": "d1",
            "type": "directory",
            "name": "..",
        }
    ),
    FileInfo(
        {
            "analytics": {"bytes_used": 35651584},
            "path": "d1",
            "type": "directory",
            "name": ".",
        }
    ),
    FileInfo(
        {
            "analytics": {"bytes_used": 17825792},
            "path": "d1",
            "type": "directory",
            "name": "biggest",
        }
    ),
    FileInfo(
        {
            "analytics": {"bytes_used": 10485760},
            "path": "d1",
            "type": "directory",
            "name": "bigger",
        }
    ),
    FileInfo(
        {
            "analytics": {"bytes_used": 5242880},
            "path": "d1",
            "type": "directory",
            "name": "big",
        }
    ),
]

```
</div>
</div>

###  Assigning a QoS policy to a file
You can use the PATCH request to assign a QoS policy to a file.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="directory1/file1")
    resource.qos_policy = {"name": "policy"}
    resource.patch()

```

###  Retrieving QoS information for a file
You can use the GET request for all fields with return_metadata="true" to retrieve QoS information for the file.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="file")
    resource.get(return_metadata=True, fields="**")
    print(resource)

```
<div class="try_it_out">
<input id="example15_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example15_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example15_result" class="try_it_out_content">
```
[
    FileInfo(
        {
            "path": "file",
            "inode_generation": 219748425,
            "is_vm_aligned": False,
            "group_id": 0,
            "modified_time": "2020-03-24T18:15:40-04:00",
            "owner_id": 0,
            "qos_policy": {
                "name": "pg1",
                "uuid": "00725264-688f-11ea-8f10-005056a7b8ac",
            },
            "volume": {"uuid": "c05eb66a-685f-11ea-8508-005056a7b8ac"},
            "creation_time": "2020-03-17T10:58:40-04:00",
            "size": 1048576,
            "unix_permissions": 644,
            "inode_number": 96,
            "accessed_time": "2020-03-24T18:15:40-04:00",
            "changed_time": "2020-03-24T18:15:40-04:00",
            "hard_links_count": 2,
            "bytes_used": 1056768,
            "type": "lun",
            "is_junction": False,
            "is_snapshot": False,
        }
    )
]

```
</div>
</div>

###  Deleting an entire directory
You can use the DELETE request to remove an entire directory recursively.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo(
        "cb6b1b39-8d21-11e9-b926-05056aca658", path="directory1/directory2"
    )
    resource.delete(recurse=True)

```

###  Deleting an entire directory with specified throttling threshold
You can specify the maximum number of directory delete operations per second when removing an entire directory recursively.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo(
        "cb6b1b39-8d21-11e9-b926-05056aca658", path="directory1/directory2"
    )
    resource.delete(recurse=True, throttle_deletion=100)

```

###  Deleting an empty directory
You can use the DELETE request to remove an empty directory.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo(
        "cb6b1b39-8d21-11e9-b926-05056aca658", path="directory1/directory2"
    )
    resource.delete()

```

###  Deleting a file
You can use the DELETE request to remove a file.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo("cb6b1b39-8d21-11e9-b926-05056aca658", path="directory1/file2")
    resource.delete()

```

###  Renaming a file
You can use the PATCH request to rename a file.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo(
        "cb6b1b39-8d21-11e9-b926-05056aca658", path="directory1/directory2/file1"
    )
    resource.path = "directory1/file2"
    resource.patch()

```

###  Renaming a directory
You can use the PATCH request to rename a directory.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FileInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FileInfo(
        "cb6b1b39-8d21-11e9-b926-05056aca658", path="directory1/directory2"
    )
    resource.path = "d3/d4"
    resource.patch()

```

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


__all__ = ["FileInfo", "FileInfoSchema"]
__pdoc__ = {
    "FileInfoSchema.resource": False,
    "FileInfo.file_info_show": False,
    "FileInfo.file_info_create": False,
    "FileInfo.file_info_modify": False,
    "FileInfo.file_info_delete": False,
}


class FileInfoSchema(ResourceSchema):
    """The fields of the FileInfo object"""

    links = fields.Nested("netapp_ontap.models.file_info_links.FileInfoLinksSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the file_info. """

    accessed_time = ImpreciseDateTime(
        data_key="accessed_time",
    )
    r""" Last access time of the file in date-time format.

Example: 2019-06-12T15:00:16.000+0000 """

    analytics = fields.Nested("netapp_ontap.models.analytics_info.AnalyticsInfoSchema", data_key="analytics", unknown=EXCLUDE)
    r""" The analytics field of the file_info. """

    bytes_used = Size(
        data_key="bytes_used",
    )
    r""" The actual number of bytes used on disk by this file. If byte_offset and length parameters are specified, this will return the bytes used by the file within the given range.

Example: 4096 """

    changed_time = ImpreciseDateTime(
        data_key="changed_time",
    )
    r""" Last time data or attributes changed on the file in date-time format.

Example: 2019-06-12T15:00:16.000+0000 """

    constituent = fields.Nested("netapp_ontap.models.file_info_constituent.FileInfoConstituentSchema", data_key="constituent", unknown=EXCLUDE)
    r""" The constituent field of the file_info. """

    creation_time = ImpreciseDateTime(
        data_key="creation_time",
    )
    r""" Creation time of the file in date-time format.

Example: 2019-06-12T15:00:16.000+0000 """

    fill_enabled = fields.Boolean(
        data_key="fill_enabled",
    )
    r""" Returns "true" if the space reservation is enabled. The field overwrite_enabled must also be set to the same value as this field. """

    group_id = Size(
        data_key="group_id",
    )
    r""" The integer ID of the group of the file owner.

Example: 30 """

    hard_links_count = Size(
        data_key="hard_links_count",
    )
    r""" The number of hard links to the file.

Example: 1 """

    inode_generation = Size(
        data_key="inode_generation",
    )
    r""" Inode generation number.

Example: 214753547 """

    inode_number = Size(
        data_key="inode_number",
    )
    r""" The file inode number.

Example: 1695 """

    is_empty = fields.Boolean(
        data_key="is_empty",
    )
    r""" Specifies whether or not a directory is empty. A directory is considered empty if it only contains entries for "." and "..". This element is present if the file is a directory. In some special error cases, such as when the volume goes offline or when the directory is moved while retrieving this info, this field might not get set.

Example: false """

    is_junction = fields.Boolean(
        data_key="is_junction",
    )
    r""" Returns "true" if the directory is a junction.

Example: false """

    is_snapshot = fields.Boolean(
        data_key="is_snapshot",
    )
    r""" Returns "true" if the directory is a Snapshot copy.

Example: false """

    is_vm_aligned = fields.Boolean(
        data_key="is_vm_aligned",
    )
    r""" Returns true if the file is vm-aligned. A vm-aligned file is a file that is initially padded with zero-filled data so that its actual data starts at an offset other than zero. The amount by which the start offset is adjusted depends on the vm-align setting of the hosting volume.

Example: false """

    modified_time = ImpreciseDateTime(
        data_key="modified_time",
    )
    r""" Last data modification time of the file in date-time format.

Example: 2019-06-12T15:00:16.000+0000 """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the file.

Example: test_file """

    overwrite_enabled = fields.Boolean(
        data_key="overwrite_enabled",
    )
    r""" Returns "true" if the space reservation for overwrites is enabled. The field fill_enabled must also be set to the same value as this field. """

    owner_id = Size(
        data_key="owner_id",
    )
    r""" The integer ID of the file owner.

Example: 54738 """

    path = fields.Str(
        data_key="path",
    )
    r""" Path of the file.

Example: d1/d2/d3 """

    qos_policy = fields.Nested("netapp_ontap.models.file_info_qos_policy.FileInfoQosPolicySchema", data_key="qos_policy", unknown=EXCLUDE)
    r""" The qos_policy field of the file_info. """

    size = Size(
        data_key="size",
    )
    r""" The size of the file, in bytes.

Example: 200 """

    target = fields.Str(
        data_key="target",
    )
    r""" The relative or absolute path contained in a symlink, in the form <some>/<path>.

Example: some_directory/some_other_directory/some_file """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['file', 'directory', 'blockdev', 'chardev', 'symlink', 'socket', 'fifo', 'stream', 'lun']),
    )
    r""" Type of the file.

Valid choices:

* file
* directory
* blockdev
* chardev
* symlink
* socket
* fifo
* stream
* lun """

    unique_bytes = Size(
        data_key="unique_bytes",
    )
    r""" Number of bytes uniquely held by this file. If byte_offset and length parameters are specified, this will return bytes uniquely held by the file within the given range.

Example: 4096 """

    unix_permissions = Size(
        data_key="unix_permissions",
    )
    r""" UNIX permissions to be viewed as an octal number. It consists of 4 digits derived by adding up bits 4 (read), 2 (write), and 1 (execute). The first digit selects the set user ID(4), set group ID (2), and sticky (1) attributes. The second digit selects permissions for the owner of the file; the third selects permissions for other users in the same group; the fourth selects permissions for other users not in the group.

Example: 493 """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the file_info. """

    @property
    def resource(self):
        return FileInfo

    gettable_fields = [
        "links",
        "accessed_time",
        "analytics",
        "bytes_used",
        "changed_time",
        "constituent",
        "creation_time",
        "fill_enabled",
        "group_id",
        "hard_links_count",
        "inode_generation",
        "inode_number",
        "is_empty",
        "is_junction",
        "is_snapshot",
        "is_vm_aligned",
        "modified_time",
        "name",
        "overwrite_enabled",
        "owner_id",
        "path",
        "qos_policy",
        "size",
        "target",
        "type",
        "unique_bytes",
        "unix_permissions",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,accessed_time,analytics,bytes_used,changed_time,constituent,creation_time,fill_enabled,group_id,hard_links_count,inode_generation,inode_number,is_empty,is_junction,is_snapshot,is_vm_aligned,modified_time,name,overwrite_enabled,owner_id,path,qos_policy,size,target,type,unique_bytes,unix_permissions,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "analytics",
        "constituent",
        "fill_enabled",
        "is_empty",
        "name",
        "overwrite_enabled",
        "path",
        "qos_policy",
        "size",
        "target",
        "unix_permissions",
        "volume.name",
        "volume.uuid",
    ]
    """analytics,constituent,fill_enabled,is_empty,name,overwrite_enabled,path,qos_policy,size,target,unix_permissions,volume.name,volume.uuid,"""

    postable_fields = [
        "analytics",
        "constituent",
        "is_empty",
        "name",
        "path",
        "target",
        "type",
        "unix_permissions",
        "volume.name",
        "volume.uuid",
    ]
    """analytics,constituent,is_empty,name,path,target,type,unix_permissions,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FileInfo.get_collection(fields=field)]
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
            raise NetAppRestError("FileInfo modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FileInfo(Resource):
    r""" Information about a single file. """

    _schema = FileInfoSchema
    _path = "/api/storage/volumes/{volume[uuid]}/files"
    _keys = ["volume.uuid", "path"]
    _post_form_data_parameters = { 'data':'string', }
    _patch_form_data_parameters = { 'data':'string', }

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of files and directories for a given directory or returns only the properties of a single given directory or file of a volume.
### Expensive properties
There is an added cost to retrieving values for these properties.  They are not included by default in GET results and must be explicitly requested using the `fields` query property. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
  * `analytics`
  * `qos_policy.name`
  * `qos_policy.uuid`

### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file info show")
        def file_info_show(
            volume_uuid,
            accessed_time: Choices.define(_get_field_list("accessed_time"), cache_choices=True, inexact=True)=None,
            bytes_used: Choices.define(_get_field_list("bytes_used"), cache_choices=True, inexact=True)=None,
            changed_time: Choices.define(_get_field_list("changed_time"), cache_choices=True, inexact=True)=None,
            creation_time: Choices.define(_get_field_list("creation_time"), cache_choices=True, inexact=True)=None,
            fill_enabled: Choices.define(_get_field_list("fill_enabled"), cache_choices=True, inexact=True)=None,
            group_id: Choices.define(_get_field_list("group_id"), cache_choices=True, inexact=True)=None,
            hard_links_count: Choices.define(_get_field_list("hard_links_count"), cache_choices=True, inexact=True)=None,
            inode_generation: Choices.define(_get_field_list("inode_generation"), cache_choices=True, inexact=True)=None,
            inode_number: Choices.define(_get_field_list("inode_number"), cache_choices=True, inexact=True)=None,
            is_empty: Choices.define(_get_field_list("is_empty"), cache_choices=True, inexact=True)=None,
            is_junction: Choices.define(_get_field_list("is_junction"), cache_choices=True, inexact=True)=None,
            is_snapshot: Choices.define(_get_field_list("is_snapshot"), cache_choices=True, inexact=True)=None,
            is_vm_aligned: Choices.define(_get_field_list("is_vm_aligned"), cache_choices=True, inexact=True)=None,
            modified_time: Choices.define(_get_field_list("modified_time"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            overwrite_enabled: Choices.define(_get_field_list("overwrite_enabled"), cache_choices=True, inexact=True)=None,
            owner_id: Choices.define(_get_field_list("owner_id"), cache_choices=True, inexact=True)=None,
            path: Choices.define(_get_field_list("path"), cache_choices=True, inexact=True)=None,
            size: Choices.define(_get_field_list("size"), cache_choices=True, inexact=True)=None,
            target: Choices.define(_get_field_list("target"), cache_choices=True, inexact=True)=None,
            type: Choices.define(_get_field_list("type"), cache_choices=True, inexact=True)=None,
            unique_bytes: Choices.define(_get_field_list("unique_bytes"), cache_choices=True, inexact=True)=None,
            unix_permissions: Choices.define(_get_field_list("unix_permissions"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["accessed_time", "bytes_used", "changed_time", "creation_time", "fill_enabled", "group_id", "hard_links_count", "inode_generation", "inode_number", "is_empty", "is_junction", "is_snapshot", "is_vm_aligned", "modified_time", "name", "overwrite_enabled", "owner_id", "path", "size", "target", "type", "unique_bytes", "unix_permissions", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FileInfo resources

            Args:
                accessed_time: Last access time of the file in date-time format.
                bytes_used: The actual number of bytes used on disk by this file. If byte_offset and length parameters are specified, this will return the bytes used by the file within the given range.
                changed_time: Last time data or attributes changed on the file in date-time format.
                creation_time: Creation time of the file in date-time format.
                fill_enabled: Returns \"true\" if the space reservation is enabled. The field overwrite_enabled must also be set to the same value as this field.
                group_id: The integer ID of the group of the file owner.
                hard_links_count: The number of hard links to the file.
                inode_generation: Inode generation number.
                inode_number: The file inode number.
                is_empty: Specifies whether or not a directory is empty. A directory is considered empty if it only contains entries for \".\" and \"..\". This element is present if the file is a directory. In some special error cases, such as when the volume goes offline or when the directory is moved while retrieving this info, this field might not get set.
                is_junction: Returns \"true\" if the directory is a junction.
                is_snapshot: Returns \"true\" if the directory is a Snapshot copy.
                is_vm_aligned: Returns true if the file is vm-aligned. A vm-aligned file is a file that is initially padded with zero-filled data so that its actual data starts at an offset other than zero. The amount by which the start offset is adjusted depends on the vm-align setting of the hosting volume.
                modified_time: Last data modification time of the file in date-time format.
                name: Name of the file.
                overwrite_enabled: Returns \"true\" if the space reservation for overwrites is enabled. The field fill_enabled must also be set to the same value as this field.
                owner_id: The integer ID of the file owner.
                path: Path of the file.
                size: The size of the file, in bytes.
                target: The relative or absolute path contained in a symlink, in the form <some>/<path>.
                type: Type of the file.
                unique_bytes: Number of bytes uniquely held by this file. If byte_offset and length parameters are specified, this will return bytes uniquely held by the file within the given range.
                unix_permissions: UNIX permissions to be viewed as an octal number. It consists of 4 digits derived by adding up bits 4 (read), 2 (write), and 1 (execute). The first digit selects the set user ID(4), set group ID (2), and sticky (1) attributes. The second digit selects permissions for the owner of the file; the third selects permissions for other users in the same group; the fourth selects permissions for other users not in the group.
            """

            kwargs = {}
            if accessed_time is not None:
                kwargs["accessed_time"] = accessed_time
            if bytes_used is not None:
                kwargs["bytes_used"] = bytes_used
            if changed_time is not None:
                kwargs["changed_time"] = changed_time
            if creation_time is not None:
                kwargs["creation_time"] = creation_time
            if fill_enabled is not None:
                kwargs["fill_enabled"] = fill_enabled
            if group_id is not None:
                kwargs["group_id"] = group_id
            if hard_links_count is not None:
                kwargs["hard_links_count"] = hard_links_count
            if inode_generation is not None:
                kwargs["inode_generation"] = inode_generation
            if inode_number is not None:
                kwargs["inode_number"] = inode_number
            if is_empty is not None:
                kwargs["is_empty"] = is_empty
            if is_junction is not None:
                kwargs["is_junction"] = is_junction
            if is_snapshot is not None:
                kwargs["is_snapshot"] = is_snapshot
            if is_vm_aligned is not None:
                kwargs["is_vm_aligned"] = is_vm_aligned
            if modified_time is not None:
                kwargs["modified_time"] = modified_time
            if name is not None:
                kwargs["name"] = name
            if overwrite_enabled is not None:
                kwargs["overwrite_enabled"] = overwrite_enabled
            if owner_id is not None:
                kwargs["owner_id"] = owner_id
            if path is not None:
                kwargs["path"] = path
            if size is not None:
                kwargs["size"] = size
            if target is not None:
                kwargs["target"] = target
            if type is not None:
                kwargs["type"] = type
            if unique_bytes is not None:
                kwargs["unique_bytes"] = unique_bytes
            if unix_permissions is not None:
                kwargs["unix_permissions"] = unix_permissions
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FileInfo.get_collection(
                volume_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FileInfo resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FileInfo"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Writes to an existing file with the supplied data or modifies the size, name, space reservation information, QoS policy, or hole range information of a file. Query-based PATCH operations are not supported.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FileInfo"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FileInfo"], NetAppResponse]:
        r"""Creates a new file with the supplied data, creates a new directory or creates a new symlink.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["FileInfo"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an existing file or directory. Query-based DELETE operations are not supported.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of files and directories for a given directory or returns only the properties of a single given directory or file of a volume.
### Expensive properties
There is an added cost to retrieving values for these properties.  They are not included by default in GET results and must be explicitly requested using the `fields` query property. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
  * `analytics`
  * `qos_policy.name`
  * `qos_policy.uuid`

### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a list of files and directories for a given directory or returns only the properties of a single given directory or file of a volume.
### Expensive properties
There is an added cost to retrieving values for these properties.  They are not included by default in GET results and must be explicitly requested using the `fields` query property. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
  * `analytics`
  * `qos_policy.name`
  * `qos_policy.uuid`

### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
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
        r"""Creates a new file with the supplied data, creates a new directory or creates a new symlink.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file info create")
        async def file_info_create(
            volume_uuid,
            links: dict = None,
            accessed_time: datetime = None,
            analytics: dict = None,
            bytes_used: Size = None,
            changed_time: datetime = None,
            constituent: dict = None,
            creation_time: datetime = None,
            fill_enabled: bool = None,
            group_id: Size = None,
            hard_links_count: Size = None,
            inode_generation: Size = None,
            inode_number: Size = None,
            is_empty: bool = None,
            is_junction: bool = None,
            is_snapshot: bool = None,
            is_vm_aligned: bool = None,
            modified_time: datetime = None,
            name: str = None,
            overwrite_enabled: bool = None,
            owner_id: Size = None,
            path: str = None,
            qos_policy: dict = None,
            size: Size = None,
            target: str = None,
            type: str = None,
            unique_bytes: Size = None,
            unix_permissions: Size = None,
            volume: dict = None,
        ) -> ResourceTable:
            """Create an instance of a FileInfo resource

            Args:
                links: 
                accessed_time: Last access time of the file in date-time format.
                analytics: 
                bytes_used: The actual number of bytes used on disk by this file. If byte_offset and length parameters are specified, this will return the bytes used by the file within the given range.
                changed_time: Last time data or attributes changed on the file in date-time format.
                constituent: 
                creation_time: Creation time of the file in date-time format.
                fill_enabled: Returns \"true\" if the space reservation is enabled. The field overwrite_enabled must also be set to the same value as this field.
                group_id: The integer ID of the group of the file owner.
                hard_links_count: The number of hard links to the file.
                inode_generation: Inode generation number.
                inode_number: The file inode number.
                is_empty: Specifies whether or not a directory is empty. A directory is considered empty if it only contains entries for \".\" and \"..\". This element is present if the file is a directory. In some special error cases, such as when the volume goes offline or when the directory is moved while retrieving this info, this field might not get set.
                is_junction: Returns \"true\" if the directory is a junction.
                is_snapshot: Returns \"true\" if the directory is a Snapshot copy.
                is_vm_aligned: Returns true if the file is vm-aligned. A vm-aligned file is a file that is initially padded with zero-filled data so that its actual data starts at an offset other than zero. The amount by which the start offset is adjusted depends on the vm-align setting of the hosting volume.
                modified_time: Last data modification time of the file in date-time format.
                name: Name of the file.
                overwrite_enabled: Returns \"true\" if the space reservation for overwrites is enabled. The field fill_enabled must also be set to the same value as this field.
                owner_id: The integer ID of the file owner.
                path: Path of the file.
                qos_policy: 
                size: The size of the file, in bytes.
                target: The relative or absolute path contained in a symlink, in the form <some>/<path>.
                type: Type of the file.
                unique_bytes: Number of bytes uniquely held by this file. If byte_offset and length parameters are specified, this will return bytes uniquely held by the file within the given range.
                unix_permissions: UNIX permissions to be viewed as an octal number. It consists of 4 digits derived by adding up bits 4 (read), 2 (write), and 1 (execute). The first digit selects the set user ID(4), set group ID (2), and sticky (1) attributes. The second digit selects permissions for the owner of the file; the third selects permissions for other users in the same group; the fourth selects permissions for other users not in the group.
                volume: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if accessed_time is not None:
                kwargs["accessed_time"] = accessed_time
            if analytics is not None:
                kwargs["analytics"] = analytics
            if bytes_used is not None:
                kwargs["bytes_used"] = bytes_used
            if changed_time is not None:
                kwargs["changed_time"] = changed_time
            if constituent is not None:
                kwargs["constituent"] = constituent
            if creation_time is not None:
                kwargs["creation_time"] = creation_time
            if fill_enabled is not None:
                kwargs["fill_enabled"] = fill_enabled
            if group_id is not None:
                kwargs["group_id"] = group_id
            if hard_links_count is not None:
                kwargs["hard_links_count"] = hard_links_count
            if inode_generation is not None:
                kwargs["inode_generation"] = inode_generation
            if inode_number is not None:
                kwargs["inode_number"] = inode_number
            if is_empty is not None:
                kwargs["is_empty"] = is_empty
            if is_junction is not None:
                kwargs["is_junction"] = is_junction
            if is_snapshot is not None:
                kwargs["is_snapshot"] = is_snapshot
            if is_vm_aligned is not None:
                kwargs["is_vm_aligned"] = is_vm_aligned
            if modified_time is not None:
                kwargs["modified_time"] = modified_time
            if name is not None:
                kwargs["name"] = name
            if overwrite_enabled is not None:
                kwargs["overwrite_enabled"] = overwrite_enabled
            if owner_id is not None:
                kwargs["owner_id"] = owner_id
            if path is not None:
                kwargs["path"] = path
            if qos_policy is not None:
                kwargs["qos_policy"] = qos_policy
            if size is not None:
                kwargs["size"] = size
            if target is not None:
                kwargs["target"] = target
            if type is not None:
                kwargs["type"] = type
            if unique_bytes is not None:
                kwargs["unique_bytes"] = unique_bytes
            if unix_permissions is not None:
                kwargs["unix_permissions"] = unix_permissions
            if volume is not None:
                kwargs["volume"] = volume

            resource = FileInfo(
                volume_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FileInfo: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Writes to an existing file with the supplied data or modifies the size, name, space reservation information, QoS policy, or hole range information of a file. Query-based PATCH operations are not supported.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file info modify")
        async def file_info_modify(
            volume_uuid,
            accessed_time: datetime = None,
            query_accessed_time: datetime = None,
            bytes_used: Size = None,
            query_bytes_used: Size = None,
            changed_time: datetime = None,
            query_changed_time: datetime = None,
            creation_time: datetime = None,
            query_creation_time: datetime = None,
            fill_enabled: bool = None,
            query_fill_enabled: bool = None,
            group_id: Size = None,
            query_group_id: Size = None,
            hard_links_count: Size = None,
            query_hard_links_count: Size = None,
            inode_generation: Size = None,
            query_inode_generation: Size = None,
            inode_number: Size = None,
            query_inode_number: Size = None,
            is_empty: bool = None,
            query_is_empty: bool = None,
            is_junction: bool = None,
            query_is_junction: bool = None,
            is_snapshot: bool = None,
            query_is_snapshot: bool = None,
            is_vm_aligned: bool = None,
            query_is_vm_aligned: bool = None,
            modified_time: datetime = None,
            query_modified_time: datetime = None,
            name: str = None,
            query_name: str = None,
            overwrite_enabled: bool = None,
            query_overwrite_enabled: bool = None,
            owner_id: Size = None,
            query_owner_id: Size = None,
            path: str = None,
            query_path: str = None,
            size: Size = None,
            query_size: Size = None,
            target: str = None,
            query_target: str = None,
            type: str = None,
            query_type: str = None,
            unique_bytes: Size = None,
            query_unique_bytes: Size = None,
            unix_permissions: Size = None,
            query_unix_permissions: Size = None,
        ) -> ResourceTable:
            """Modify an instance of a FileInfo resource

            Args:
                accessed_time: Last access time of the file in date-time format.
                query_accessed_time: Last access time of the file in date-time format.
                bytes_used: The actual number of bytes used on disk by this file. If byte_offset and length parameters are specified, this will return the bytes used by the file within the given range.
                query_bytes_used: The actual number of bytes used on disk by this file. If byte_offset and length parameters are specified, this will return the bytes used by the file within the given range.
                changed_time: Last time data or attributes changed on the file in date-time format.
                query_changed_time: Last time data or attributes changed on the file in date-time format.
                creation_time: Creation time of the file in date-time format.
                query_creation_time: Creation time of the file in date-time format.
                fill_enabled: Returns \"true\" if the space reservation is enabled. The field overwrite_enabled must also be set to the same value as this field.
                query_fill_enabled: Returns \"true\" if the space reservation is enabled. The field overwrite_enabled must also be set to the same value as this field.
                group_id: The integer ID of the group of the file owner.
                query_group_id: The integer ID of the group of the file owner.
                hard_links_count: The number of hard links to the file.
                query_hard_links_count: The number of hard links to the file.
                inode_generation: Inode generation number.
                query_inode_generation: Inode generation number.
                inode_number: The file inode number.
                query_inode_number: The file inode number.
                is_empty: Specifies whether or not a directory is empty. A directory is considered empty if it only contains entries for \".\" and \"..\". This element is present if the file is a directory. In some special error cases, such as when the volume goes offline or when the directory is moved while retrieving this info, this field might not get set.
                query_is_empty: Specifies whether or not a directory is empty. A directory is considered empty if it only contains entries for \".\" and \"..\". This element is present if the file is a directory. In some special error cases, such as when the volume goes offline or when the directory is moved while retrieving this info, this field might not get set.
                is_junction: Returns \"true\" if the directory is a junction.
                query_is_junction: Returns \"true\" if the directory is a junction.
                is_snapshot: Returns \"true\" if the directory is a Snapshot copy.
                query_is_snapshot: Returns \"true\" if the directory is a Snapshot copy.
                is_vm_aligned: Returns true if the file is vm-aligned. A vm-aligned file is a file that is initially padded with zero-filled data so that its actual data starts at an offset other than zero. The amount by which the start offset is adjusted depends on the vm-align setting of the hosting volume.
                query_is_vm_aligned: Returns true if the file is vm-aligned. A vm-aligned file is a file that is initially padded with zero-filled data so that its actual data starts at an offset other than zero. The amount by which the start offset is adjusted depends on the vm-align setting of the hosting volume.
                modified_time: Last data modification time of the file in date-time format.
                query_modified_time: Last data modification time of the file in date-time format.
                name: Name of the file.
                query_name: Name of the file.
                overwrite_enabled: Returns \"true\" if the space reservation for overwrites is enabled. The field fill_enabled must also be set to the same value as this field.
                query_overwrite_enabled: Returns \"true\" if the space reservation for overwrites is enabled. The field fill_enabled must also be set to the same value as this field.
                owner_id: The integer ID of the file owner.
                query_owner_id: The integer ID of the file owner.
                path: Path of the file.
                query_path: Path of the file.
                size: The size of the file, in bytes.
                query_size: The size of the file, in bytes.
                target: The relative or absolute path contained in a symlink, in the form <some>/<path>.
                query_target: The relative or absolute path contained in a symlink, in the form <some>/<path>.
                type: Type of the file.
                query_type: Type of the file.
                unique_bytes: Number of bytes uniquely held by this file. If byte_offset and length parameters are specified, this will return bytes uniquely held by the file within the given range.
                query_unique_bytes: Number of bytes uniquely held by this file. If byte_offset and length parameters are specified, this will return bytes uniquely held by the file within the given range.
                unix_permissions: UNIX permissions to be viewed as an octal number. It consists of 4 digits derived by adding up bits 4 (read), 2 (write), and 1 (execute). The first digit selects the set user ID(4), set group ID (2), and sticky (1) attributes. The second digit selects permissions for the owner of the file; the third selects permissions for other users in the same group; the fourth selects permissions for other users not in the group.
                query_unix_permissions: UNIX permissions to be viewed as an octal number. It consists of 4 digits derived by adding up bits 4 (read), 2 (write), and 1 (execute). The first digit selects the set user ID(4), set group ID (2), and sticky (1) attributes. The second digit selects permissions for the owner of the file; the third selects permissions for other users in the same group; the fourth selects permissions for other users not in the group.
            """

            kwargs = {}
            changes = {}
            if query_accessed_time is not None:
                kwargs["accessed_time"] = query_accessed_time
            if query_bytes_used is not None:
                kwargs["bytes_used"] = query_bytes_used
            if query_changed_time is not None:
                kwargs["changed_time"] = query_changed_time
            if query_creation_time is not None:
                kwargs["creation_time"] = query_creation_time
            if query_fill_enabled is not None:
                kwargs["fill_enabled"] = query_fill_enabled
            if query_group_id is not None:
                kwargs["group_id"] = query_group_id
            if query_hard_links_count is not None:
                kwargs["hard_links_count"] = query_hard_links_count
            if query_inode_generation is not None:
                kwargs["inode_generation"] = query_inode_generation
            if query_inode_number is not None:
                kwargs["inode_number"] = query_inode_number
            if query_is_empty is not None:
                kwargs["is_empty"] = query_is_empty
            if query_is_junction is not None:
                kwargs["is_junction"] = query_is_junction
            if query_is_snapshot is not None:
                kwargs["is_snapshot"] = query_is_snapshot
            if query_is_vm_aligned is not None:
                kwargs["is_vm_aligned"] = query_is_vm_aligned
            if query_modified_time is not None:
                kwargs["modified_time"] = query_modified_time
            if query_name is not None:
                kwargs["name"] = query_name
            if query_overwrite_enabled is not None:
                kwargs["overwrite_enabled"] = query_overwrite_enabled
            if query_owner_id is not None:
                kwargs["owner_id"] = query_owner_id
            if query_path is not None:
                kwargs["path"] = query_path
            if query_size is not None:
                kwargs["size"] = query_size
            if query_target is not None:
                kwargs["target"] = query_target
            if query_type is not None:
                kwargs["type"] = query_type
            if query_unique_bytes is not None:
                kwargs["unique_bytes"] = query_unique_bytes
            if query_unix_permissions is not None:
                kwargs["unix_permissions"] = query_unix_permissions

            if accessed_time is not None:
                changes["accessed_time"] = accessed_time
            if bytes_used is not None:
                changes["bytes_used"] = bytes_used
            if changed_time is not None:
                changes["changed_time"] = changed_time
            if creation_time is not None:
                changes["creation_time"] = creation_time
            if fill_enabled is not None:
                changes["fill_enabled"] = fill_enabled
            if group_id is not None:
                changes["group_id"] = group_id
            if hard_links_count is not None:
                changes["hard_links_count"] = hard_links_count
            if inode_generation is not None:
                changes["inode_generation"] = inode_generation
            if inode_number is not None:
                changes["inode_number"] = inode_number
            if is_empty is not None:
                changes["is_empty"] = is_empty
            if is_junction is not None:
                changes["is_junction"] = is_junction
            if is_snapshot is not None:
                changes["is_snapshot"] = is_snapshot
            if is_vm_aligned is not None:
                changes["is_vm_aligned"] = is_vm_aligned
            if modified_time is not None:
                changes["modified_time"] = modified_time
            if name is not None:
                changes["name"] = name
            if overwrite_enabled is not None:
                changes["overwrite_enabled"] = overwrite_enabled
            if owner_id is not None:
                changes["owner_id"] = owner_id
            if path is not None:
                changes["path"] = path
            if size is not None:
                changes["size"] = size
            if target is not None:
                changes["target"] = target
            if type is not None:
                changes["type"] = type
            if unique_bytes is not None:
                changes["unique_bytes"] = unique_bytes
            if unix_permissions is not None:
                changes["unix_permissions"] = unix_permissions

            if hasattr(FileInfo, "find"):
                resource = FileInfo.find(
                    volume_uuid,
                    **kwargs
                )
            else:
                resource = FileInfo(volume_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FileInfo: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an existing file or directory. Query-based DELETE operations are not supported.
### Learn more
* [`DOC /storage/volumes/{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path})"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="file info delete")
        async def file_info_delete(
            volume_uuid,
            accessed_time: datetime = None,
            bytes_used: Size = None,
            changed_time: datetime = None,
            creation_time: datetime = None,
            fill_enabled: bool = None,
            group_id: Size = None,
            hard_links_count: Size = None,
            inode_generation: Size = None,
            inode_number: Size = None,
            is_empty: bool = None,
            is_junction: bool = None,
            is_snapshot: bool = None,
            is_vm_aligned: bool = None,
            modified_time: datetime = None,
            name: str = None,
            overwrite_enabled: bool = None,
            owner_id: Size = None,
            path: str = None,
            size: Size = None,
            target: str = None,
            type: str = None,
            unique_bytes: Size = None,
            unix_permissions: Size = None,
        ) -> None:
            """Delete an instance of a FileInfo resource

            Args:
                accessed_time: Last access time of the file in date-time format.
                bytes_used: The actual number of bytes used on disk by this file. If byte_offset and length parameters are specified, this will return the bytes used by the file within the given range.
                changed_time: Last time data or attributes changed on the file in date-time format.
                creation_time: Creation time of the file in date-time format.
                fill_enabled: Returns \"true\" if the space reservation is enabled. The field overwrite_enabled must also be set to the same value as this field.
                group_id: The integer ID of the group of the file owner.
                hard_links_count: The number of hard links to the file.
                inode_generation: Inode generation number.
                inode_number: The file inode number.
                is_empty: Specifies whether or not a directory is empty. A directory is considered empty if it only contains entries for \".\" and \"..\". This element is present if the file is a directory. In some special error cases, such as when the volume goes offline or when the directory is moved while retrieving this info, this field might not get set.
                is_junction: Returns \"true\" if the directory is a junction.
                is_snapshot: Returns \"true\" if the directory is a Snapshot copy.
                is_vm_aligned: Returns true if the file is vm-aligned. A vm-aligned file is a file that is initially padded with zero-filled data so that its actual data starts at an offset other than zero. The amount by which the start offset is adjusted depends on the vm-align setting of the hosting volume.
                modified_time: Last data modification time of the file in date-time format.
                name: Name of the file.
                overwrite_enabled: Returns \"true\" if the space reservation for overwrites is enabled. The field fill_enabled must also be set to the same value as this field.
                owner_id: The integer ID of the file owner.
                path: Path of the file.
                size: The size of the file, in bytes.
                target: The relative or absolute path contained in a symlink, in the form <some>/<path>.
                type: Type of the file.
                unique_bytes: Number of bytes uniquely held by this file. If byte_offset and length parameters are specified, this will return bytes uniquely held by the file within the given range.
                unix_permissions: UNIX permissions to be viewed as an octal number. It consists of 4 digits derived by adding up bits 4 (read), 2 (write), and 1 (execute). The first digit selects the set user ID(4), set group ID (2), and sticky (1) attributes. The second digit selects permissions for the owner of the file; the third selects permissions for other users in the same group; the fourth selects permissions for other users not in the group.
            """

            kwargs = {}
            if accessed_time is not None:
                kwargs["accessed_time"] = accessed_time
            if bytes_used is not None:
                kwargs["bytes_used"] = bytes_used
            if changed_time is not None:
                kwargs["changed_time"] = changed_time
            if creation_time is not None:
                kwargs["creation_time"] = creation_time
            if fill_enabled is not None:
                kwargs["fill_enabled"] = fill_enabled
            if group_id is not None:
                kwargs["group_id"] = group_id
            if hard_links_count is not None:
                kwargs["hard_links_count"] = hard_links_count
            if inode_generation is not None:
                kwargs["inode_generation"] = inode_generation
            if inode_number is not None:
                kwargs["inode_number"] = inode_number
            if is_empty is not None:
                kwargs["is_empty"] = is_empty
            if is_junction is not None:
                kwargs["is_junction"] = is_junction
            if is_snapshot is not None:
                kwargs["is_snapshot"] = is_snapshot
            if is_vm_aligned is not None:
                kwargs["is_vm_aligned"] = is_vm_aligned
            if modified_time is not None:
                kwargs["modified_time"] = modified_time
            if name is not None:
                kwargs["name"] = name
            if overwrite_enabled is not None:
                kwargs["overwrite_enabled"] = overwrite_enabled
            if owner_id is not None:
                kwargs["owner_id"] = owner_id
            if path is not None:
                kwargs["path"] = path
            if size is not None:
                kwargs["size"] = size
            if target is not None:
                kwargs["target"] = target
            if type is not None:
                kwargs["type"] = type
            if unique_bytes is not None:
                kwargs["unique_bytes"] = unique_bytes
            if unix_permissions is not None:
                kwargs["unix_permissions"] = unix_permissions

            if hasattr(FileInfo, "find"):
                resource = FileInfo.find(
                    volume_uuid,
                    **kwargs
                )
            else:
                resource = FileInfo(volume_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FileInfo: %s" % err)


