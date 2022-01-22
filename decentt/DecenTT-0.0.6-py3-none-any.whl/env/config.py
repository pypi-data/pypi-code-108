import os
from DecenTT.env.load_env import load_env


# Load the dot env file

# root_path = os.path.dirname(os.path.abspath(__file__))
# load_env(path=root_path + "/../.env")
from dotenv import load_dotenv

load_dotenv()


# Declare all the exportable variables here
MQTT_HOST = str(os.environ.get("MQTT_HOST"))
MQTT_PORT = str(os.environ.get("MQTT_PORT"))
MQTT_USER = str(os.environ.get("MQTT_USER"))
MQTT_PASS = str(os.environ.get("MQTT_PASS"))
SUBSYSTEM_PATH = str(os.environ.get("SUBSYSTEM_PATH"))

LOG_PATH = str(os.environ.get("LOG_PATH"))

DEFAULT_HOST = str(os.environ.get("DEFAULT_HOST"))

