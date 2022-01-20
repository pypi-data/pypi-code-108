# Copyright 2016 Cisco Systems, Inc
import errno
import json
import lxml.etree as et
import operator
import os
import shutil
import tempfile
import traceback

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from yangsuite.paths import get_path
from yangsuite.logs import get_logger
from ysyangtree import context
from ysfilemanager import atomic_create
from ysfilemanager.views.utility import post_existing_repository_required
from ..nconf import (
    ncclient_server_capabilities,
    get_schema_list_via_capabilities,
    get_schema_list_via_ietf_netconf_monitoring,
    get_schema_list_via_ietf_yang_library,
    SessionKey,
    NetconfNotSupported,
    NetconfSession,
    YANG_LIBRARY_CAP_NS,
    MONITORING_NS,
)


log = get_logger(__name__)


@login_required
def list_schemas(request):
    """Get the list of schemas supported by a given device.

    Args:
      request (HttpRequest): POST request (for parity with
        :func:`download_schemas`)
    Returns:
      JsonResponse: with key ``schemas``, value as the list of schemas from
      :func:`get_schema_list`
    """
    return schema_json_handler(request, get_schema_list)


@login_required
@post_existing_repository_required
def download_schemas(request, targetrepo=None):
    """Download schema files and save them to a YSYangRepository.

    Args:
      request (HttpRequest): Either GET (status check) or POST (start download
        and validation process). A POST request needs to have 'schemas', which
        is a JSON-formatted string list of [[mod,rev],[mod,rev],...], as well
        as 'device' and 'repository' strings
    Returns:
      JsonResponse: for GET requests, see :func:`download_schemas_status`;
      for POST requests, see :func:`schema_json_handler`.
    """
    if request.method == 'GET':
        # Status request
        return download_schemas_status(request.GET.get('device'),
                                       request.user.username)
    else:
        # Actually do the download and validate
        schemas = request.POST.get('schemas')
        if len(schemas) > 0:
            schemas = json.loads(schemas)

        return schema_json_handler(
            request, download_schemas_to_repo,
            schemas=schemas, targetrepo=targetrepo)


##########################
# End of view functions  #
# Helper functions below #
##########################


def get_schema_list(key):
    """Connect to the given device and retrieve the list of schemas.

    Helper function to :func:`list_schemas`

    Args:
      key (SessionKey): used to look up the device session

    Returns:
      dict: ``{'schemas': list of {'name': NAME, 'revision': REVISION} items``.

    Raises:
      OSError: ECONNREFUSED if unable to connect to the device.
    """
    ncs = NetconfSession.get(key)

    log.info('Trying to connect now to "%s" to get schema list',
             ncs.device_name)

    schemas = None

    if ncclient_server_capabilities(key, YANG_LIBRARY_CAP_NS):
        schemas = get_schema_list_via_ietf_yang_library(key)
        if not schemas:
            log.warning("Got an empty list of schemas from %s via "
                        "ietf-yang-library, even though it claims to "
                        "support it? Falling through to using the device's "
                        "reported capabilities instead.",
                        ncs.device_name)
    elif ncclient_server_capabilities(key, MONITORING_NS):
        schemas = get_schema_list_via_ietf_netconf_monitoring(key)
        if not schemas:
            log.warning("Got an empty list of schemas from %s via "
                        "ietf-netconf-monitoring, even though it claims to "
                        "support it? Falling through to using the device's "
                        "reported capabilities instead.",
                        ncs.device_name)
    else:
        log.info('Device "%s" does not support ietf-yang-library or '
                 'ietf-netconf-monitoring. '
                 "A partial list of modules will be derived from the device's "
                 "reported capabilities but this may be incomplete, lacking "
                 "submodules, etc.", ncs.device_name)

    # Failsafe approach
    if not schemas:
        schemas = get_schema_list_via_capabilities(key)

    log.info('Got schema list from %s - %s schemas in list',
             ncs.device_name, len(schemas))

    # Sort the schemas for user-friendly display (by name, then by revision)
    schemas.sort(key=operator.itemgetter('name', 'revision'))

    return {'schemas': schemas}


download_status = {}
"""Dict indexed by user, each with keys ``value``, ``max``, ``info``."""


def download_schemas_to_repo(key, schemas, targetrepo):
    """Download the given schemas from the given device to the given repo.

    Args:
      key (SessionKey): used to look up the device session
      schemas (list): List of [module, revision] to download from this device
      targetrepo (YSYangRepository): Repository to download the schemas into

    Note: we assume it's already been confirmed that the requestor (key.user)
    has permission to write to targetrepo!

    Returns:
      dict: See YSFileRepository.add_yang_files
    """
    global download_status

    if not schemas:
        log.error('No schemas specified')
        raise Exception("No schemas specified")

    ncs = NetconfSession.get(key)

    if not ncclient_server_capabilities(
            key,
            "urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring"):
        log.warning('Device "%s" does not support the '
                    'ietf-netconf-monitoring schema; you will have to obtain '
                    'the requested schemas from another source.',
                    ncs.device_name)
        raise OSError(errno.EPROTONOSUPPORT,
                      'Device "{0}" does not support the '
                      'ietf-netconf-monitoring schema; you will have to '
                      'obtain the requested schemas from another source.'
                      .format(ncs.device_name))

    download_status[key.user] = {
        'value': 0,
        'max': len(schemas),
        'info': '(no file in progress)',
    }

    getsc = et.Element(
        'get-schema',
        xmlns="urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring")
    ident = et.Element('identifier')
    getsc.append(ident)
    # TODO add et.Element('version') as well

    scratchdir = tempfile.mkdtemp(dir=get_path('scratch', user=key.user))
    errors = []

    try:
        log.info("Downloading %d schemas from %s", len(schemas),
                 ncs.device_name)
        with ncs:

            # Download the requested schema files from the device to scratch
            for sc in schemas:
                module, revision = sc
                log.info('Getting schema %s from %s', module, ncs.device_name)
                download_status[key.user]['info'] = (
                    "downloading {0}...".format(module))

                ident.text = module
                # TODO vers.text = revision

                file_name = module + '@' + revision + '.yang'
                file_path = os.path.join(scratchdir, file_name)
                try:
                    ret = ncs.manager.dispatch(rpc_command=getsc)
                    if not ret.ok:
                        error = et.tostring(
                            et.fromstring(ret._raw.encode('utf-8')),
                            pretty_print=True).decode()
                        errors.append(
                            (file_name,
                             'get-schema:\n{0}'.format(error))
                        )
                        continue
                    obj = et.fromstring(ret.xml.encode('utf-8'))

                    if (len(obj) > 0 and obj[0].text and obj[0].text.strip()):
                        with atomic_create(file_path, reraise=False,
                                           encoding='utf-8') as fd:
                            fd.write(obj[0].text)
                except Exception as e:
                    errors.append((file_name, str(e)))
                    pass

                download_status[key.user]['value'] += 1

        log.info('Schema download from %s completed', ncs.device_name)
        download_status[key.user]['info'] = '(all files downloaded)'

        # Sanity check
        if not (download_status[key.user]['value'] ==
                download_status[key.user]['max']):
            log.warning("Schema download finished, but didn't reach the"
                        " expected number of schemas"
                        " (downloaded %d, expected %d)",
                        download_status[key.user]['value'],
                        download_status[key.user]['max'])

        result = targetrepo.add_yang_files(scratchdir)
        result['errors'] += errors
        return result

    except Exception as e:   # TODO be more specific
        log.debug(traceback.format_exc())
        log.error('Error while downloading schemas: %s', str(e))
    finally:
        if os.path.exists(scratchdir):
            shutil.rmtree(scratchdir)


def schema_json_handler(request, callback_function, **kwargs):
    """Helper for list_schemas and download_schemas.

    Args:
      request (HttpRequest): POST with at a minimum key 'device'
      callback_function (function): Wrapped function, to call with
        ``(key=key, **kwargs)`` as its arguments and expect a response.

    Returns:
      JsonResponse: representing reply to send to user. In case of error,
      response will be sent with an appropriate status code and reason.
    """
    # Default response information
    status = 500
    result = {}
    reason = "Unknown error"

    username = request.user.username

    device = request.POST.get('device')

    if device is None:
        return JsonResponse({}, status=400, reason="No device specified")

    key = SessionKey(username, device)

    try:
        NetconfSession.get(key)
    except OSError:
        return JsonResponse({}, status=404,
                            reason='Device profile "{0}" not found'
                            .format(device))
    except NetconfNotSupported as exc:
        return JsonResponse({'reply': str(exc)},
                            status=400, reason=str(exc))

    try:
        reply = callback_function(key=key, **kwargs)
        if reply:
            # Successful request, report reply to requestor.
            # Does *not* guarantee all results within reply are "success"
            status = 200
            result['reply'] = reply
            reason = None

    except Exception as e:
        # Check if we're raising an OSError and handle appropriately
        if isinstance(e, OSError) and e.errno in [
                errno.ECONNREFUSED, errno.EPROTONOSUPPORT]:
            log.error('502: Bad Gateway error')
            return JsonResponse({}, status=502, reason=e.strerror)
        else:
            # Default error handling
            status = 500
            reason = "Exception: " + str(e)
            log.error("Server cannot process this request")
            log.debug(traceback.format_exc())

    return JsonResponse(result, status=status, reason=reason)


def download_schemas_status(device, username):
    """Helper for :func:`download_schemas`.

    Args:
      device: (str): Device name
      username (str): Username

    Returns:
      JsonResponse: reply to send to user in the form::

        {'value': <current progress count>,
         'max': <target count for completion>,
         'info': <status information string>}
    """
    global download_status
    if username not in download_status:
        return JsonResponse({
            'value': 0,
            'max': 0,
            'info': 'No request in progress'
        })
    result = download_status[username].copy()
    if result['value'] < result['max']:
        # Still downloading - estimate total work is twice the number of files
        result['max'] *= 2
    else:
        # Download complete, how's the context loading/validating status?
        ctx = context.YSContext.get_instance(username)
        if ctx:
            result['value'] += ctx.load_status['count']
            result['max'] += ctx.load_status['total']
            result['info'] = ctx.load_status['info']
        # else error...?
    return JsonResponse(result)
