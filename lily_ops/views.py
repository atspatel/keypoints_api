from rest_framework.views import APIView
from rest_framework.response import Response

from .models import QuizInfo, LilyCharacters, QuizActivity, QuizCharacterVoteCount
from .serializers import QuizInfoSerializer
import logging
import uuid


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class QuizView(APIView):
    def get(self, request):
        quiz_id = request.GET.get('quiz_id', None)
        session = request.GET.get('session', None)
        if quiz_id:
            quiz_obj = QuizInfo.objects.filter(name=quiz_id).first()
            return Response({'data': QuizInfoSerializer(quiz_obj, context={'session': session}).data, 'status': True})
        return Response({'status': False, "data": {}})


class QuizActivityView(APIView):
    def post(self, request):
        session_id = request.data.get('session', None)
        quiz = request.data.get('quiz', None)
        answer = request.data.get('answer', None)

        if session_id:
            quiz_obj = QuizInfo.objects.filter(id=quiz).first()
            character_obj = LilyCharacters.objects.filter(id=answer).first()

            activity_obj = QuizActivity.objects.create(
                session=session_id, quiz=quiz_obj, answer=character_obj)
            count_obj, _ = QuizCharacterVoteCount.objects.get_or_create(
                quiz=quiz_obj, character=character_obj)
            count_obj.number = count_obj.number + 1
            count_obj.save()

            return Response({'status': True, "id": activity_obj.id})
        return Response({'status': False})
