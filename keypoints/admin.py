from django.contrib import admin
from django.apps import apps

from .views import VideoPost

# Register your models here.


class VideoPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'creator', 'title',
                    'creation_date', 'update_date']


admin.site.register(VideoPost, VideoPostAdmin)

app = apps.get_app_config('keypoints')
for model_name, model in app.models.items():
    if model_name not in ["VideoPost".lower()]:
        admin.site.register(model)
