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

# Create your views here.
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.urls import reverse
from social_layer.mediautils.utils import handle_upload_file

from social_layer.utils import get_social_profile
from social_layer.comments.models import Comment
from social_layer.profiles.models import SocialProfile, SocialProfilePhoto
from social_layer.utils import execute_string

@login_required
def setup_profile(request):
    """ Setup the social profile settings """
    did_exist = SocialProfile.objects.filter(user=request.user).exists()
    sprofile = get_social_profile(request)
    alt_setup = getattr(settings, 'SOCIAL_ALT_SETUP_PROFILE', None)
    if alt_setup:
        # pass an alternative function if your app needs
        # this should should None if expects the normal behavior
        response = execute_string(alt_setup, request)
        if response:
            return response
    redir_after = request.COOKIES.get('slogin_next', None)
    if request.method == "POST":
        sprofile.nick = request.POST.get('nick', '')
        sprofile.phrase = request.POST.get('phrase', '')
        for upload_file in request.FILES:
            foto = handle_upload_file(file_post=request.FILES[upload_file],
                                        quality=2,
                                        Model=SocialProfilePhoto,
                                        extra_args={'profile': sprofile})
            if foto:
                oldies = SocialProfilePhoto.objects.exclude(pk=foto.pk).filter(profile=sprofile)
                oldies.delete()
        sprofile.save()
        # TODO handle spam optin
        receive_email = bool(request.POST.get('receive_email', ''))
        if redir_after:
            resp = redirect(redir_after)
            resp.delete_cookie('slogin_next')
            return resp
        else:
            return redirect(sprofile.get_url())
    data = {
        'sprofile': sprofile,
        'did_exist': bool(did_exist),
        'redir_after': redir_after,
        }
    return render(request, 'social_layer/profiles/setup_profile.html', data)
    
def view_profile(request, pk):
    """ View the User's profile page """
    sprofile = SocialProfile.objects.filter(pk=pk).first()
    if not sprofile:
        raise Http404()
    alt_view = getattr(settings, 'SOCIAL_ALT_VIEW_PROFILE', None)
    if alt_view:
        # pass an alternative function if your app needs.
        # this should return None if excpets the normal behavior
        response = execute_string(alt_view, request, sprofile)
        if response:
            return response
    data = {
        'sprofile': sprofile,
        'comments': Comment.objects.filter(author=sprofile)
        }
    # a callable that returns a dict for the social profile view
    if getattr(settings, 'SOCIAL_PROFILE_CONTEXT', None):
        extra = execute_string(settings.SOCIAL_PROFILE_CONTEXT, sprofile)
        data.update(extra)
    return render(request, 'social_layer/profiles/profile.html', data)


def social_login(request):
    """ 
    The Implementing application MUST take care of authentication.
    Any action that requires a social login must be redirected here. 
    It will redirect the user to the 'social' login page.
    This url is defined by: settings.SOCIAL_VISITOR_LOGIN
    """
    next_url = request.GET.get('next', '/')
    resp = redirect('/'+settings.SOCIAL_VISITOR_LOGIN)
    resp.set_cookie('slogin_next', next_url, expires=360) 
    return resp


def list_profiles(request):
    """ List other people's profiles """
    list_profiles = SocialProfile.objects.all().order_by('?')
    data = {'list_profiles': list_profiles[0:100],}
    return render(request, 'social_layer/profiles/list_profiles.html', data)


def delete_profile_photo(request):
    """ The delete the user's photo """
    profile = get_social_profile(request)
    pic = profile.picture()
    if pic is not None:
        pic.delete()
    #post = get_object_or_404(SocialProfilePhoto,
                             #pk=pk, profile__user=request.user)
    #post.delete()
    return redirect(reverse('social_layer:setup_profile'))
 
