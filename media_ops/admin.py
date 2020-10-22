from django.contrib import admin
from django.apps import apps

from .models import ImagesUrl


class ImagesUrlAdmin(admin.ModelAdmin):
    list_display = ['id', 'image_url', 'creation_date']


admin.site.register(ImagesUrl, ImagesUrlAdmin)

app = apps.get_app_config('media_ops')
for model_name, model in app.models.items():
    if model_name != "ImagesUrl".lower():
        admin.site.register(model)
