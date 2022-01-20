import traceback
import json
from google.protobuf import json_format

from yangsuite import get_logger, get_path
from ysyangtree import TaskHandler, TaskException

from ysdevices import YSDeviceProfile
from ysgnmi.gnmi_util import GnmiMessage
from ysgnmi.device_plugin import GnmiSession

log = get_logger(__name__)

try:
    from ystestmgr.rpcverify import RpcVerify
except ImportError:
    log.warning('Install yangsuite-testmanager for opfield verification')

    class RpcVerify:
        def process_operational_state(data, returns={}):
            return data


class GnmiException(Exception):
    pass


def get_capabilities(user, devprofile):
    """Get the gNMI capabilities from the given device profile.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with

    Raises:
      grpc.RpcError: in case of connection error

    Returns:
      dict: Representation of :class:`CapabilityResponse` protobuf.
    """
    try:
        session = GnmiSession.get(devprofile, user)
        caps = session.gnmi.capabilities()
        stop_session(user, devprofile)
        if not caps:
            session.log.error('No capabilities returned.')
            raise Exception('No capabilities returned.')
        return json_format.MessageToDict(caps)

    except Exception as exc:
        stop_session(user, devprofile)
        raise exc


def get_request(user, devprofile, request):
    """Send a gNMI GET request to the given device.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Passed through as kwargs of :class:`GetRequest`
        constructor.

    Raises:
      grpc.RpcError: in case of a connection error
      ValueError: if request contains invalid values

    Returns:
      dict: Representation of :class:`GetResponse` protobuf
    """
    gnmi_string = ''
    if 'raw' in request:
        try:
            session = GnmiSession.get(devprofile, user)
            GnmiMessage.run_get(session, request['raw'])
        except Exception:
            log.error(traceback.format_exc())
    else:
        try:
            if not request.get('modules'):
                return {'error': 'No data requested from model.'}

            msg_type = request.get('action')
            if not msg_type:
                raise GnmiException('ERROR: gNMI message type missing.')
            gmsg = GnmiMessage(msg_type, request)
            gmcs = gmsg.get_messages()

            if not gmcs:
                raise Exception('No message defined for GET.')
            for gmc in gmcs:
                gnmi_string += json_format.MessageToJson(gmc.payload)
                gnmi_string += '\n'
                if request.get('run'):
                    session = GnmiSession.get(devprofile, user)
                    GnmiMessage.run_get(session, gmc.payload)
            if not request.get('run'):
                if not gnmi_string:
                    raise Exception(
                        'Build GET failed.  Check YANG Suite logs for details.'
                    )
                return gnmi_string
        except GnmiException as exc:
            raise exc
        except Exception:
            log.error(traceback.format_exc())


def get_results(user, devprofile):
    """Retrieve active log messages.

    Args:
      devprofile (ysdevices.YSDeviceProfile): Device profile class.
      user (str): YANG suite username.

    Returns:
      collections.deque: Queue of active log messages.
    """
    session = GnmiSession.get(devprofile, user)
    notifier = session.active_notifications.get(session)
    if notifier:
        if notifier.is_alive():
            session.results.append('Waiting for notification')
            if notifier.time_delta \
                    and notifier.time_delta < notifier.stream_max:
                notifier.stop()
    return session.result_queue()


def set_request(user, devprofile, request):
    """Send a gNMI SET request to the given device.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Passed through as kwargs of :class:`SetRequest`
        constructor.

    Raises:
      grpc.RpcError: in case of a connection error
    """
    if 'raw' in request:
        try:
            session = GnmiSession.get(devprofile, user)
            GnmiMessage.run_set(session, request['raw'])
        except Exception:
            log.error(traceback.format_exc())
    else:
        try:
            gnmi_string = ''
            if not request.get('modules'):
                return {'error': 'No data requested from model.'}

            msg_type = request.get('action')
            if not msg_type:
                raise GnmiException('ERROR: gNMI message type missing.')
            gmsg = GnmiMessage(msg_type, request)
            gmcs = gmsg.get_messages()

            if not gmcs:
                raise Exception('No messages defined for SET.')
            for gmc in gmcs:
                if gmc.json_val:
                    gnmi_dict = json_format.MessageToDict(gmc.payload)
                    for upd in gnmi_dict['update']:
                        if 'jsonIetfVal' in upd['val']:
                            upd['val']['jsonIetfVal'] = gmc.json_val
                        else:
                            upd['val']['jsonVal'] = gmc.json_val
                        break
                    gnmi_string += json.dumps(gnmi_dict, indent=2)
                else:
                    gnmi_string += json_format.MessageToJson(gmc.payload)
                gnmi_string += '\n'
                if request.get('run'):
                    session = GnmiSession.get(devprofile, user)
                    GnmiMessage.run_set(session, gmc.payload)
            if not request.get('run'):
                if not gnmi_string:
                    raise Exception(
                        'Build SET failed.  Check YANG Suite logs for details.'
                    )
                return gnmi_string
        except GnmiException as exc:
            raise exc
        except Exception:
            log.error(traceback.format_exc())


def subscribe_request(user, devprofile, request):
    """Send a gNMI Subscribe request to the given device.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Passed through as kwargs of :class:`SetRequest`
        constructor.

    Raises:
      grpc.RpcError: in case of a connection error
    """
    if 'raw' in request:
        try:
            session = GnmiSession.get(devprofile, user)
            GnmiMessage.run_subscribe(session, request['raw'], request)
        except Exception:
            log.error(traceback.format_exc())
    else:
        gnmi_string = ''
        try:
            if not request.get('modules'):
                return {'error': 'No data requested from model.'}

            msg_type = request.get('action')
            if not msg_type:
                raise GnmiException('ERROR: gNMI message type missing.')
            sample_interval = request.get('sample_interval')
            if sample_interval:
                sample_interval = int(1e9) * int(sample_interval)
                request['sample_interval'] = sample_interval
            else:
                request['sample_interval'] = int(1e9) * 10
            gmsg = GnmiMessage(msg_type, request)
            gmcs = gmsg.get_messages()

            if not gmcs:
                raise Exception('No message defined for SUBSCRIBE.')
            for gmc in gmcs:
                gnmi_string += json_format.MessageToJson(gmc.payload)
                gnmi_string += '\n'
                if request.get('run'):
                    session = GnmiSession.get(devprofile, user)
                    GnmiMessage.run_subscribe(session, gmc.payload, request)
            if not request.get('run'):
                if not gnmi_string:
                    raise Exception(
                        'Build SUBSCRIBE failed.  Check YANG Suite logs '
                        'for details.'
                    )
                return gnmi_string
        except GnmiException as exc:
            raise exc
        except Exception:
            log.error(traceback.format_exc())


def stop_session(user, devprofile):
    """Stop subscribe threads, close channel, and remove session instance.

    Args:
      user (str): YANG Suite username.
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with.
    """
    if isinstance(devprofile, YSDeviceProfile):
        device = devprofile.base.profile_name
    else:
        device = str(devprofile)
    log.info("Stopping session {0}:{1}".format(user, device))
    GnmiSession.close(user, devprofile)


def show_gnmi_replay(user, devprofile, request):
    """Return replay metadata formatted for gNMI protocol.

    Args:
      request (dict): Replay name and category.

    Raises:
      tasks.TaskException: in case of replay retreival error

    Returns:
      dict: Representation of :class:`GetResponse`, :class:`SetResponse`
    """
    # TODO: need variables from device or may fail on xpath
    request_dict = {}
    user = request.get('user')
    replay_name = request.get('replay')
    category = request.get('category')
    path = get_path('replays_dir', user=user)
    try:
        request['replay'] = TaskHandler.get_replay(path, category, replay_name)

        # TODO: construct from replay

    except Exception as exe:
        log.error("Failed to generate gNMI replay %s", replay_name)
        log.debug(traceback.format_exc())
        raise TaskException("Failed to generate gNMI replay {0}\n{1}".format(
                replay_name,
                str(exe)
            )
        )

    return request_dict


def run_gnmi_replay(user, devprofile, request):
    """Run a replay over gNMI protocol.

    Args:
      devprofile (ysdevices.devprofile.YSDeviceProfile): Device to
        communicate with
      request (dict): Replay name and category.

    Raises:
      grpc.RpcError: in case of a connection error

    Returns:
      dict: Representation of :class:`GetResponse`, :class:`SetResponse`
    """
    user = request.get('user', '')
    response = {}

    gen_request = show_gnmi_replay(request)
    if gen_request['action'] == 'set':
        response = set_request(devprofile, user, gen_request['request'])
    elif gen_request['action'] == 'get':
        response = set_request(devprofile, user, gen_request['request'])
    else:
        raise TypeError(
                'gNMI "{0}" not supported.'.format(gen_request['action'])
            )

    return str(response)
