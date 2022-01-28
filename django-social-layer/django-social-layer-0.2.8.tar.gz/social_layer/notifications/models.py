from django.db import models
from django.utils import timezone
# Create your models here.
class Notification(models.Model):
    """ Notification object, people get notified of social interactions """
    to = models.ForeignKey('auth.User',
                           related_name='notification_to',
                           on_delete=models.CASCADE)
    text = models.TextField()
    date_time = models.DateTimeField(default=timezone.localtime)
    read = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        other = Notification.objects.exclude(pk=self.pk
                                ).filter(to=self.to,
                                        text=self.text,
                                        date_time__date=self.date_time.date())
        if not other.exists():
            super(Notification, self).save(*args, **kwargs)
