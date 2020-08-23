from django.db import models
from django.utils import timezone
import uuid
# Create your models here.


class AbstractTimeClass(models.Model):
    creation_date = models.DateTimeField(default=timezone.now, blank=True)
    creation_date.editable = True
    update_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActivityOps(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    activity = models.CharField(max_length=255)
    video_id = models.CharField(max_length=255, null=True, blank=True)
    button_id = models.CharField(max_length=255, null=True, blank=True)
    session_id = models.UUIDField(null=True, blank=True, editable=False)


class SessionDuration(AbstractTimeClass):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_id = models.UUIDField(unique=True)
    video_id = models.CharField(max_length=255, null=True, blank=True)
    duration = models.FloatField(default=0.0)
