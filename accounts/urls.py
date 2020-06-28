from django.urls import path

from .views import LogIn, LogOut
from .views import OTPRegisterOps
from .views import UserBioView

urlpatterns = [
    # GET
    path('get_otp/<phone_number>', OTPRegisterOps.as_view(), name="get_otp"),
    path('annonymous_login', LogIn.as_view(), name="annonymous_login"),
    path('logout', LogOut.as_view(), name="logout"),

    # POST
    path('post_bio/', UserBioView.as_view(), name="post_bio"),
    path('login/', LogIn.as_view(), name="login"),
]
