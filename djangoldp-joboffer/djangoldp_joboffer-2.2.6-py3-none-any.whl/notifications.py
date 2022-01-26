from django.conf import settings
from djangoldp.models import Model
from djangoldp_skill.models import Skill
from djangoldp_joboffer.models import JobOffer
import logging


logger = logging.getLogger('djangoldp')


def filter_joboffer_notification_recipient_has_skill(recipient, notification):
    '''
    returns True if the recipient user has a skill which is attached to the job-offer,
    False otherwise
    '''
    try:
        # we are only interested in filtering notifications about JobOffers
        if '@type' not in notification['object'] or notification['object']['@type'] != Model.get_meta(JobOffer, 'rdf_type', 'hd:joboffer'):
            return True

        # handling some strange (PyLD?) behaviour where a list with a single element is truncated into just that element
        post_skills = notification['object']['skills']['ldp:contains'].split(',')
        job_skills = Skill.objects.filter(urlid__in=post_skills)

        # if there is an intersection between the set of job offer skills and user skills
        # it means that there is at least one skill in the job offer which matches user skills
        if (job_skills.intersection(recipient.skills.all()).count() > 0):
            return True

        return False

    except AttributeError as e:
        print('ERROR: ' + str(e))
        logger.error('AttributeError filtering notification for skill ' + str(e) + ' , did not send notification ' + str(notification))
        return False
    except KeyError as e:
        print('ERROR: ' + str(e))
        logger.error('KeyError filtering notification for skill ' + str(e) + ' , did not pass skills ' + str(notification))
        return False
    except JobOffer.DoesNotExist as e:
        print('ERROR: ' + str(e))
        logger.error('The JobOffer ' + str(notification['object']) + ' did not exist on this server, did not send notification ' + str(notification))
        return False
