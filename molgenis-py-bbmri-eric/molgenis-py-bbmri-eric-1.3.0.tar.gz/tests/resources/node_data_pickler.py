"""
Use this script to update the node_data.pkl file that contains test data (the staging
data of node NO).
"""

import pickle

from dotenv import dotenv_values

from molgenis.bbmri_eric.bbmri_client import EricSession

# noinspection PyProtectedMember
from molgenis.bbmri_eric.model import Node

# get credentials from .env.local (in this dir) - if this file doesn't exist: create it
config = dotenv_values(".env.local")
target = config["TARGET"]
username = config["USERNAME"]
password = config["PASSWORD"]

# get staging data of node NL
session = EricSession(url=target)
session.login(username, password)
node_data = session.get_staging_node_data((Node("NO", "Norway")))

# pickle and write the NodeData object to file
file = open("node_data.pkl", "wb")
pickle.dump(node_data, file)
file.close()
