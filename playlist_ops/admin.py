from django.contrib import admin
from django.apps import apps

from .models import PlaylistInfo


class PlaylistInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


admin.site.register(PlaylistInfo, PlaylistInfoAdmin)

app = apps.get_app_config('playlist_ops')
for model_name, model in app.models.items():
    if model_name not in ["PlaylistInfo".lower()]:
        admin.site.register(model)
