from django.urls import path
from .views import MediaView, AspectRatioView, PopupView
urlpatterns = [
    # GET
    path('media/', MediaView.as_view(), name="get_media"),

    path('aspect_ratio', AspectRatioView.as_view(), name="get_aspect_ratio"),
    path('popup/', PopupView.as_view(), name="get_create_popup"),
    # # POST
    # path('post_media/', MediaInfoView.as_view(), name="create_media"),
    # # PUT
]
