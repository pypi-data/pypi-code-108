from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse
from django.core import serializers
from .forms.forms import CalibrationForm
from .models.models import Calibration


def index(request):
    context = {'title': 'HomeHub'}
    return render(request, 'home.html', context)
#
#
# def postFriend(request):
#     # request should be ajax and method should be POST.
#     if request.is_ajax and request.method == "POST":
#         # get the form data
#         form = FriendForm(request.POST)
#         # save the data and after fetch the object in instance
#         if form.is_valid():
#             instance = form.save()
#             # serialize in new friend object in json
#             ser_instance = serializers.serialize('json', [instance, ])
#             # send to client side.
#             return JsonResponse({"instance": ser_instance}, status=200)
#         else:
#             # some form errors occured.
#             return JsonResponse({"error": form.errors}, status=400)
#
#     # some error occured
#     return JsonResponse({"error": ""}, status=400)
#
#
# # chat/views.py
# from django.shortcuts import render
#
#
# def start(request):
#     return render(request, 'start.html', {})
#
#
# def calibrate(request, room_name):
#     return render(request, 'calibrate.html', {
#         'room_name': room_name
#     })
