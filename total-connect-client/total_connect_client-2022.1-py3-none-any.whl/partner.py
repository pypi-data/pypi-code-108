"""Test your system from the command line."""

import logging
import sys
from pprint import pprint


from total_connect_client.client import TotalConnectClient

logging.basicConfig(filename="test.log", level=logging.DEBUG)

if len(sys.argv) != 3:
    print("usage:  username password ")
    sys.exit()


USERNAME = sys.argv[1]
PASSWORD = sys.argv[2]

TC = TotalConnectClient(USERNAME, PASSWORD)

for location_id in TC.locations:
    response = TC.request("GetAssociatedPartners", args=(TC.token, location_id))
    pprint(response)


sys.exit()
