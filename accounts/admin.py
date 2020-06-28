from django.contrib import admin
from django.apps import apps

# Register your models here
from .models import User, AnnonymousUserTable


class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone', 'first_name',
                    'last_name', 'is_admin', "time_created"]


admin.site.register(User, UserAdmin)


class AnnonymousUserTableAdmin(admin.ModelAdmin):
    list_display = ['id', 'creation_date']


admin.site.register(AnnonymousUserTable, AnnonymousUserTableAdmin)


app = apps.get_app_config('accounts')
for model_name, model in app.models.items():
    if model_name not in ["user", "AnnonymousUserTable".lower()]:
        admin.site.register(model)
