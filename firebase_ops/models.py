from django.db import models

from accounts.models import AnnonymousUserTable
# Create your models here.

class FcmTokenData(models.Model):
    fcm_token = models.CharField(max_length=255, unique=True)
    ann_token = models.ForeignKey(AnnonymousUserTable, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
