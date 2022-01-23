from time import sleep
from typing import Union

from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

from ehelply_bootstrapper.sockets.managers import SCMApiGateway, SCMFastApi
from ehelply_bootstrapper.sockets.schemas import ChannelSocketMessage, APIGatewayMessage
from ehelply_bootstrapper.utils.state import State

from ehelply_microservice_library.integrations.m2m import M2M


async def scm_fastapi_init(
        realtime_controller: SCMFastApi,
        websocket: WebSocket,
        m2m: M2M
):
    """
    Call from a FastAPI socket endpoint set up in a microservice router.

    Verifies auth on the initial connection only. Identity token only needs to be valid for the initial connection.

    Args:
        realtime_controller:
        websocket:
        m2m:

    Returns:

    Microservice code example:
    ```
    from ehelply_bootstrapper.sockets.backbones import SCBRedis
    from ehelply_bootstrapper.sockets.managers import SCMFastApi
    from ehelply_bootstrapper.sockets.events import EventSocketEcho, EListenerSocketEcho

    class RealtimeController(SCMFastApi):
        def register_events(self):
            self.register_event(action="ehelply.bootstrapper.socket.echo", event=EventSocketEcho)

        def register_event_listeners(self):
            self.register_listener(EListenerSocketEcho())

    scb_redis: SCBRedis = SCBRedis(State.redis, connection_limit_per_identifier=1)
    realtime_controller: RealtimeController = RealtimeController(scb_redis)

    @router.websocket('/game')
    async def websocket_endpoint(websocket: WebSocket, m2m: M2M = Depends(get_m2m)):
        m2m: M2M = State.integrations.get("m2m")
        scm_fastapi_init(
            realtime_controller=realtime_controller,
            websocket=websocket,
            m2m=m2m
        )
    ```
    """
    authorized: bool = False

    participant_uuid: Union[None, str] = None

    await websocket.accept()

    try:
        while not authorized:
            message: Union[ChannelSocketMessage, dict, None] = await websocket.receive_json(mode='binary')

            if message:
                try:
                    message = ChannelSocketMessage(**message)
                except:
                    message = None

                if message and message.action == "authorization":

                    authorization: str = message.data['authorization']
                    ehelply_active_participant: str = message.data['ehelply-active-participant']

                    try:
                        claims = m2m.verify_token(token=authorization)
                    except:
                        await websocket.close(1008)
                        return

                    if not ehelply_active_participant:
                        await websocket.close(1008)
                        return

                    if ehelply_active_participant in claims['custom:participants'].split(','):
                        participant_uuid = ehelply_active_participant
                        authorized = True
                    else:
                        await websocket.close(1008)
                        return

            else:
                sleep(0.1)

    except WebSocketDisconnect:
        if participant_uuid:
            await realtime_controller.disconnect(participant_uuid)

    if authorized:
        await realtime_controller.connect(participant_uuid, websocket)


async def scm_apigateway_init(
        realtime_controller: SCMApiGateway,
        apigateway_message: APIGatewayMessage,
        m2m: M2M,
        log_messages: bool = False,
        log_errors: bool = False
):
    """
    Call from a realtime HTTP endpoint set up in a microservice router.

    Verifies authorization on every message. Identity token must be valid for each request.

    Excepts messages from API Gateway to have the following form (use Request Templates in APIGateway to achieve this):
    {
        "connection_id": "<APIGateway_ConnectionId>",       # This comes from APIGateway context vars
        "event": "MESSAGE",                                 # This comes from APIGateway context vars
        "message": {                                        # This is the only part that would come from a client
            "action": "<message_action>",
            "data": {
                "authorization": "<identity_token>",
                "ehelply-active-participant": "<active_participant>",
                ... other message data
            }
        }
    }


    Microservice code example:
    ```
    from ehelply_bootstrapper.sockets.schemas import ChannelSocketMessage, APIGatewayMessage
    from ehelply_bootstrapper.sockets.backbones import SCBDict
    from ehelply_bootstrapper.sockets.managers import SCMApiGateway
    from ehelply_bootstrapper.sockets.events import EventSocketEcho, EListenerSocketEcho
    from ehelply_bootstrapper.drivers.aws_utils.aws_apigateway import APIGateway, APIConfig
    from ehelply_bootstrapper.utils.environment import Environment


    class RealtimeController(SCMApiGateway):
        def register_events(self):
            self.register_event(action="ehelply.bootstrapper.socket.echo", event=EventSocketEcho)

        def register_event_listeners(self):
            self.register_listener(EListenerSocketEcho())


    stage: str = Environment.stage()
    if Environment.is_dev():
        stage = "test"

    realtime_backbone: SCBDict = SCBDict()
    realtime_apigateway: APIGateway = APIGateway(
        api_config=APIConfig(
            api_uuid="lt7x6mhfxg",
            stage=stage
        ),
        is_websockets=True
    )
    realtime_controller: RealtimeController = RealtimeController(
        socket_connection_backbone=realtime_backbone,
        api_gateway=realtime_apigateway
    )


    @router.post(
        '/realtime',
        tags=["realtime"],
    )
    async def apigateway_websocket_endpoint(apigateway_message: APIGatewayMessage = Body(...), m2m: M2M = Depends(get_m2m)):
        scm_apigateway_init(realtime_controller=realtime_controller, apigateway_message=apigateway_message, m2m=m2m)
    ```
    """
    # TODO: Auth could and likely should be moved into a lambda function in API Gateway

    if log_messages:
        State.logger.info(str(apigateway_message))

    if apigateway_message.event == "DISCONNECT":
        await realtime_controller.disconnect(identifier=None, connection=apigateway_message.connection_id)
        return

    if apigateway_message.event == "MESSAGE":

        try:
            message: ChannelSocketMessage = apigateway_message.message
        except:
            if log_errors:
                State.logger.warning("eHelply Sockets - Invalid message")
            await realtime_controller.disconnect(identifier=None, connection=apigateway_message.connection_id)
            return

        if 'authorization' not in message.data or 'ehelply-active-participant' not in message.data:
            if log_errors:
                State.logger.warning("eHelply Sockets - Invalid authorization")
            await realtime_controller.disconnect(identifier=None, connection=apigateway_message.connection_id)
            return

        authorization: str = message.data['authorization']
        ehelply_active_participant: str = message.data['ehelply-active-participant']

        try:
            claims = m2m.verify_token(token=authorization)
        except:
            if log_errors:
                State.logger.warning("eHelply Sockets - Invalid authorization token")
            await realtime_controller.disconnect(identifier=None, connection=apigateway_message.connection_id)
            return

        if not ehelply_active_participant:
            if log_errors:
                State.logger.warning("eHelply Sockets - Invalid active participant")
            await realtime_controller.disconnect(identifier=None, connection=apigateway_message.connection_id)
            return

        if ehelply_active_participant in claims['custom:participants'].split(','):
            participant_uuid = ehelply_active_participant
        else:
            if log_errors:
                State.logger.warning("eHelply Sockets - Active participant is not allowed")
            await realtime_controller.disconnect(identifier=None, connection=apigateway_message.connection_id)
            return

        del message.data['authorization']
        del message.data['ehelply-active-participant']

        await realtime_controller.connect(participant_uuid, apigateway_message.connection_id)
        await realtime_controller.on_receive(ehelply_active_participant, message)
