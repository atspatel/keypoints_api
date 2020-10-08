from rest_framework import serializers
from django.conf import settings
from django.db.models import Sum

from .models import LilyCharacters, QuizInfo, QuizActivity, QuizCharacterVoteCount
from .models import Episode


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ('ep', 'thumbnail')


class LilyCharactersSerializer(serializers.ModelSerializer):
    vote = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LilyCharacters
        fields = ('id', 'name', 'thumbnail', 'color', 'vote')

    def get_vote(self, obj):
        quiz = self.context.get('quiz', None)
        if quiz:
            count_obj = QuizCharacterVoteCount.objects.filter(
                quiz=quiz, character=obj).first()
            total_votes = QuizCharacterVoteCount.objects.filter(
                quiz=quiz, character__isnull=False).aggregate(Sum('number'))['number__sum']

            if count_obj:
                return int(count_obj.number*100/total_votes) if total_votes > 0 else int(100/6)
        return 0


class QuizInfoSerializer(serializers.ModelSerializer):
    characters = serializers.SerializerMethodField(read_only=True)
    episode = serializers.SerializerMethodField(read_only=True)
    question = serializers.SerializerMethodField(read_only=True)
    selected = serializers.SerializerMethodField(read_only=True)
    next_ep = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuizInfo
        fields = ('id', 'quiz_type', 'episode', 'start_time',
                  'end_time', 'question', 'selected', 'isTimer', 'credit_video', 'characters', 'next_ep')

    def get_characters(self, obj):
        characters = LilyCharacters.objects.all()
        return LilyCharactersSerializer(characters, context={"quiz": obj}, many=True).data

    def get_episode(self, obj):
        return obj.ep.ep if obj.ep else None

    def get_question(self, obj):
        return {"part1": obj.question_part1, "part2": obj.question_part2}

    def get_selected(self, obj):
        session = self.context.get('session', None)
        if session:
            activity_obj = QuizActivity.objects.filter(
                session=session).order_by('-creation_date').first()
            if activity_obj and activity_obj.answer:
                return LilyCharactersSerializer(activity_obj.answer).data
        return None

    def get_next_ep(self, obj):
        if obj.ep and obj.quiz_type == 'credit':
            next_ep = obj.ep.ep + 1
            episode_obj = Episode.objects.filter(ep=next_ep).first()
            if episode_obj:
                return EpisodeSerializer(episode_obj).data
        return None
