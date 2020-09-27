from django.urls import path
from .views import MediaView
urlpatterns = [
    # GET
    path('media/', MediaView.as_view(), name="get_media"),

    # # POST
    # path('post_media/', MediaInfoView.as_view(), name="create_media"),
    # # PUT
]
