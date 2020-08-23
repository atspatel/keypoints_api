from .views import ActivityView, VideoPlaylistTimeView

from django.urls import path
urlpatterns = [
    # POST
    path('post_activity/', ActivityView.as_view(), name="post_activity"),
    path('post_duration/', VideoPlaylistTimeView.as_view(), name="post_duration"),
    # PUT
]
