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

from importlib import import_module
from social_layer.profiles.models import SocialProfile, SocialProfilePhoto

def get_social_profile_byuser(user):
    """ returns a SocialProfile object given an user """
    sprofile = SocialProfile.objects.filter(user=user).first()
    if not sprofile:
        sprofile = SocialProfile.objects.create(user=user)
    return sprofile

def get_social_profile(request):
    """ Returns the social profile of the user """
    if request.user.is_authenticated:
        sprofile = get_social_profile_byuser(request.user) 
        if not sprofile.ip:
            sprofile.ip = (request.META.get('HTTP_X_FORWARDED_FOR', None)
                           or request.META.get('REMOTE_ADDR', None))
            sprofile.save()
        return sprofile
    return None

def execute_string(function_string, *args, **kwargs):
    """ executes a function given it name as a string """
    mod_name, func_name = function_string.rsplit('.',1)
    mod = import_module(mod_name)
    func = getattr(mod, func_name)
    result = func(*args, **kwargs)
    return result

    

