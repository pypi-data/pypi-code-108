import os

from loguru import logger
from dyndebug import Debug
from typing import Callable, Any
from dotmap import DotMap
from capturejob.service.fileservice import FileService


from datetime import datetime


def CaptureJob():
    debug = Debug('capturejob')
    config = DotMap({
        "connectionString": os.environ.get("CAPTURE_CONNECTION_STRING"),
        "containerName": os.environ.get("CAPTURE_CONTAINER_NAME"),
    })

    print(config.containerName)
    fileservice =FileService(config)

    job = os.environ.get("JOB")

    now = datetime.now() 
    date_time = now.strftime("%Y%m%d_%H%M%S")    

    cwd = os.getcwd()
    
    folder = f"{date_time}_{job}"
    fileservice.upload(os.path.join(cwd,"stdout.txt"),folder,"stdout.txt")
    fileservice.upload(os.path.join(cwd,"stderr.txt"),folder,"stderr.txt")
 