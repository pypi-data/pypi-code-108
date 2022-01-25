import os

VERSION = "dev.999"
PLUGIN_DIR = os.path.dirname(__file__)
try:
    with open(os.path.join(PLUGIN_DIR, "VERSION")) as version_file:
        VERSION = version_file.read().strip()
except BaseException:
    pass

MAX_PACKAGES = [
    {
        "build_version": "",
        "environment": [
            {"merge_policy": "exclusive", "name": "HDF5_USE_FILE_LOCKING", "value": "FALSE"},
            {
                "merge_policy": "exclusive",
                "name": "ADSKFLEX_LICENSE_FILE",
                "value": "@conductor-adlm",
            },
            {
                "merge_policy": "exclusive",
                "name": "MAX_LOCATION",
                "value": "C:/Program Files/Autodesk/3ds Max 2019",
            },
            {
                "merge_policy": "append",
                "name": "Path",
                "value": "C:/Program Files/Autodesk/3ds Max 2019",
            },
            {
                "merge_policy": "append",
                "name": "Path",
                "value": "C:/Program Files/SomePluginPath-21/bin",
            },
        ],
        "major_version": "2019",
        "minor_version": "",
        "package": "Autodesk_Max_2019.exe",
        "package_id": "abcdef2019",
        "path": "C:/Program Files/Autodesk/3ds Max 2019",
        "plugin_host_product": "",
        "plugin_host_version": "",
        "product": "max",
        "release_version": "",
        "vendor": "autodesk",
        "children": [],
    },
    {
        "build_version": "",
        "environment": [
            {"merge_policy": "exclusive", "name": "HDF5_USE_FILE_LOCKING", "value": "FALSE"},
            {
                "merge_policy": "exclusive",
                "name": "ADSKFLEX_LICENSE_FILE",
                "value": "@conductor-adlm",
            },
            {
                "merge_policy": "exclusive",
                "name": "MAX_LOCATION",
                "value": "C:/Program Files/Autodesk/3ds Max 2021",
            },
            {
                "merge_policy": "append",
                "name": "Path",
                "value": "C:/Program Files/Autodesk/3ds Max 2021",
            },
            {
                "merge_policy": "append",
                "name": "Path",
                "value": "C:/Program Files/SomePluginPath-21/bin",
            },
        ],
        "major_version": "2021",
        "minor_version": "",
        "package": "Autodesk_Max_2021.exe",
        "package_id": "abcdef2021",
        "path": "C:/Program Files/Autodesk/3ds Max 2021",
        "plugin_host_product": "",
        "plugin_host_version": "",
        "product": "max",
        "release_version": "",
        "vendor": "autodesk",
        "children": [],
    },
    {
        "build_version": "",
        "environment": [
            {"merge_policy": "exclusive", "name": "HDF5_USE_FILE_LOCKING", "value": "FALSE"},
            {
                "merge_policy": "exclusive",
                "name": "ADSKFLEX_LICENSE_FILE",
                "value": "@conductor-adlm",
            },
            {
                "merge_policy": "exclusive",
                "name": "MAX_LOCATION",
                "value": "C:/Program Files/Autodesk/3ds Max 2022",
            },
            {
                "merge_policy": "append",
                "name": "Path",
                "value": "C:/Program Files/Autodesk/3ds Max 2022",
            },
            {
                "merge_policy": "append",
                "name": "Path",
                "value": "C:/Program Files/SomePluginPath-22/bin",
            },
        ],
        "major_version": "2022",
        "minor_version": "",
        "package": "Autodesk_Max_2022.exe",
        "package_id": "abcdef2022",
        "path": "C:/Program Files/Autodesk/3ds Max 2022",
        "plugin_host_product": "",
        "plugin_host_version": "",
        "product": "max",
        "release_version": "",
        "vendor": "autodesk",
        "children": [],
    },
]

# ADSKFLEX_LICENSE_FILE=@conductor-adlm
# HDF5_USE_FILE_LOCKING=FALSE
# LD_LIBRARY_PATH=/usr/local/nvidia/lib64
# /usr/local/nvidia/lib64

# PATH=
# C:\Program Files\PowerShell\7
# C:\Python39\Scripts\
# C:\Python39\
# C:\Windows\system32
# C:\Windows
# C:\Windows\System32\Wbem
# C:\Windows\System32\WindowsPowerShell\v1.0\
# C:\Windows\System32\OpenSSH\
# C:\ProgramData\GooGet
# C:\Program Files\Google\Compute Engine\metadata_scripts
# C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin
# C:\Program Files\PowerShell\7\
# C:\Program Files\Google\Compute Engine\sysprep
# C:\Program Files\Docker
# C:\ProgramData\chocolatey\bin
# C:\Program Files\Common Files\Autodesk Shared\
# C:\Windows\system32\config\systemprofile\AppData\Local\Microsoft\WindowsApps
# C:\Program Files\PowerShell\7
# C:\Python39\Scripts\
# C:\Python39\
# C:\Windows\system32
# C:\Windows;C:\Windows\System32\Wbem
# C:\Windows\System32\WindowsPowerShell\v1.0\
# C:\Windows\System32\OpenSSH\
# C:\ProgramData\GooGet
# C:\Program Files\Google\Compute Engine\metadata_scripts
# C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin
# C:\Program Files\PowerShell\7\
# C:\Program Files\Google\Compute Engine\sysprep
# C:\Program Files\Docker
# C:\ProgramData\chocolatey\bin
# C:\Program Files\Common Files\Autodesk Shared\
# C:\Windows\system32\config\systemprofile\AppData\Local\Microsoft\WindowsApps

# Path=C:\Program Files\Autodesk\3ds Max 2019


#	3dsmaxcmdio.exe D:/Users/jonathancross/Downloads/3dsmax_biplane_arnold_2019.v002/biplane_arnold_2019_nolicense.max -frames:1 -v:5 -outputName:H:/3dsmax-biplane/renderoutput/biplane.exr