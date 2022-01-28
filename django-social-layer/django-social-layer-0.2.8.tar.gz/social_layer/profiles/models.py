
#import uuid
from django.db import models
from django.utils import timezone
from django.urls import reverse
from social_layer.mediautils.models import Media

# Create your models here.
class SocialProfile(models.Model):
    """ the Social media Profile object for the user to show online """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    nick = models.CharField(max_length=64, null=True, blank=True)
    phrase = models.CharField(max_length=256, null=True, blank=True)

    date_time = models.DateTimeField(default=timezone.localtime)
    last_actv = models.DateTimeField(default=timezone.localtime)
    ip = models.CharField(max_length=46, null=True, blank=True)

    comment_section = models.OneToOneField('social_layer.CommentSection',
                                           related_name='sprofile_comment_section',
                                           on_delete=models.SET_NULL,
                                           null=True, blank=True)
    _cached_profoto = None

    def save(self, *args, **kwargs):
        """ the save takes care of setting up a nickname and fix string sizes
        """
        if not self.nick:
            if '@' in self.user.username:
                self.nick = self.user.username.split('@')[0]
            else:
                self.nick = self.user.username
        if self.nick:
            self.nick = self.nick[0:64]
        if self.phrase:
            self.phrase = self.phrase[0:256]
        super(SocialProfile, self).save(*args, **kwargs)

    def picture(self):
        """ return the profile thumbnail """
        if self._cached_profoto is None:
            self._cached_profoto = SocialProfilePhoto.objects.filter(
                                                    profile=self).last()
        return self._cached_profoto

    def get_url(self):
        """ get the url to the profilepage """
        return reverse('social_layer:view_profile', kwargs={'pk':self.pk})
    
class SocialProfilePhoto(Media):
    """ picture used by the SocialProfile.picture
    """
    profile = models.ForeignKey(SocialProfile, on_delete=models.CASCADE)

