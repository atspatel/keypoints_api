from .views import ActivityView

from django.urls import path
urlpatterns = [
    # POST
    path('post_activity/', ActivityView.as_view(), name="post_activity"),
    # PUT
]
