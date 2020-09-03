from django.contrib import admin
from .models import ActivityOps, SessionDuration


class ActivityOpsAdmin(admin.ModelAdmin):
    list_display = ['activity', 'video_id',
                    'button_id', 'session_id', 'creation_date']


admin.site.register(ActivityOps, ActivityOpsAdmin)


class SessionDurationAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'video_id',
                    'duration', 'duration_1', 'creation_date']


admin.site.register(SessionDuration, SessionDurationAdmin)
