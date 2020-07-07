from django.urls import path
from .views import VideoPost, AdminCreatorView

urlpatterns = [
    # GET
    path('creator/', AdminCreatorView.as_view(), name="get_creator"),

    # POST
    path('video_post/', VideoPost.as_view(), name="post_vide"),
]
