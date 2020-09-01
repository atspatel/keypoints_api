"""keypoints_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path('admin_ops/', include('admin_ops.urls')),
    re_path('accounts/', include('accounts.urls')),
    re_path('firebase_ops/', include('firebase_ops.urls')),
    re_path('tags_ops/', include('tags_models.urls')),
    re_path('keypoints/', include('keypoints.urls')),
    re_path('keypoints_account/', include('keypoints_account.urls')),
    re_path('activity_ops/', include('activity_ops.urls')),
    re_path('excercise_ops/', include('excercise_ops.urls')),
    re_path('playlist_ops/', include('playlist_ops.urls')),
]
