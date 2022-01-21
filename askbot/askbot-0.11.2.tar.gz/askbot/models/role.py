"""Role will be the record of per-user roles/permission
assignments. Currently roles are coupled
with the reputation system, but should be separated."""
from django.db import models
from django.contrib.auth.models import User

#todo: migrate here all permissions defined
#by user's status, reputation,
#methods User.assert_can... , etc.
#after that retire field User.status, except
#perhaps status == 'suspended' and 'blocked'
ROLE_CHOICES = (
    ('recv_feedback', 'Receive user\'s feedback email'), #mod
    ('recv_mod_alerts', 'Receive moderation alert emails'), #mod
    ('terminate_accounts', 'Terminate user accounts'), #admin
    ('download_user_data', 'Download user data') #admin
)

MOD_ROLES = set(('recv_feedback', 'recv_mod_alerts'))
ADMIN_ROLES = MOD_ROLES | set(('terminate_accounts', 'download_user_data'))


def get_role_set(status):
    """Returns role set corresponding to the user status"""
    if status == 'administrator':
        return ADMIN_ROLES
    elif status == 'moderator':
        return MOD_ROLES
    else:
        raise ValueError('unsupported status {}'.format(status))


class Role(models.Model):
    """Assigns permissions to users."""
    user = models.ForeignKey(User, related_name='askbot_roles', on_delete=models.CASCADE)
    role = models.CharField(max_length=64, choices=ROLE_CHOICES)

    class Meta: #pylint: disable=missing-docstring, old-style-class, no-init, too-few-public-methods
        app_label = 'askbot'
        db_table = 'askbot_role'
        unique_together = ('user', 'role')
