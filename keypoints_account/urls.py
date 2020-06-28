from django.urls import path
from django.conf.urls import url, include

from .views import CreatorView, FollowView, KeyPointsPreferenceView

urlpatterns = [
    path('creators/', CreatorView.as_view(), name="get_post_creator"),
    path('creators/<suggestion_text>/',
         CreatorView.as_view(), name="get_creator"),

    path('preferences/', KeyPointsPreferenceView.as_view(),
         name='get_post_preferences'),
    path('follow/', FollowView.as_view(), name="get_post_follow"),
]
