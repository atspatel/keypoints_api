from .views import ActivityView, VideoPlaylistTimeView

from django.urls import path
urlpatterns = [
    # POST
    path('post_activity/', ActivityView.as_view(), name="post_activity"),
    path('get_analytics',
         VideoPlaylistTimeView.as_view(), name="get_analytics"),
    path('post_duration/', VideoPlaylistTimeView.as_view(), name="post_duration"),
    # PUT
]
