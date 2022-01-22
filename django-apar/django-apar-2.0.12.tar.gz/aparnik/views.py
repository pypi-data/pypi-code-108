# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http.response import JsonResponse
from django.utils.html import strip_tags

from aparnik.contrib.basemodels.models import BaseModel


def install(request):
    context = {
        'title': 'نصب'
    }
    template_name = 'aparnik/index.html'
    return render(request, template_name=template_name, context=context)


def share(request):
    # q['id'] = model.pk
    # q['type'] = model.resourcetype
    # q['ref'] = ''
    # TODO: handle
    # چه کسی فرستاده؟
    # چه کسی باز کرده؟
    pk = request.GET.get('id', 0)
    ref = request.GET.get('ref', '')
    # TODO: use ref
    model = get_object_or_404(BaseModel.objects.all(), pk=pk).get_real_instance()
    title = strip_tags(model.get_title())
    description = strip_tags(model.get_description())

    context = {
        'title': title,
        'description': description,
        'app_url': request.build_absolute_uri(model.get_api_uri()),
        'install_app_url': request.build_absolute_uri(reverse('aparnik:install')),
        'model': model,
    }
    template_name = 'aparnik/share.html'
    return render(request, template_name=template_name, context=context)
