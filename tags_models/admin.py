from django.contrib import admin
from django.apps import apps

app = apps.get_app_config('tags_models')
for model_name, model in app.models.items():
    admin.site.register(model)