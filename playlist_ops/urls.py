from django.urls import path
from .views import PlaylistView
urlpatterns = [
    # GET
    path('playlist/', PlaylistView.as_view(), name="get_playlist"),

    # # POST
    # path('post_media/', MediaInfoView.as_view(), name="create_media"),
    # # PUT
]
