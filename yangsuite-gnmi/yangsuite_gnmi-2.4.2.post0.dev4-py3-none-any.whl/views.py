import json
import traceback

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from yangsuite import get_logger
from ysdevices import YSDeviceProfile
from ysfilemanager import split_user_set, YSYangSet
from ysyangtree.views import ctx_status

from ysgnmi import gnmi
from ysgnmi.yangtree import YSGnmiYangtree
from ysyangtree.models import YangSetTree
from ysyangtree.yangsettree import get_yangset_tree, create_yangset_tree
from ysyangtree.ymodels import DEFAULT_INCLUDED_NODETYPES
from ysyangtree.views.yangtree import create_display_node


log = get_logger(__name__)


@login_required
def render_main_page(request, yangset=None, modulenames=None):
    """Return the main gnmi.html page."""
    return render(request, 'ysgnmi/gnmi.html', {
        'devices': YSDeviceProfile.list(require_feature="gnmi"),
        'yangset': yangset or '',
        'modulenames': modulenames or '',
    })


@login_required
def get_json_tree(request):
    """Retrieve context and build the JSTree based on model name(s).

    Args:
      request (django.http.HttpRequest): HTTP POST request

        - names (list): module name(s) to parse
        - yangset (str): YANG set slug 'owner+setname' to use with context

    Returns:
      django.http.JsonResponse: JSTree data
    """
    if request.method == 'POST':
        names = request.POST.getlist('names[]')

        if not names:
            return JsonResponse({}, status=400,
                                reason="No model name(s) specified")

        yangset = request.POST.get('yangset')
        if not yangset:
            return JsonResponse({}, status=400,
                                reason="No yangset specified")
        try:
            owner, setname = split_user_set(yangset)
        except ValueError:
            return JsonResponse({}, status=400,
                                reason="Invalid yangset string")
        try:
            ys = YSYangSet.load(owner, setname)
        except (OSError, ValueError):
            return JsonResponse({}, status=404, reason="No such yangset")
        except RuntimeError:
            return JsonResponse({}, status=404, reason="No such yangset owner")

        if ys:
            pass

        ref = request.POST.get('reference')
        if not ref:
            ref = request.user.username

        ysettree = get_yangset_tree(owner, setname, names, ref,
                                    plugin_name='yangsuite-gnmi')

        if ysettree and isinstance(ysettree, YangSetTree):
            ysettree = ysettree
        else:
            add_modules = {'module': names}
            repository = request.POST.get('repository')
            if not repository:
                repository = ''

            ysettree = create_yangset_tree(
                                owner, setname,
                                add_modules, repository,
                                ref,
                                plugin_name='yangsuite-gnmi',
                                child_class=YSGnmiYangtree)
        modules_data = []

        if isinstance(ysettree, YangSetTree):
            modules_details = json.loads(ysettree.set_modules).get('moduledet')
            for name in names:
                for num in range(len(modules_details)):
                    if (modules_details[num].get('name') == name):
                        if modules_details[num].get('type') == 'submodule':
                            main_mod = modules_details[num].get('main_module')
                            if main_mod not in names:
                                names.append(main_mod)
                        else:
                            arg_mod = modules_details[num].get('augments')
                            if arg_mod:
                                for add in arg_mod:
                                    if add not in names:
                                        names.append(add)

            tree_data = json.loads(ysettree.data).get('data')

            for name in names:
                for num in range(len(tree_data)):
                    if (tree_data[num]['text'] == name):
                        child_dict = {}
                        child_dict = create_display_node(
                                      tree_data[num],
                                      DEFAULT_INCLUDED_NODETYPES)

                        modules_data.append(child_dict)

        return JsonResponse({'data': modules_data,
                             'included_nodetypes': sorted(
                              DEFAULT_INCLUDED_NODETYPES)})
    else:
        return ctx_status(request.user.username, request.GET.get('yangset'))


@login_required
def build_get_request(request):
    """Build the parameters of a gNMI Get request.

    Args:
      request (django.http.HttpRequest) HTTP POST request with JSON content,
        of the form::

          {
            devprofile: 'my-device',
            origin: 'openconfig',
            modules: {
              'moduleA': {
                namespace_modules: { ... },
                entries: [
                  {xpath:, value:, nodetype:, datatype:},
                  ...
                ]
              }
            }
          }

    Returns:
      django.http.JsonResponse: JSON representation of GetRequest protobuf
    """
    try:
        jsondata = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({}, status=400, reason="Invalid JSON")

    if 'device' not in jsondata or not jsondata['device']:
        return JsonResponse({}, status=400, reason="No device specified")
    try:
        devprofile = YSDeviceProfile.get(jsondata['device'])
    except OSError:
        return JsonResponse({}, status=404, reason="No such device found")

    try:
        request_str = ''
        jsondata['platform'] = devprofile.gnmi.platform
        if jsondata.get('action') == 'get':
            request_str = gnmi.get_request(
                request.user.username,
                devprofile,
                jsondata
            )
        elif jsondata.get('action') == 'subscribe':
            request_str = gnmi.subscribe_request(
                request.user.username,
                devprofile,
                jsondata
            )
        return JsonResponse({'gnmiMsgs': request_str})

    except Exception as exc:
        return JsonResponse({}, status=404, reason=str(exc))


@login_required
def build_set_request(request):
    """Build the parameters of a gNMI Set request.

    Args:
      request (django.http.HttpRequest) HTTP POST request with JSON content,
        of the form::

          {
            devprofile: 'my-device',
            origin: 'openconfig',
            modules: {
              'moduleA': {
                namespace_modules: { ... },
                entries: [
                  {xpath:, value:, nodetype:, datatype:, edit-op:},
                  ...
                ]
              }
            }
          }

    Returns:
      django.http.JsonResponse: JSON representation of SetRequest protobuf
    """
    try:
        jsondata = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({}, status=400, reason="Invalid JSON")

    if 'device' not in jsondata or not jsondata['device']:
        return JsonResponse({}, status=400, reason="No device specified")
    try:
        devprofile = YSDeviceProfile.get(jsondata['device'])
    except OSError:
        return JsonResponse({}, status=404, reason="No such device found")

    request_str = ''
    jsondata['platform'] = devprofile.gnmi.platform
    jsondata['action'] = 'set'
    request_str = gnmi.set_request(
        request.user.username,
        devprofile,
        jsondata
    )

    return JsonResponse({'gnmiMsgs': request_str})


@login_required
def run_result(request, device):
    """Render the result web page that polls for test results."""
    return render(request, 'ysgnmi/result.html', {'device': device})


@login_required
def run_request(request, device):
    """Run the gNMI request described by the given parameters.

    Args:
      request (django.http.HttpRequest): HTTP POST request with JSON body.
      device (str): Device profile slug
    """
    if request.method == 'POST':
        try:
            devprofile = YSDeviceProfile.get(device)
        except OSError:
            return JsonResponse({}, status=404, reason="No such device found")
        try:
            jsondata = json.loads(request.body.decode('utf-8'))
        except ValueError:
            return JsonResponse({}, status=400, reason="Invalid JSON")

        if 'action' not in jsondata:
            return JsonResponse({}, status=400, reason="No action specified")

        try:
            user = request.user.username
            action = jsondata["action"]
            jsondata['run'] = True

            if action == 'capabilities':
                return JsonResponse(
                    {'capabilities': gnmi.get_capabilities(user, devprofile)}
                )
            elif action == 'get':
                return JsonResponse(
                    {'response': gnmi.get_request(user, devprofile, jsondata)}
                )
            elif action == 'set':
                return JsonResponse(
                    {'response': gnmi.set_request(user, devprofile, jsondata)}
                )
            elif action == 'subscribe':
                return JsonResponse(
                    {'response': gnmi.subscribe_request(
                        user, devprofile, jsondata
                    )}
                )
            else:
                return JsonResponse({}, status=400, reason="Unknown action")
        except Exception as exc:
            if hasattr(exc, 'code'):
                log.error(exc.code())
                log.error(exc.details())
                codename = exc.code().name
                if codename == "UNAVAILABLE":
                    return JsonResponse({}, status=500,
                                        reason="Connection to device failed")
                elif codename == "UNIMPLEMENTED":
                    return JsonResponse({}, status=501, reason=exc.details())
                return JsonResponse({}, status=500, reason=exc.details())
            return JsonResponse({}, status=500, reason=str(exc))
    else:
        device = request.GET.get('device')
        try:
            devprofile = YSDeviceProfile.get(device)
        except OSError:
            return JsonResponse({}, status=404, reason="No such device found")
        result = gnmi.get_results(request.user.username, devprofile)
        if not result:
            result = {'result': 'Waiting for response'}
        if result:
            try:
                json.dumps(result)
            except Exception:
                result = {'result': ['ERROR:\n{0}'.format(str(result))]}

        return JsonResponse(result)


@login_required
def stop_session(request, device):
    try:
        devprofile = YSDeviceProfile.get(device)
    except OSError:
        return JsonResponse({}, status=404, reason="No such device found")

    try:
        gnmi.stop_session(request.user.username, devprofile)
    except OSError:
        return JsonResponse({}, status=404, reason="Failed to stop session.")

    return JsonResponse({}, status=201)


# TODO: replay run from testmgr not adjusted to new version yet.
@login_required
def test_run(request):
    """Render initial test run page."""
    try:
        from ystestmgr import testmgr
    except ImportError:
        return JsonResponse(
            {}, status=501, reason="yangsuite-testmanager not installed"
        )
    if request.method == 'POST':
        config = request.POST.get('config')
        if 'type' not in config or 'name' not in config:
            return JsonResponse(
                {}, status=400, reason='Invalid request: {0}'.format(
                    str(config)))
        else:
            try:
                config = json.loads(config)
                result = testmgr.runner(user=request.user.username,
                                        config=config)
                return JsonResponse(result, status=200)
            except testmgr.TestMgrException as e:
                log.error(str(e))
                return JsonResponse({}, status=400, reason=str(e))
            except Exception as e:
                log.error(traceback.format_exc())
                return JsonResponse({}, status=400, reason=str(e))

    else:

        config = request.GET.get('config')
        config = json.loads(config)
        user = request.user.username

        if 'device' not in config or 'name' not in config:
            return JsonResponse({'reply': '\n<pre>{0}</pre>\n'.format(
                'KEY ERROR: Unable to retrieve Run Status.')})

        data = testmgr.get_log_data(user, config['device'], config['name'])

        return JsonResponse({'reply': data})


@login_required
def run_replay(request, device):
    """Run the replay over gNMI protocol.

    Args:
      request (django.http.HttpRequest): HTTP POST request with JSON body.
      device (str): Device profile slug
    """
    # TODO: add this support
    try:
        devprofile = YSDeviceProfile.get(device)
    except OSError:
        return JsonResponse({}, status=404, reason="No such device found")

    try:
        jsondata = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({}, status=400, reason="Invalid JSON")

    try:
        if 'replay' not in jsondata or 'category' not in jsondata:
            return JsonResponse(
                {}, status=400, reason="Invalid {0}:{1}".format(
                    str(jsondata.get('replay')),
                    str(jsondata.get('category'))
                ))
        jsondata['user'] = request.user.username
        return JsonResponse(
            {'replay': gnmi.run_gnmi_replay(devprofile, jsondata)}
        )

    except Exception as exc:
        log.error(exc.code())
        log.error(exc.details())
        codename = exc.code().name
        if codename == "UNAVAILABLE":
            return JsonResponse({}, status=500,
                                reason="Connection to device failed")
        elif codename == "UNIMPLEMENTED":
            return JsonResponse({}, status=501, reason=exc.details())
        else:
            return JsonResponse({}, status=500, reason=exc.details())


@login_required
def show_replay(request):
    """Return the replay message in requested format.

    Args:
      request (django.http.HttpRequest): HTTP POST request with JSON body.

    """
    try:
        jsondata = json.loads(request.body.decode('utf-8'))
    except ValueError:
        return JsonResponse({}, status=400, reason="Invalid JSON")

    if 'replay' not in jsondata or 'category' not in jsondata:
        return JsonResponse(
            {}, status=400, reason="Invalid {0}:{1}".format(
                str(jsondata.get('replay')),
                str(jsondata.get('category'))
            ))
    jsondata['user'] = request.user.username

    try:
        gnmi_replay = gnmi.show_gnmi_replay(jsondata)
        if not gnmi_replay:
            return JsonResponse(
                {}, status=500, reason="Unable to translate replay"
            )
        return JsonResponse({'gnmi_replay': gnmi_replay})

    except Exception as exe:
        return JsonResponse({}, status=500, reason=str(exe))
