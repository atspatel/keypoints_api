from .views import VideoPostView, VideoUploadView
from .views import VideoLikeView, VideoReshareView, ThumbnailView
from .views import CategoryView, TopicView, HashtagView, OptionsView

from django.urls import path
from django.conf.urls import url, include

urlpatterns = [
    # get
    path('video_feed/<post_id>/',
         VideoPostView.as_view(), name="get_video_feed"),

    # post
    path('video_feed/',
         VideoPostView.as_view(), name="get_video_feed"),
    path('upload_video/',
         VideoUploadView.as_view(), name="upload_video_post"),
    path('upload_thumbnail/',
         ThumbnailView.as_view(), name="upload_thumbnail"),

    path('post_like/',
         VideoLikeView.as_view(), name="get_video_feed"),
    path('post_reshare/',
         VideoReshareView.as_view(), name="upload_video_post"),


    path('category/',
         CategoryView.as_view(), name="get_category"),
    path('category/<suggestion_text>/',
         CategoryView.as_view(), name="get_category"),
    path('topic/',
         TopicView.as_view(), name="get_topic"),
    path('topic/<suggestion_text>/',
         TopicView.as_view(), name="get_topic"),
    path('hashtag/<suggestion_text>/',
         HashtagView.as_view(), name="get_hashtag"),
    path('get_options/', OptionsView.as_view(), name='get_options'),
]
