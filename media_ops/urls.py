from django.urls import path
from .views import ImageView
urlpatterns = [
    # POST
    path('image/', ImageView.as_view(), name="Upload Image")
]
