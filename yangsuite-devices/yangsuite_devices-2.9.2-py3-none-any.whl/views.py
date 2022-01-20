# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import json
import os
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from yangsuite import get_path
from yangsuite.logs import get_logger
from ysfilemanager import YSYangRepository, YSMutableYangSet
from .devprofile import YSDeviceProfile, YSDeviceProfileValidationError
from ysnetconf.nconf import SessionKey
from ysnetconf.views.download import get_schema_list, download_schemas_to_repo


log = get_logger(__name__)


def json_request(decoratee):
    """Decorator for views that expect a request in JSON format."""
    def decorated(request, **kwargs):
        jsondata = {}
        if request.body:
            try:
                jsondata = json.loads(request.body.decode('utf-8'))
                if 'csrfmiddlewaretoken' in jsondata:
                    del jsondata['csrfmiddlewaretoken']
            except json.decoder.JSONDecodeError:
                return JsonResponse({}, status=400,
                                    reason="Malformed JSON request")
        return decoratee(request, jsondata, **kwargs)
    decorated.__doc__ = decoratee.__doc__
    return decorated

###############################
# Django view functions below #
###############################


@login_required
def devices_page(request):
    """Get the main "device profiles list" setup page."""
    from django.contrib.auth.models import User
    return render(request, 'ysdevices/device.html',
                  {
                      'users': User.objects.all(),
                      'data_info': YSDeviceProfile.data_format(),
                  })


@login_required
@json_request
def create_default_repo_yangset(request, json_data, device_key=None):
    """Create default Repository and Yangset for
       the given device profile from the server.

    Args:
      request (HttpRequest): GET
      device_key (str): Required

    Returns:
      JsonResponse: either a HTTP 200 success message with no content,
        or an error message with possible dict {'errors': errors} for details.
    """

    if request.method != "GET":
        return JsonResponse({}, status=405,
                            reason="Method not allowed")

    if not device_key:
        return JsonResponse({}, status=400,
                            reason="Device key not specified")

    reponame = device_key + "-default-repo"
    setname = device_key + "-default-yangset"

    user = request.user.username
    device_profile = None
    try:
        device_profile = YSDeviceProfile.get(device_key)
        result = device_profile.check_reachability()
        if not result['status']:
            return JsonResponse({}, status=404,
                                reason="The device is not reachable")
        else:
            newrepo = YSYangRepository.create(user, reponame)

        key = SessionKey(user, device_key)
        schema_list = get_schema_list(key)
        ys_schema_list = [[sl['name'],
                           ('unknown' if sl['revision'] is None else
                           sl['revision'])]
                          for sl in schema_list['schemas']]
        download_schemas_to_repo(key, ys_schema_list, newrepo)
    except OSError:
        return JsonResponse({}, status=403,
                            reason="A repository by that name already exists")

    try:
        ys = YSMutableYangSet(
                  user,
                  setname,
                  ys_schema_list,
                  reponame=reponame
                  )
        ys.write()
    except Exception as exc:
        return JsonResponse({}, status=500, reason=str(exc))

    return JsonResponse(
        {
            'repository': newrepo.slug,
            'set': setname
        },
        status=200,
        reason="Request reached"
    )


@login_required
@json_request
def device_crud(request, json_data, device_key=None):
    """Create, read, update, or delete the given device profile.

    Args:
      request (HttpRequest): POST, GET, PATCH, or DELETE request
      device_key (str): Required for GET, PATCH, or DELETE; ignored for POST.

    Returns:
      JsonResponse: either a HTTP 200 success message with no content,
        or an error message with possible dict {'errors': errors} for details.
      HttpResponse: for a generic "GET" request with no parameters
        (rendering the device.html page)
    """
    if request.method != "POST":
        if not device_key:
            return JsonResponse({}, status=400,
                                reason="Device key not specified")
    if request.method == "POST":
        json_data['yangsuite'] = {'user': request.user.username}
        return create_device(json_data)
    elif request.method == "PATCH":
        return update_device(device_key, json_data, request.user.username)
    elif request.method == "DELETE":
        return delete_device(device_key, request.user.username)
    else:    # GET
        try:
            return JsonResponse(
                {'device': YSDeviceProfile.get(device_key).dict()})
        except OSError:
            return JsonResponse(
                {},
                status=404,
                reason='Unable to load device profile "{0}"'
                .format(device_key))


@login_required
@json_request
def file_upload(request, json_data, device_key):
    """Save file associated to a device profile.

    Args:
      request (HttpRequest): POST request
      device_key (str): Required for POST.

    Returns:
      JsonResponse: either a HTTP 201 success message with no content,
        or an error message with possible dict {'errors': errors} for details.
    """
    try:
        profile = YSDeviceProfile.get(device_key)
    except OSError:
        return JsonResponse(
            {},
            status=404,
            reason='Unable to load device profile "{0}"'.format(device_key))
    try:
        json_data['user'] = request.user.username
        profile.upload(device_key, json_data)
        return JsonResponse({'message': "Upload Successful"}, status=201)
    except OSError:
        return JsonResponse({},
                            status=404,
                            reason="Unable to upload {0}".format(
                               json_data.get('file_name', 'file')
                            ))


def create_device(data):
    """Create, validate, and possibly save a new device profile.

    Helper to :func:`device_crud`.
    """
    try:
        profile = YSDeviceProfile(data)
    except YSDeviceProfileValidationError as e:
        return JsonResponse({'errors': e.errors}, status=400)
    # Make sure no existing device profile would be overwritten
    try:
        YSDeviceProfile.get(profile.base.profile_name)
        return JsonResponse({}, status=403,
                            reason="A profile by that name already exists")
    except OSError:
        pass
    result, message = profile.write()
    if result:
        return JsonResponse({'message': message}, status=201)
    else:
        return JsonResponse({'message': message}, status=400)


def update_device(device_key, data, user):
    """Validate changes to an existing profile and save if valid.

    Helper to :func:`device_crud`.
    """
    try:
        profile = YSDeviceProfile.get(device_key)
    except OSError:
        return JsonResponse(
            {},
            status=404,
            reason='Unable to load device profile "{0}"'.format(device_key))

    try:
        ys_data = profile.dict().get('yangsuite', {})
        ys_user = ys_data.get('user', '')
        if not ys_user:
            # Old profile not pinned to yangsuite user
            data['yangsuite'] = {'user': user}
        elif ys_user != user:
            return JsonResponse(
                {'message': '{0} does not own device profile'.format(user)},
                status=401)
        if not data.get('base', {}).get('variables', ''):
            data.get('base', {})['variables'] = {}
        profile.update(data)
    except YSDeviceProfileValidationError as e:
        return JsonResponse({'errors': e.errors}, status=400)
    result, message = profile.write()
    if result:
        return JsonResponse({'message': message}, status=201)
    else:
        return JsonResponse({'message': message}, status=400)


def delete_device(device_key, user):
    """Delete a device profile. Helper for :func:`device_crud`."""
    profile = YSDeviceProfile.get(device_key)
    ys_data = profile.dict().get('yangsuite', {})
    ys_user = ys_data.get('user', '')

    if ys_user and ys_user != user:
        return JsonResponse(
            {'message': '{0} does not own device profile'.format(user)},
            status=401)

    result, message = YSDeviceProfile.delete(device_key, user)
    if result:
        return JsonResponse({'message': message})
    else:
        return HttpResponse(status=400, reason=message)


@login_required
def list_devices(request):
    """Get the listing of device profiles, optionally filtered."""
    return JsonResponse({'devices': YSDeviceProfile.list()})


@login_required
def new_device_form(request):
    """Get the blank form used to define a new profile.

    Note that the return is an HTML snippet ``<form>...</form>`` and not a
    complete web page.
    """
    return render(request, 'ysdevices/device_form.html',
                  {
                      'data_format': YSDeviceProfile.data_format(),
                  })


@login_required
def edit_device_form(request, device_key):
    """Get the form used to edit an existing profile.

    Note that the return is an HTML snippet ``<form>...</form>`` and not a
    complete web page.
    """
    try:
        profile = YSDeviceProfile.get(device_key)
    except OSError:
        return JsonResponse(
            {},
            status=404,
            reason='Unable to load device profile "{0}"'
            .format(device_key))
    data_format = YSDeviceProfile.data_format()
    for category, data in profile.dict().items():
        for key, value in data.items():
            if category not in data_format:
                continue
            if key not in data_format[category]['data']:
                if value and key.startswith('encrypted_'):
                    _, _, key = key.partition('encrypted_')
                    if key in data_format[category]['data']:
                        data_format[category]['data'][key]['default'] = (
                            "_placeholder_")
                continue
            data_format[category]['data'][key]['default'] = value

    return render(request, 'ysdevices/device_form.html',
                  {
                      'data_format': data_format,
                  })


@login_required
@json_request
def check_device(request, json_data, device_key=None):
    """Confirm reachability of the given device profile.

    Returns:
      JsonResponse: information about device reachability (on success)
      or an error status with a possible {'errors': ...} dict.
    """
    device_profile = None
    profile_name = ''
    profile_data = ''
    if request.method == 'GET':
        # Request to check connectivity of an existing device
        if not device_key:
            return JsonResponse({}, status=400,
                                reason="Device key not specified")
        device_profile = YSDeviceProfile.get(device_key)
    else:
        # Request to check connectivity of a new/updated device
        try:
            if device_key:
                device_profile = YSDeviceProfile.get(device_key)
            else:
                device_profile = YSDeviceProfile(
                    {
                        'yangsuite': {
                            'user': request.user.username
                        }
                    }
                )

            device_profile.update(json_data)
        except YSDeviceProfileValidationError as e:
            return JsonResponse({'errors': e.errors}, status=400)

    if not device_profile:
        return JsonResponse(
            {},
            status=404,
            reason='Device profile "{0}" not found'.format(device_key))

    # Check if older profile is not pinnned to a yangsuite user
    if 'yangsuite ' not in device_profile.dict():
        device_profile.update(
            {
                'yangsuite': {
                    'user': request.user.username
                }
            }
        )

    profile_name = device_profile.base.profile_name
    try:
        profile_data = YSDeviceProfile.get(profile_name)
        result = device_profile.check_reachability()

    except FileNotFoundError:
        create_device(json_data)
        profile_data = YSDeviceProfile.get(profile_name)
        result = device_profile.check_reachability()
        delete_device(profile_name, request.user.username)

    # retrieve the device OS type and the OS version from the json file
    device_path = get_path('devices_dir')
    device_json_path = os.path.join(device_path, 'device_stats.json')
    if os.path.exists(device_json_path):
        with open(device_json_path, 'r') as fd:
            json_data = json.load(fd)
        if json_data.get(device_profile.base.profile_name, ''):
            result['os_type'] = json_data[profile_name]['os_type']
            result['os_ver'] = json_data[profile_name]['os_ver']

    # If SSH is not enabled, retrive the os_type from the device profile.
    else:
        result['os_ver'] = ''
        if hasattr(profile_data, 'gnmi'):
            if profile_data.netconf.enabled and profile_data.gnmi.enabled:
                result['os_type'] = profile_data.netconf.device_variant
            elif profile_data.gnmi.enabled:
                result['os_type'] = profile_data.gnmi.platform
            elif profile_data.netconf.enabled:
                result['os_type'] = profile_data.netconf.device_variant
        elif profile_data.netconf.enabled:
            result['os_type'] = profile_data.netconf.device_variant

    log.info("Connectivity check for %s: %s",
             device_profile.base.profile_name, result)
    return JsonResponse(result)
