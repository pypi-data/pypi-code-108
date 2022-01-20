# Copyright 2016 to 2021, Cisco Systems, Inc., all rights reserved.
import socket
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from yangsuite import get_logger
from ysdevices import YSDeviceProfile
from .grpctelemetry import YSGrpcTelemetryServer

log = get_logger(__name__)


@login_required
def render_main_page(request):
    """Return the main grpctelemetry.html page."""
    devices = YSDeviceProfile.list(require_feature="netconf")
    return render(request, 'ysgrpctelemetry/grpctelemetry.html',
                  {'devices': devices})


@login_required
def start_servicer(request, port):
    """Start servicer listening on the given port (and IP)."""
    address = request.POST.get('address')
    if address in ['localhost', '127.0.0.1']:
        try:
            address = socket.gethostbyname(socket.gethostname())
        except socket.gaierror:
            address = request.POST.get('address')
    secure = request.POST.get('secure', None)
    result, message = YSGrpcTelemetryServer.serve(
        address, port, request.user.username, secure,
    )
    return JsonResponse({'result': result, 'message': message})


@login_required
def stop_servicer(request, port):
    """Stop servicer listening on the given port."""
    result, message = YSGrpcTelemetryServer.stop(port)
    return JsonResponse({'result': result, 'message': message})


@login_required
def get_servicer_list(request):
    servers = []
    for s in YSGrpcTelemetryServer.servers.items():
        if s:
            port, svr = s
            _, _, ip, tls, out_file, out_uri = svr
            servers.append([ip, port, tls, out_file, out_uri])
    fileout = YSGrpcTelemetryServer.out_file
    uri = YSGrpcTelemetryServer.out_uri
    return JsonResponse(
        {"servers": servers, 'fileout': fileout, 'uri': uri}
    )


@login_required
def set_output(request):
    """Set telemetry output destinations."""
    result = {}
    file_output = request.POST.get('file')
    uri = request.POST.get('uri')
    print(file_output, uri)
    if file_output or uri:
        YSGrpcTelemetryServer.set_output(file_output, uri)
    return JsonResponse(result)


@login_required
def get_output(request):
    """Get the latest output from any given listener stream."""
    result = YSGrpcTelemetryServer.get_output()
    return JsonResponse(result)
