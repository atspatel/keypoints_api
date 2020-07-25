from django.contrib import admin
from .models import ActivityOps


class ActivityOpsAdmin(admin.ModelAdmin):
    list_display = ['activity', 'video_id', 'button_id', 'creation_date']


admin.site.register(ActivityOps, ActivityOpsAdmin)
