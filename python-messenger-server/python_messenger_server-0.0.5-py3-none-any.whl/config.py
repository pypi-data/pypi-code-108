import os
import sys
import configparser
from PySide2.QtCore import QCoreApplication

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

SITE_PACKAGES_DIR = None
for path in sys.path:
    if path.endswith("site-packages"):
        SITE_PACKAGES_DIR = path
        break
        
QT_PLUGINS_PATH = os.path.join(
    SITE_PACKAGES_DIR, "PySide2\\plugins")
QCoreApplication.setLibraryPaths([QT_PLUGINS_PATH])

config = configparser.ConfigParser()
SERVER_INI = f"{BASE_DIR}\\server.ini"
config.read(SERVER_INI)
SETTINGS = config["SETTINGS"]

SERVER_PORT = SETTINGS.get("server_port")
LISTEN_ADDRESS = SETTINGS.get("listen_address")

DATABASE_PATH = SETTINGS.get("database_path")
DATABASE_NAME = SETTINGS.get("database_file")

USER_ADDRESS = "127.0.0.1"
USER_PORT = 7777

MAX_POCKET_SIZE = 1024
MAX_CONNECTIONS = 5

LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATABASE_DIR = os.path.join(BASE_DIR, "databases")
CLIENT_DIR = os.path.join(BASE_DIR, "client")
SERVER_DIR = os.path.join(BASE_DIR, "server")
CLIENT_UI_DIR = "client\\gui\\ui"
SERVER_UI_DIR = "server\\gui\\ui"
DATABASE_ENGINE = f'sqlite:///{DATABASE_PATH}\\{DATABASE_NAME}'
CLIENT_DATABASE_ENGINE = 'sqlite:///client\\client_base_'
TEST_DATABASE_ENGINE = 'sqlite:///test_server_base.db3'
VENV_DIR = sys.executable

CLIENT_LOG_DIR = os.path.join(LOG_DIR, 'client_logs')
SERVER_LOG_DIR = os.path.join(LOG_DIR, 'server_logs')
