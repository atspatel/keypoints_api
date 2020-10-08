from django.urls import path
from .views import QuizView, QuizActivityView
urlpatterns = [
    # GET
    path('quiz/', QuizView.as_view(), name="get_quiz_data"),


    path('post_answer/', QuizActivityView.as_view(), name="post_answer"),
]
