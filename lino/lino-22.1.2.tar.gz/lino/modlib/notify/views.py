# Copyright 2008-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import json
from django.views.generic import View
from lino.core.views import json_response
from .models import Subscription

class PushSubscription(View):
    def get(self, request):
        s = json.loads(request.GET.get('sub'))
        fields = dict(endpoint=s['endpoint'],
            auth=s['keys']['auth'], p256dh=s['keys']['p256dh'])
        lang = request.GET.get('lang')
        if lang:
            fields.update(lang=lang)
        userAgent = request.GET.get('userAgent')
        if userAgent:
            fields.update(userAgent=userAgent)
        sub, _ = Subscription.objects.get_or_create(**fields)
        if str(request.user) == 'anonymous':
            sub.user = None
        else:
            sub.user = request.user
        sub.full_clean()
        sub.save()
        return json_response({'success': True})
