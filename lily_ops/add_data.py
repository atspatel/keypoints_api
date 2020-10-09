import json

from constants import storage_dir
from lily_ops.models import Episode, LilyCharacters, QuizInfo

episode_json = "./z_data/episode.json"
character_json = "./z_data/characters.json"
quiz_json = "./z_data/quiz_info.json"

episode_data = json.load(open(episode_json, 'r'))
data = episode_data.get('data', [])
for episode in data:
    ep = episode['ep']
    video_url = os.path.join(storage_dir, episode['video_url'])
    thumbnail = os.path.join(storage_dir, episode['thumbnail'])

    episode_obj, _ = Episode.objects.update_or_create(
        ep=ep, defaults={'video_url': video_url, 'thumbnail': thumbnail})
    print('episode', episode_obj.id)


character_data = json.load(open(character_json, 'r'))
data = character_data.get('data', [])

for character in data:
    order = character['order']
    name = character['name']
    thumbnail = os.path.join(storage_dir, character['thumbnail'])
    color = character['color']

    character_obj, _ = LilyCharacters.objects.update_or_create(
        name=name, defaults={"order": order, "thumbnail": thumbnail, "color": color})
    print('character', character_obj.id)


quiz_data = json.load(open(quiz_json, 'r'))
data = quiz_data.get('data', [])
for quiz in data:
    name = quiz['name']
    quiz_type = quiz['quiz_type']
    episode = quiz['episode']
    start_time = quiz['start_time']
    end_time = quiz['end_time']
    question_part1 = quiz['question_part1']
    question_part2 = quiz['question_part2']
    isTimer = quiz['isTimer']
    credit_video = os.path.join(
        storage_dir, quiz['credit_video']) if quiz['credit_video'] else None
    hint_video = os.path.join(
        storage_dir, quiz['hint_video']) if quiz['hint_video'] else None
    next_quiz = quiz['next_quiz']

    episode_obj = Episode.objects.filter(ep=episode).first()
    print(episode_obj)
    quiz_obj, _ = QuizInfo.objects.update_or_create(
        name=name, defaults={
            "quiz_type": quiz_type,
            "ep": episode_obj,
            "start_time": start_time,
            "end_time": end_time,
            "question_part1": question_part1,
            "question_part2": question_part2,
            "isTimer": isTimer,
            "credit_video": credit_video,
            "hint_video": hint_video})
    print('quiz', quiz_obj.id)
