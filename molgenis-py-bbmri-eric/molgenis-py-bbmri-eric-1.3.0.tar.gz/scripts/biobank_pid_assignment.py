"""
This script can be used to do the initial assignment of persistent identifiers to
the biobanks table.

This script requires two files in this directory:
1. A ".env" file:

TARGET=<SERVER_URL>
USERNAME=<ADMIN_USERNAME>
PASSWORD=<ADMIN_PASSWORD>

2. A "pyhandle_creds.json" file:

{
  "handle_server_url": "<URL_TO_HANDLE_SERVER>",
  "private_key": "<FULL_PATH_TO_PRIVATE_KEY.pem>",
  "certificate_only": "<FULL_PATH_TO_CERTIFICATE_ONLY.pem>",
  "client": "rest",
  "prefix": "<HANDLE_PREFIX>",
  "server_url": "<URL_TO_WHICH_THE_PIDS_WILL_RESOLVE>"
}

See https://eudat-b2handle.github.io/PYHANDLE/pyhandleclientrest.html#authentication
-using-client-certificates for more information.

Follow these steps:
1. Add a string attribute "pid" to the eu_bbmri_eric_biobanks table
2. Make the attribute "nullable"
3. Run the script
4. Change the "pid" attribute from "nullable" to "required" and "readOnly"
"""

from dotenv import dotenv_values

from molgenis.bbmri_eric.bbmri_client import ExtendedSession
from molgenis.bbmri_eric.pid_service import PidService

table = "eu_bbmri_eric_biobanks"

print("Logging in to the directory")
config = dotenv_values(".env")
target = config["TARGET"]
username = config["USERNAME"]
password = config["PASSWORD"]
session = ExtendedSession(url=target)
session.login(username, password)

print("Creating handle client")
pid_service = PidService.from_credentials("pyhandle_creds.json")

print("Getting data from the directory")
biobanks = session.get_uploadable_data(table)

print("Registering PIDs")
url_prefix = session.url + "#/biobank/"
for biobank in biobanks:
    if "pid" in biobank:
        continue

    url = url_prefix + biobank["id"]
    pid = pid_service.register_pid(url=url, name=biobank["name"])
    biobank["pid"] = pid
    print(f"Generated {pid} for {biobank['id']}")

print("Uploading to directory")
session.update_batched(table, biobanks)

print("All done!")
