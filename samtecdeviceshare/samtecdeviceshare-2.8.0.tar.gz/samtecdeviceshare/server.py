import os
import tempfile
from asyncio import CancelledError
from typing import Optional
import uvicorn
from fastapi import FastAPI, status, HTTPException, BackgroundTasks
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import samtecdeviceshare
from .fastapi_utils import repeat_every
from .types import DeviceState, NetworkCredentialCleaned, NetworkCredentials, AppDataV1, TextResponseEnum
from .logger import setup_logger
from .sdshare import SamtecDeviceShare
from .balena import is_on_balena

logger = setup_logger('sdc', os.getenv('APP_LOG_PATH', tempfile.gettempdir()))

sds = SamtecDeviceShare()

app = FastAPI(
    title='Samtec Device Share',
    version=samtecdeviceshare.__version__,
    root_path=sds.config.root_path
)

if is_on_balena():
    from .balena.api import router as balena_router
    logger.debug('Exposing balena supervisor routes')
    app.include_router(balena_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@repeat_every(wait_first=True, seconds=1, logger=logger)
async def sdc_update():
    await sds.update()

@app.on_event("startup")
async def startup_event():
    logger.info('Server starting up')
    await sds.open()
    await sdc_update()

@app.on_event("shutdown")
async def shutdown_event():
    logger.warning('Server shutting down')
    await sds.close()

#######################################################################################################################
# SDC REST Routes (v1 - legacy)
#######################################################################################################################

@app.get("/data.json", response_model=AppDataV1, status_code=status.HTTP_200_OK, description='''
Get minimal device information including type and web port. ''')
async def get_app_data():
    return AppDataV1(type=sds.config.app_name, port=sds.config.app_web_port)

@app.get("/img.png", description='''Get app icon.''')
async def get_app_img() -> Response:
    return FileResponse(sds.config.app_img_path, media_type="application/octet-stream", status_code=status.HTTP_200_OK)

#######################################################################################################################
# SDC REST Routes (v2)
#######################################################################################################################

@app.get("/api/v2/device", response_model=DeviceState, status_code=status.HTTP_200_OK, description='''
Get full device information.''')
async def get_device_state():
    return await sds.get_device_state()

@app.get("/api/v2/app/logs", description='Download all app logs as a zip.')
async def get_app_logs() -> Response:
    try:
        return Response(content=await sds.get_log_zip_data(), media_type="application/octet-stream", status_code=status.HTTP_200_OK)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to get app logs w/ error: {0}'.format(err)) from err

@app.post('/api/v2/device/blink', status_code=status.HTTP_200_OK, description='''
Have the device blink for 15 seconds.''')
async def blink_device() -> TextResponseEnum:
    try:
        return TextResponseEnum.from_bool(await sds.blink_device())
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to get app state w/ error: {0}'.format(err)) from err

@app.post('/api/v2/device/restart', status_code=status.HTTP_202_ACCEPTED, description='''
Performs a full reboot of the device.''')
async def restart_device() -> TextResponseEnum:
    return TextResponseEnum.from_bool(await sds.restart_device())

@app.post('/api/v2/app/update/check', status_code=status.HTTP_204_NO_CONTENT, description='''
Checks if an app update exists and if so downloads it. ''')
async def app_update_check(background_tasks: BackgroundTasks, credentials: Optional[NetworkCredentials] = None) -> TextResponseEnum:
    try:
        background_tasks.add_task(sds.perform_ota_update_check, credentials)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except (CancelledError, ConnectionResetError) as err:
        logger.exception('Request cancelled or reset (error: %s)', err)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to perform update check w/ error: {0}'.format(err)) from err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to perform update check w/ error: {0}'.format(err)) from err

@app.post('/api/v2/app/update/install', status_code=status.HTTP_204_NO_CONTENT, description='''
Installs update if downloaded and restarts app.''')
async def app_update_install(background_tasks: BackgroundTasks) -> TextResponseEnum:
    try:
        background_tasks.add_task(sds.update_application)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to perform update w/ error: {0}'.format(err)) from err

#######################################################################################################################
# Optional WiFi REST Routes
#######################################################################################################################

@app.get('/api/v2/network/wifi/credentials', response_model=Optional[NetworkCredentialCleaned], status_code=status.HTTP_200_OK, description='''
Get WiFi connection information. __NOTE__: Only gets stored default connection for now.''')
async def get_wifi_network():
    return sds.get_default_wifi()

@app.post('/api/v2/network/wifi/credentials', status_code=status.HTTP_200_OK, description='''
Temporarily connect to supplied WiFi network. Connection is cleared on reboot or app restart.''')
async def set_wifi_network(credentials: NetworkCredentials) -> TextResponseEnum:
    try:
        await sds.launch_wifi(credentials)
        return TextResponseEnum.Success
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Failed to update WiFi credentials w/ error: {0}'.format(err)) from err

if __name__ == "__main__":
    uvicorn.run(app, host=sds.config.rest_address, port=sds.config.rest_port)
