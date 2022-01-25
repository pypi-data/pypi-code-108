
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Depends, status, Response
from fastapi.responses import JSONResponse
from . import (
    BalenaAppInfo, get_application_state, ping, blink, update_check, reboot, shutdown, purge, restart, restart_service,
    supervisor_api_key, supervisor_uuid, regenerate_api_key, get_device_state, healthy,
    set_host_config, get_host_config, get_applications_state, get_version, get_container_ids,
    get_state_status, stop_service, restart_services, purge_all_user_data,
    BalenaDeviceInfo, BalenaHostConfig, BalenaAppsInfo, BalenaStateStatus, BalenaServiceInput,
    BalenaVersionResponse, BalenaServiceContainerIds
)
async def get_uuid_header(device_token: str = Header(...)):
    if device_token not in (supervisor_api_key(), supervisor_uuid()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="device auth header invalid")

router = APIRouter(
    prefix='/balena',
    dependencies=[Depends(get_uuid_header)],
)

@router.get('/ping', status_code=status.HTTP_200_OK)
async def route_ping():
    await ping()

@router.post('/v1/blink', status_code=status.HTTP_200_OK)
async def route_blink():
    success = await blink()
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.post('/v1/update', status_code=status.HTTP_204_NO_CONTENT)
async def route_update(force: Optional[bool] = None):
    success = await update_check(force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post('/v1/reboot', status_code=status.HTTP_202_ACCEPTED)
async def route_reboot(force: Optional[bool] = None):
    success = await reboot(force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(dict(Data='OK', Error=''))

@router.post('/v1/shutdown', status_code=status.HTTP_202_ACCEPTED)
async def route_shutdown(force: Optional[bool] = None):
    success = await shutdown(force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(dict(Data='OK', Error=''))

@router.post('/v1/purge', status_code=status.HTTP_200_OK)
async def route_purge():
    success = await purge()
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return JSONResponse(dict(Data='OK', Error=''))

@router.post('/v1/restart', status_code=status.HTTP_200_OK)
async def route_restart():
    success = await restart()
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return "OK"

@router.post('/v1/regenerate-api-key', status_code=status.HTTP_200_OK)
async def route_regenerate_api_key() -> str:
    key = await regenerate_api_key()
    return key

@router.get('/v1/device', status_code=status.HTTP_200_OK, response_model=BalenaDeviceInfo)
async def route_device():
    return await get_device_state()

@router.get('/v1/healthy', status_code=status.HTTP_200_OK)
async def route_healthy():
    success = await healthy()
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.patch('/v1/device/host-config', status_code=status.HTTP_200_OK)
async def route_set_host_config(host_config: BalenaHostConfig):
    success = await set_host_config(host_config=host_config)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.get('/v1/device/host-config', status_code=status.HTTP_200_OK, response_model=BalenaHostConfig)
async def route_get_host_config():
    return await get_host_config()

@router.get('/v2/applications/state', status_code=status.HTTP_200_OK, response_model=BalenaAppsInfo)
async def route_get_applications_state():
    return await get_applications_state()

@router.get('/v2/applications/{app_id}/state', status_code=status.HTTP_200_OK, response_model=BalenaAppInfo)
async def route_get_application_state(app_id: int):
    return await get_application_state()

@router.get('/v2/state/status', status_code=status.HTTP_200_OK, response_model=BalenaStateStatus)
async def route_get_state_status():
    return await get_state_status()

@router.post('/v2/applications/{app_id}/restart-service', status_code=status.HTTP_200_OK)
async def route_restart_service(app_id: int, service: BalenaServiceInput, force: Optional[bool] = None):
    success = await restart_service(service=service.service_name, app_id=app_id, force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.post('/v2/applications/{app_id}/stop-service', status_code=status.HTTP_200_OK)
async def route_stop_service(app_id: int, service: BalenaServiceInput, force: Optional[bool] = None):
    success = await stop_service(service=service.service_name, app_id=app_id, force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.post('/v2/applications/{app_id}/start-service', status_code=status.HTTP_200_OK)
async def route_start_service(app_id: int, service: BalenaServiceInput, force: Optional[bool] = None):
    success = await stop_service(service=service.service_name, app_id=app_id, force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.post('/v2/applications/{app_id}/restart', status_code=status.HTTP_200_OK)
async def route_restart_services(app_id: int, force: Optional[bool] = None):
    success = restart_services(app_id=app_id, force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.post('/v2/applications/{app_id}/purge', status_code=status.HTTP_200_OK)
async def route_purge_all_user_data(app_id: int, force: Optional[bool] = None):
    success = await purge_all_user_data(app_id=app_id, force=force or False)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

@router.get('/v2/version', status_code=status.HTTP_200_OK, response_model=BalenaVersionResponse)
async def route_get_version():
    version = await get_version()
    return BalenaVersionResponse(
        version=version,
        status="success"
    )

@router.get('/v2/containerId', status_code=status.HTTP_200_OK, response_model=BalenaServiceContainerIds)
async def route_get_container_ids():
    return await get_container_ids()
