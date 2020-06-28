from .views import FcmTokenView

from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    ## POST
    path('post_fcm_token/', FcmTokenView.as_view(), name="post_fcm_token"),
    ## PUT
]
