from akismet import Akismet, APIKeyError, AkismetError
from askbot.conf import settings as askbot_settings
from askbot import get_version
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str
from askbot.utils.html import site_url
from django.urls import reverse
import logging

def get_user(user, request):
    return user or request.user

def get_user_param(user, param_name):
    """Returns param from the user if user is not anonymous.
    Returns `None` otherwise.
    """
    if user.is_anonymous:
        return None
    return getattr(user, param_name)

def akismet_check_spam(text, request=None, author=None, ip_addr=None, user_agent=None):
    """Returns True if spam found, false if not,
    May raise exceptions if something is not right with
    the Akismet account/service/setup"""
    return call_akismet(text,
                        request=request,
                        author=author,
                        ip_addr=ip_addr,
                        user_agent=user_agent,
                        command='check_spam')

def akismet_submit_spam(text, request=None, author=None, ip_addr=None, user_agent=None):
    """Submits manually marked spam to Akismet"""
    return call_akismet(text,
                        request=request,
                        author=author,
                        ip_addr=ip_addr,
                        user_agent=user_agent,
                        command='submit_spam')

def call_akismet(text, request=None, author=None, ip_addr=None, user_agent=None, command='check_spam'):
    """Calls akismet apy with a command.
    Supports commands 'check_spam', 'submit_spam' and 'submit_ham'
    """
    if not askbot_settings.USE_AKISMET:
        return False
    try:
        if askbot_settings.AKISMET_API_KEY.strip() == "":
            raise ImproperlyConfigured('You have not set AKISMET_API_KEY')

        data = {'comment_content': text}
        user = get_user(author, request)
        username = get_user_param(user, 'username')
        if username:
            data['comment_author'] = smart_str(username)

        email = get_user_param(user, 'email')
        if email:
            data['comment_author_email'] = email

        api = Akismet(key=askbot_settings.AKISMET_API_KEY,
                      blog_url=smart_str(site_url(reverse('questions'))))

        user_ip = ip_addr or request.META.get('REMOTE_ADDR')
        user_agent = user_agent or request.environ['HTTP_USER_AGENT']
        if command == 'check_spam':
            return api.comment_check(user_ip, user_agent, **data)
        elif command == 'submit_spam':
            return api.submit_spam(user_ip, user_agent, **data)
        elif command == 'submit_ham':
            return api.submit_ham(user_ip, user_agent, **data)
        else:
            raise RuntimeError('unknown akismet method: "{}"'.format(command))

        return api.comment_check(user_ip, user_agent, **data)
    except APIKeyError:
        logging.critical('Akismet Key is missing')
    except AkismetError:
        logging.critical('Akismet error: Invalid Akismet key or Akismet account issue!')
    except Exception as e:
        logging.critical(('Akismet error: %s' % str(e)).encode('utf-8'))
    return False
