from django.urls import path
from django.conf.urls import url, include

from .views import PlaylistView, ExcerciseView

urlpatterns = [
    path('create_playlist/', PlaylistView.as_view(), name="create_playlist"),
    path('get_data/', ExcerciseView.as_view(), name="get_exc_data")]
