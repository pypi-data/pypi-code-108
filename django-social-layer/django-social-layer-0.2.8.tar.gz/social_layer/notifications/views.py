# This file is part of django-social-layer
#
#    django-social-layer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    django-social-layer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with django-social-layer. If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from social_layer.notifications.models import Notification

@login_required
def view_notifications(request):
    """ List the past notifications """
    list_notif = Notification.objects.filter(to=request.user).order_by('-date_time')
    data = {
        'list_notif': list_notif,
        'has_notif': False,
        }
    response = render(request, 'social_layer/notifications/view_notifications.html', data)
    list_notif.filter(read=False).update(read=True)
    return response

def get_notifications(request):
    """ Returns a list of unread notifications of logged in user """
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(to=request.user, read=False)
    else:
        notifs = Notification.objects.none()
    return notifs

@staff_member_required
def admin_send_notification(request, pk):
    user = get_user_model().objects.get(pk=pk)
    if request.method == "POST":
        notif = Notification.objects.create(to=user,
                                            text=request.POST.get('text'))
    list_notifs = Notification.objects.filter(to=user).order_by('-id')
    data = {'list_notif': list_notifs,}
    return render(request, 'social_layer/notifications/admin_send_notification.html', data)
