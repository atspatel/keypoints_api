from django.contrib import admin
from django.apps import apps

from .models import PopupCarouselMapping

app = apps.get_app_config('popup_ops')


class PopupCarouselMappingAdmin(admin.ModelAdmin):
    list_display = ['id', 'creation_date']


admin.site.register(PopupCarouselMapping, PopupCarouselMappingAdmin)

for model_name, model in app.models.items():
    if model_name != "PopupCarouselMapping".lower():
        admin.site.register(model)
