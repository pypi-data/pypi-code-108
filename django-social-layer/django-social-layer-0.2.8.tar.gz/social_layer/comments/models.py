#from django.db import models
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from social_layer.models import Like, LikableObject

### Comments
class CommentSection(LikableObject):
    """ A comment section can be added to any page.
    It optionally is tied to a url. But also can be refered by its id.
    the owner is also optional. If is not None, the owner will get a
    notification when someone makes a new comment.
    """
    url = models.TextField(null=True, blank=True)
    owner = models.ForeignKey('social_layer.SocialProfile',
                              related_name='comment_section_owner',
                              null=True, blank=True,
                              on_delete=models.CASCADE)
   
    comments_enabled = models.BooleanField(default=True)
    owner_can_delete = models.BooleanField(default=False)
    anyone_can_reply = models.BooleanField(default=True)
    is_flat = models.BooleanField(default=True)

    cached_featured = models.TextField(blank=True, default="")
    # in case of featured = True, it will show limited comments
    featured = False
    _cached_comment_list = None
    max_comments = getattr(settings, 'SOCIAL_MAX_FEATURED_COMMENTS', 3)
    
    def get_url(self):
        """ return the parent url of the comment or the default view """
        if self.url:
            return self.url
        else:
            return reverse('social_layer:comment_section',
                           kwargs={'pk':self.pk})

    def get_comments(self):
        """ return comments from this comment section
        You can limit the amount of comments with the 'featured' flag.
        If True, only a number of MAX_FEATURED_COMMENTS (defaults to 3) will be
        rendered on screen.
        """
        if self._cached_comment_list is None:
            self._cached_comment_list = Comment.objects.filter(
                                                comment_section=self,
                                                reply_to=None)
        if self.featured:
            return self._cached_comment_list[0:self.max_comments]
        else:
            return self._cached_comment_list

    def get_featured_comments(self):
        """ get a limited number of comments, defined by MAX_FEATURED_COMMENTS
        """
        max_comm = getattr(settings, 'SOCIAL_MAX_FEATURED_COMMENTS', 3)
        return self.get_comments()[0:max_comm]

    def updt_counters(self):
        """ Updates the counting """
        self.count_likes = LikePost.objects.filter(comment_section=self,
                                                   like=True).count()
        self.count_dislikes = LikePost.objects.filter(comment_section=self,
                                                      like=False).count()
        self.count_replies = Comment.objects.filter(comment_section=self).count()
        self.save()


class Comment(LikableObject):
    """ the Comment object """
    comment_section = models.ForeignKey('social_layer.CommentSection',
                                        related_name='comment_section',
                                        on_delete=models.CASCADE)
    author = models.ForeignKey('social_layer.SocialProfile',
                               related_name='comment_author',
                               on_delete=models.CASCADE)
    text = models.TextField()
    date_time = models.DateTimeField(default=timezone.localtime)
    reply_to = models.ForeignKey('social_layer.Comment',
                                related_name='comment_reply_to',
                                on_delete=models.CASCADE,
                                null=True, blank=True)

    class Meta():    
        ordering = ['-date_time']

    def save(self, *args, **kwargs):
        """ the save method prevents repeated comments and crops the text.
        """
        if self.text:
            self.text = self.text.replace('\n', ' ')[0:512]
            other = Comment.objects.exclude(pk=self.pk
                                  ).filter(author=self.author,
                                           text=self.text,
                                           comment_section=self.comment_section,
                                           reply_to=self.reply_to)
            if not other.exists():
                super(Comment, self).save(*args, **kwargs)
                self.comment_section.updt_counters()

    def get_replies(self):
        """ Return all the replies to this comment """
        if not hasattr(self, 'cached_get_replies'):
            replies = Comment.objects.filter(comment_section=self.comment_section,
                                             reply_to=self)
            self.cached_get_replies = replies
        return self.cached_get_replies

    def updt_counters(self):
        """ Updates the counting """
        self.count_likes = LikeComment.objects.filter(comment=self,
                                                      like=True).count()
        self.count_dislikes = LikeComment.objects.filter(comment=self,
                                                         like=False).count()
        self.count_replies = Comment.objects.filter(reply_to=self).count()
        self.save()


class LikeComment(Like):
    """ a Like for a Comment """
    comment = models.ForeignKey('social_layer.Comment', 
                                related_name='like_comment',
                                on_delete=models.CASCADE)

class LikePost(Like):
    """ a Like for a CommentSection """
    comment_section = models.ForeignKey('social_layer.CommentSection', 
                                        related_name='like_commentsection',
                                        on_delete=models.CASCADE)
