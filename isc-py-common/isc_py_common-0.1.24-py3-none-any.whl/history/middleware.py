import logging
import traceback
from datetime import timedelta

from django.db import transaction
from django.db.utils import DatabaseError, IntegrityError
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

from history import utils
from history.models.visitor import Visitor
from history.utils import get_ip

logger = logging.getLogger(__name__)


class VisitorTrackingMiddleware(MiddlewareMixin):
    """
    Keeps track of your active users.  Anytime a visitor accesses a valid URL,
    their unique record will be updated with the page they're on and the last
    time they requested a page.

    Records are considered to be unique when the session key and IP address
    are unique together.  Sometimes the same user used to have two different
    records, so I added a check to see if the session key had changed for the
    same IP and user agent in the last 5 minutes
    """

    def process_request(self, request):
        # create some useful variables
        ip_address = get_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT')

        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        username = request.session.get('username')

        # if we get here, the URL needs to be tracked
        # determine what time it is
        now = timezone.now()

        attrs = {
            'username': username,
            'ip_address': ip_address,
        }

        # for some reason, Visitor.objects.get_or_create was not working here
        try:
            visitor = Visitor.objects.using('history').get(**attrs)
        except Visitor.DoesNotExist:
            # see if there's a visitor with the same IP and user agent
            # within the last 5 minutes
            cutoff = now - timedelta(minutes=5)
            visitors = Visitor.objects.using('history').filter(
                ip_address=ip_address,
                user_agent=user_agent,
                last_update__gte=cutoff
            )

            if len(visitors):
                visitor = visitors[0]
                visitor.session_key = session_key
                logger.debug('Using existing visitor for IP %s / UA %s: %s' % (ip_address, user_agent, visitor.id))
            else:
                visitor, created = Visitor.objects.using('history').get_or_create(**attrs)
                if created:
                    logger.debug('Created a new visitor: %s' % attrs)
        except:
            return

        # update the tracking information
        visitor.session_key = session_key
        visitor.user_agent = user_agent

        # if the visitor record is new, or the visitor hasn't been here for
        # at least an hour, update their referrer URL
        one_hour_ago = now - timedelta(hours=1)
        if not visitor.last_update or visitor.last_update <= one_hour_ago:
            visitor.referrer = request.META.get('HTTP_REFERER', 'unknown')
            visitor.session_start = now

        visitor.url = request.path
        visitor.last_update = now
        try:
            sid = transaction.savepoint()
            visitor.save()
            transaction.savepoint_commit(sid)
        except IntegrityError:
            transaction.savepoint_rollback(sid)
        except DatabaseError:
            logger.error('There was a problem saving visitor information:\n%s\n\n%s' % (traceback.format_exc(), locals()))


class VisitorCleanUpMiddleware(MiddlewareMixin):
    """Clean up old visitor tracking records in the database"""

    def process_request(self, request):
        timeout = utils.get_cleanup_timeout()

        if str(timeout).isdigit():
            logger.debug('Cleaning up visitors older than %s hours' % timeout)
            timeout = timezone.localtime(timezone.now()) - timedelta(hours=int(timeout))
            Visitor.objects.using('history').filter(last_update__lte=timeout).delete()
