# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
"""Analytics coverage APIs."""
import csv

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from yangsuite import get_logger
from ysdevices.devprofile import YSDeviceProfile
from ysfilemanager import split_user_set
from yscoverage.coverage import (
    YangCoverage,
    YangCoverageInProgress,
    YangCoverageException
)
from yscoverage.dataset import dataset_for_yangset
from yscoverage.yangdiff import getdiff


log = get_logger(__name__)


@login_required
def render_main_page(request):
    """Return the main coverage.html page."""
    devices = YSDeviceProfile.list(require_feature="ssh")

    return render(request,
                  'yscoverage/coverage.html',
                  {'devices': devices})


@login_required
def getconfig(request):
    """Get running configuration from device."""
    device = request.POST.get('device')

    if not device:
        return JsonResponse({}, status=404, reason='No device')

    dev_profile = YSDeviceProfile.get(device)

    try:
        cfg = YangCoverage.get_config(dev_profile)
    except YangCoverageException as e:
        return JsonResponse({}, status=404, reason=str(e))

    return JsonResponse({'config': cfg})


def getreleases(request):
    """Get releases to choose from for model coverage."""
    if request.method == 'POST':
        ios = request.POST.get('ios')
        uri = request.POST.get(
            'uri',
            "http://yang-suite.cisco.com:8480/coverage/getreleases")

        if not ios:
            return JsonResponse({}, status=404, reason='No platform specified')

        releases = YangCoverage.get_releases(ios)

        if 'releases' in releases and not len(releases['releases']):
            # Try base server
            releases = YangCoverage.get_base_releases(uri + '?ios=' + ios)
            JsonResponse(releases)

        return JsonResponse(releases)
    else:
        ios = request.GET.get('ios', 'xe')

        releases = YangCoverage.get_releases(ios)

        return JsonResponse(releases)


@login_required
def getcoverage(request):
    """Get model coverage."""
    if request.method == 'POST':

        port = request.POST.get('port', '')
        cli = request.POST.get('cli')
        uri = request.POST.get('uri')
        timeout = request.POST.get('timeout', 120)
        coverage = ''
        xml = ''

        if not cli:
            return JsonResponse({}, status=404, reason='No config to test')

        while timeout:
            try:
                coverage, xml = YangCoverage.get_coverage(cli,
                                                          port,
                                                          uri)
                timeout = 0
            except YangCoverageInProgress:
                timeout -= 1
            except Exception as e:
                return JsonResponse({}, status=404, reason=str(e))

        result = {'coverage': coverage,
                  'xml': xml,
                  'average': YangCoverage.average_lines_per_second}

        return JsonResponse(result)

    else:

        return JsonResponse(YangCoverage.get_progress())


@login_required
def render_datasets_page(request):
    """Return the datasets.html page."""
    return render(request,
                  'yscoverage/dataset.html')


@login_required
def get_dataset(request):
    """Get XPath dataset for a given module and yangset."""
    model = request.POST.get('model') or request.GET.get('model')
    yangset = request.POST.get('yangset') or request.GET.get('yangset')
    addons = (request.POST.getlist('addons[]') or
              request.GET.getlist('addons[]'))
    fmt = request.POST.get('format') or request.GET.get('format')
    all_data = request.POST.get('all_data') or request.GET.get('all_data')
    if all_data == 'true':
        all_data = True
    else:
        all_data = False

    if not model:
        return JsonResponse({}, status=400, reason='No model specified.')
    if not yangset:
        return JsonResponse({}, status=400, reason='No yangset specified.')
    if not fmt:
        fmt = 'json'

    owner, setname = split_user_set(yangset)
    data = dataset_for_yangset(owner, setname, model, addons,
                               reference=request.user.username,
                               all_data=all_data)

    if fmt == 'json':
        return JsonResponse(data)
    elif fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s.csv' % model

        writer = csv.writer(response)
        # Add header row
        writer.writerow(data['header'])
        # Write data
        for row in data['data']:
            writer.writerow(row)
        return response
    else:
        return JsonResponse({}, status=400, reason='Unrecognized "format"')


@login_required
def get_diff(request):
    """Get diffs from two versions of a model."""
    model = request.POST.get('model') or request.GET.get('model')
    from_set = request.POST.get('fromset') or request.GET.get('fromset')
    to_set = request.POST.get('toset') or request.GET.get('toset')
    addons = (request.POST.getlist('addons[]') or
              request.GET.getlist('addons[]'))
    fmt = request.POST.get('format') or request.GET.get('format')

    if not model:
        return JsonResponse({}, status=400, reason='No model specified.')
    if not from_set:
        return JsonResponse({}, status=400, reason='No "from" yangset given.')
    if not to_set:
        return JsonResponse({}, status=400, reason='No "to" yangset given.')
    if not fmt:
        fmt = 'json'

    addons.append("nodetype")
    try:
        from_dataset = dataset_for_yangset(*split_user_set(from_set),
                                           model,
                                           addons,
                                           reference=request.user.username)
        to_dataset = dataset_for_yangset(*split_user_set(to_set),
                                         model,
                                         addons,
                                         reference=request.user.username)
    except:
        return JsonResponse(
            {}, status=400,
            reason='Error loading the module.'
            )

    data = getdiff(from_dataset,
                   to_dataset)

    if fmt == 'json':
        return JsonResponse(data)
    elif fmt == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=diff.csv'

        writer = csv.writer(response)
        writer.writerow(data['header'])
        for row in data['data']:
            writer.writerow(row)
        return response
    else:
        return JsonResponse({}, status=400, reason='Unrecognized "format"')
