import os

from loguru import logger
from dyndebug import Debug
from typing import Callable, Any
from dotmap import DotMap
from capturejob.service.fileservice import FileService
from datetime import datetime

def checkPrerequsites(variable):
    if os.getenv(variable) is None:
        return True
    return False


def CaptureJob():
    debug = Debug('capturejob')

    issues = list(
        filter(
            checkPrerequsites,
            ["CAPTURE_CONNECTION_STRING","CAPTURE_CONTAINER_NAME","TASK_ID"],
        )
    )
    if len(issues) > 0:
        raise Exception(f"Missing environment variables {issues}")

    config = DotMap({
        "connectionString": os.environ.get("CAPTURE_CONNECTION_STRING"),
        "containerName": os.environ.get("CAPTURE_CONTAINER_NAME"),
    })

    print(config.containerName)
    fileservice =FileService(config)

    job = os.environ.get("TASK_ID")

    now = datetime.now() 
    date_time = now.strftime("%Y%m%d_%H%M%S")    

    cwd = os.getcwd()
    
    folder = f"{date_time}_{job}"
    fileservice.upload(os.path.join(cwd,"log.txt"),folder,"log.txt")    
 