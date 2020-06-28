from .views import LanguageView
from django.urls import path
from django.conf.urls import url, include


urlpatterns = [
    path('get_languages/', LanguageView.as_view(), name="get_stories"),
]
