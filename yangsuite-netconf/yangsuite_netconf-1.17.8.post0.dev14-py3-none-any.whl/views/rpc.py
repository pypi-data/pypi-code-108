# Copyright 2016 Cisco Systems, Inc
"""RPC handling for Netconf protocol."""
import errno
import traceback
import re
import lxml.etree as et
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from yangsuite.logs import get_logger
from yangsuite.paths import get_path
from ysdevices import YSDeviceProfile
from .. import nconf
from ysyangtree.tasks import TaskHandler, TaskException
from .utilities import json_request, netconf_session_request


log = get_logger(__name__)

#  TODO: Fix JsonResponse format


@login_required
def run_result(request):
    """Render notification result page."""
    return render(request, 'ysnetconf/runresult.html')


@login_required
def get_task_rpc(request):
    """Retrieve task and return generated Netconf.

    Args:
      name (str): Name of task (no name return entire list)
      category (str): User defined category
      dsstore (str): Name of target datastore.
      gentype (str): One of:

        - 'basic' (ncclient format)
        - 'raw' (complete RPC)
        - 'script' (ncclient PYTHON script)
    """
    req = request.POST.dict()
    path = get_path('tasks_dir', user=request.user.username)
    name = request.POST.get('name', '')

    if name:
        # gentype "run" is for internal use, and is not serializable to
        # JSON format as it contains lxml Element objects.
        # Rather than reject it specifically, only accept the ones we want.
        if req.get('gentype') not in ['basic', 'raw', 'script', 'custom']:
            return JsonResponse({}, status=400, reason="Invalid gentype")

        try:
            th = TaskHandler(name, path, req)
            replay = th.retrieve_task()
            ret = nconf.gen_task_api(replay, req)
            return JsonResponse(ret)
        except TaskException as e:
            return JsonResponse({}, status=500, reason=str(e))
    else:
        return JsonResponse({}, status=400, reason='No task name.')


@login_required
@json_request
@netconf_session_request
def clear_rpc_results(request, jsondata, key):
    """Replace collections.deque live stream cache."""
    nconf.NetconfSession.get(key).clear_log()

    return JsonResponse({'status': 'done'})


@login_required
@json_request
@netconf_session_request
def run_rpc(request, jsondata, key):
    """Run an RPC constructed from get APIs or get the status/output thereof.

    Args:
      request (django.http.HttpRequest): POST request (begin communication)
        or GET request (get latest data about communication in progress)
      jsondata (dict): Data parsed from POST request.body, with keys:

        - device (str): Name of device profile to communicate with.
        - task (str): Name of saved task to run.
        - rpcs (list or str): Ignored if 'task' is present. Either a list of
          data dicts needed to form multiple RPCs, or if 'custom' is present,
          an XML string describing the literal RPCs to send.
        - custom (str): If present and non-empty (e.g., "true"), then 'rpcs' is
          an XML string rather than a list of dicts.
        - rpctimeout (str): RPC reply timeout value in seconds.

      key (SessionKey): derived from user and device in the
                        netconf_session_request decorator

    Returns:
      JsonResponse:

        - for a POST request, will have keys 'reply' (list of (nc_op, output)
          entries, as returned by :func:`ncclient_send`) and/or 'error'
          (descriptive error string).
        - for a GET request, will have keys 'reply' (list of text and/or XML
          strings) and 'connected' (boolean).
    """
    if request.method == 'POST':
        result = {'reply': "No RPC reply"}
        task = jsondata.get('task')
        rpcs = jsondata.get('rpcs')
        user = request.user.username
        custom = jsondata.get('custom')

        try:
            ncrpcs = []

            if task is not None:
                path = get_path('tasks_dir', user=user)
                jsondata['gentype'] = 'run'
                th = TaskHandler(task, path, jsondata)
                replay = th.retrieve_task()
                task_gen = nconf.gen_task_api(replay, jsondata)
                if task_gen['error']:
                    return JsonResponse({'error': task_gen['error']})
                ncrpcs = task_gen['ncrpcs']
            elif rpcs is None:
                return JsonResponse({'reply': "No RPC sent"})
            elif custom is not None:
                log.debug("Creating custom RPC from %s", rpcs)
                ncrpcs = []
                start = 0
                # check for multiple RPCs
                for m in re.finditer('</[a-z]*:rpc>|</rpc>', rpcs):
                    rpc = et.fromstring(rpcs[start:m.end()])
                    ncrpcs.append(('rpc', {'rpc_command': rpc}))
                    start = m.end()
            else:
                for rpc in rpcs:
                    log.debug("Generating RPC(s) for %s", rpc)
                    rpc['gentype'] = 'run'
                    ncrpcs += nconf.gen_rpc_api(rpc)['ncrpcs']

            result['reply'] = nconf.ncclient_send(key, ncrpcs)

        except Exception as e:
            log.error("Exception: %s", e)
            log.debug(traceback.format_exc())
            result['error'] = str(e)

        return JsonResponse(result)
    else:
        data = []
        nconf_session = nconf.NetconfSession.get(key)
        nc_log = nconf_session.message_log
        while(len(nc_log)):
            data.append(nc_log.popleft())
        return JsonResponse({
            'connected': nconf_session.connected,
            'reply': data,
        })


@login_required
@json_request
def get_rpc(request, jsondata):
    """Get the XML text for the requested RPC.

    Args:
      request (django.http.HttpRequest): HTTP request
      jsondata (dict): Parsed from request.body and passed through to
        :func:`~ysnetconf.nconf.gen_rpc_api`
    """
    result = {'reply': "No RPC reply"}

    res = nconf.gen_rpc_api(jsondata)
    if res:
        result['reply'] = res['rpc']

    return JsonResponse(result)


@login_required
def get_yang(request, yangset=None, modulenames=None):
    """Render the base netconf page, with optional selections.

    Args:
      request (django.http.HttpRequest): HTTP GET request
      yangset (str): YANG set slug 'owner+setname' to auto-select.
      modulenames (str): module name(s) to auto-select from this yangset,
        as comma-separated list of the form "module-1,module-2,module-3"
    Returns:
      django.http.HttpResponse: page to display
    """
    devices = YSDeviceProfile.list(require_feature="netconf")
    replay_dir = get_path('tasks_dir', user=request.user.username)

    return render(request, 'ysnetconf/netconf.html', {
        'devices': devices,
        'yangset': yangset or '',
        'modulenames': modulenames or '',
        'replay_dir': replay_dir
    })


@login_required
@json_request
@netconf_session_request
def lock_unlock_datastore(request, jsondata, key):
    """Lock or Unlock the datastore of the selected device.

    Args:
      request (django.http.HttpRequest): HTTP POST request
      jsondata (dict): Data parsed from POST request.body, with keys:

        - device (str): name of the selected device.
        - dsstore (str): name of the selected datastore.
        - lock (boolean): boolean variable indicating lock or unlock.
        - retry_timer (str): timer value to retry lock on datastore.

      key (SessionKey): derived from user and device
    """
    for param in ['device', 'dsstore', 'lock', 'retry_timer']:
        if param not in jsondata:
            return JsonResponse({}, status=400,
                                reason='Missing mandatory parameter {0}'.
                                format(param))

    dsstore = jsondata.get('dsstore')
    lock = jsondata.get('lock')
    retry_timer = jsondata.get('retry_timer')
    try:
        timer = int(retry_timer)
    except ValueError:
        return JsonResponse({}, status=400, reason="Invalid retry_timer value")

    result = {'resp': 'Unknown Error'}

    if lock:
        res = nconf.lock_datastore(key, dsstore, timer)
    else:
        res = nconf.unlock_datastore(key, dsstore)
    result['resp'] = res['reply']
    return JsonResponse(result)


@login_required
@json_request
@netconf_session_request
def start_end_session(request, jsondata, key):
    """Function to start and send netconf session.

    Args:
        request (django.http.HttpRequest): HTTP POST request
        jsondata (dict): Data parsed from POST request.body, with keys:

          - device (str): name of the selected device
          - session (str): 'start' or 'end'
          - rpctimeout (str): RPC reply timeout value in seconds.

        key (SessionKey): derived from user and device

    Returns:
        JsonResponse: with key 'reply' (boolean success)
    """
    status = jsondata.get('session')
    rpctimeout = jsondata.get('rpctimeout', '30')
    try:
        timeout = int(rpctimeout)
    except ValueError:
        return JsonResponse({}, status=400, reason="Invalid rpctimeout value")
    result = {'reply': False}

    if status == 'start':
        result['reply'] = nconf.start_session(key, timeout)
    elif status == 'end':
        result['reply'] = nconf.end_session(key)
    else:
        return JsonResponse({}, status=400, reason="Invalid session value")
    return JsonResponse(result)


@login_required
@netconf_session_request
def list_capabilities(request, key, **kwargs):
    """Get the list of capabilities reported by a given device.

    Returns:
      django.http.JsonResponse: {'capabilities': [list of dicts]}
    """
    try:
        return JsonResponse(
            {'capabilities': nconf.ncclient_server_capabilities_report(key)})
    except Exception as e:
        return JsonResponse({}, status=500, reason=str(e))


@login_required
@netconf_session_request
def list_datastores(request, key, **kwargs):
    """Get a dict of datastores applicable to a given device for each operation.

    Args:
      request (django.http.HttpRequest): HTTP GET request
    Returns:
      django.http.JsonResponse: {'datastores': [list]}
    """
    list_all = request.GET.get('list_all')
    try:
        dslist_dict = {'get':
                       nconf.ncclient_server_datastores(key, 'get'),
                       'edit-config':
                       nconf.ncclient_server_datastores(key, 'edit-config'),
                       'get-config':
                       nconf.ncclient_server_datastores(key, 'get-config'),
                       }
        if list_all:
            datastores_set = set(dslist_dict['get'])
            datastores_set.update(dslist_dict['edit-config'])
            datastores_set.update(dslist_dict['get-config'])
            return JsonResponse({'all_datastores': sorted(datastores_set)})
        return JsonResponse(dslist_dict)
    except nconf.NCClientError as e:
        return JsonResponse({}, status=501, reason=str(e))

    except Exception as e:
        # Check if we're raising an OSError and handle appropriately
        if isinstance(e, OSError) and e.errno in [
                errno.ECONNREFUSED, errno.EPROTONOSUPPORT]:
            log.error("502: Bad Gateway Error")
            return JsonResponse({}, status=502, reason=e.strerror)
        else:
            # Default error handling
            return JsonResponse({}, status=500, reason=str(e))


@login_required
def set_log(request):
    """Set the log level for ncclient module.

    Args:
        request (django.http.HttpRequest): HTTP POST request
    """
    loglevel = request.POST.get('loglevel', 'info')
    result = {}
    try:
        result['reply'] = nconf.set_logging(loglevel)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({}, status=500, reason=str(e))
