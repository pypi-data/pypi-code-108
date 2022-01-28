from django.db import models
from django.utils import timezone
from django.urls import reverse
from social_layer.mediautils.models import Media
from social_layer.comments.models import CommentSection

class Post(models.Model):
    """ a Post is the class that defines a User Generated Content.
    Talking about social media websites, a post usually consist of:
        selfies, cat photos, gym session photos, photos os dishes, etc.
    """
    text = models.TextField(null=True, blank=True)
    date_time = models.DateTimeField(default=timezone.localtime)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
    owner = models.ForeignKey('social_layer.SocialProfile',
                              related_name='post_commentsection_owner',
                              on_delete=models.CASCADE)
    comments = models.ForeignKey('social_layer.CommentSection',
                                 related_name='post_commentsection',
                                 on_delete=models.CASCADE)
    # cached values
    _cached_get_url = None

    def save(self, *args, **kwargs):
        """ before saving: - set up a commentsection object. """
        if self.comments_id is None:
            self.comments = CommentSection.objects.create(owner=self.owner)
        super(Post, self).save(*args, **kwargs)
        if self.comments.get_url() != self.get_url():
            self.comments.url = self.get_url()
            self.comments.save()

    def get_url(self):
        """ get the url of this post """
        if self._cached_get_url is None:
            self._cached_get_url = reverse('social_layer:view_post',
                                           kwargs={'pk': self.pk})
        return self._cached_get_url

class PostMedia(Media):
    """ PostMedia holds the file associated with a POST.
    This is where cat pictures and gym photos will be stored.
    """
    post = models.OneToOneField('social_layer.Post', on_delete=models.CASCADE)

