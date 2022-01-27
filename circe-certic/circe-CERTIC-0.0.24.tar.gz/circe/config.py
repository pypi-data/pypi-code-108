import os
from pathlib import Path
from multiprocessing import cpu_count
import sys
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    "CIRCE_HOST": "127.0.0.1",
    "CIRCE_PORT": 8000,
    "CIRCE_DEBUG": False,
    "CIRCE_WORKERS": cpu_count() if os.name != "nt" else 1,
    "CIRCE_WORKING_DIR": "{}/.circe/".format(Path.home()),
    "CIRCE_IMMEDIATE_MODE": False,
    "CIRCE_USE_AUTH": True,
    "CIRCE_ACCESS_LOG": False,
    "CIRCE_ENABLE_WEB_UI": False,
    "CIRCE_WEB_UI_CRYPT_KEY": "you should really change this",
    "CIRCE_WEB_UI_REMOVE_USER_FILES_DELAY": 7200,
    "CIRCE_TRANSFORMATIONS_MODULE": None,
}

for key in CONFIG.keys():
    try:
        val = os.environ[key]
        if key in [
            "CIRCE_DEBUG",
            "CIRCE_USE_AUTH",
            "CIRCE_ACCESS_LOG",
            "CIRCE_IMMEDIATE_MODE",
            "CIRCE_ENABLE_WEB_UI",
        ]:
            CONFIG[key] = True if val == "1" else False
        else:
            CONFIG[key] = val
    except KeyError:
        pass

if (
    CONFIG["CIRCE_ENABLE_WEB_UI"]
    and CONFIG["CIRCE_WEB_UI_CRYPT_KEY"] == "you should really change this"
):
    sys.exit(
        "Running Web UI with the default crypt key is insecure. Please change CIRCE_WEB_UI_CRYPT_KEY."
    )


if CONFIG["CIRCE_IMMEDIATE_MODE"]:
    CONFIG["CIRCE_WORKERS"] = 1

paths = [
    CONFIG["CIRCE_WORKING_DIR"],
    "{}/queue/".format(CONFIG["CIRCE_WORKING_DIR"]),
    "{}/done/".format(CONFIG["CIRCE_WORKING_DIR"]),
]
for path in paths:
    os.makedirs(path, exist_ok=True)
if CONFIG["CIRCE_ENABLE_WEB_UI"]:
    os.makedirs(
        "{}/web_ui_sessions/".format(CONFIG["CIRCE_WORKING_DIR"]), exist_ok=True
    )
