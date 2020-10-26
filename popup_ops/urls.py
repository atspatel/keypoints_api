from django.urls import path
from .views import MediaView, AspectRatioView, PopupView, KpMediaVideoView
urlpatterns = [
    # GET
    path('media/', MediaView.as_view(), name="get_media"),

    # # POST
    path('video/', KpMediaVideoView.as_view(), name="get_post_video"),

    path('aspect_ratio', AspectRatioView.as_view(), name="get_aspect_ratio"),
    path('popup/', PopupView.as_view(), name="get_create_popup"),

    # path('post_media/', MediaInfoView.as_view(), name="create_media"),
    # # PUT
]
