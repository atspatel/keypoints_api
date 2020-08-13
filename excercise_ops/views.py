from rest_framework.views import APIView
from rest_framework.response import Response
import json

from .workout_constants import excercise_list, excercise_data


class PlaylistView(APIView):
    def get(self, request):
        return Response({'status': True})

    def post(self, request):
        t_dur = 10
        workout = json.loads(request.data.get(
            'workout', json.dumps([])))
        playlist = "#EXTM3U\n#EXT-X-MEDIA-SEQUENCE:0\n#EXT-X-TARGETDURATION:%d" % (
            t_dur)
        for group in workout:
            group_playlist = ""
            for activity in group.get('activity', []):
                activity_data = excercise_data[activity['w_id']]
                start = activity_data.get('start', {}).get('playlist', '')
                offset = activity_data.get('start', {}).get(
                    'time', 0) - activity_data.get('start', {}).get('offset', 0)

                end = activity_data.get('end', {}).get('playlist', '')
                offset = activity_data.get('end', {}).get(
                    'time', 0) - activity_data.get('end', {}).get('offset', 0)

                rep_count = max(
                    round((activity['time'] - offset) /
                          activity_data['rep']['time']),
                    1
                )

                rep_playlist = activity_data.get('rep', {}).get('playlist', '')
                rep = "\n".join([rep_playlist for i in range(rep_count)])

                group_playlist = "%s\n%s\n%s\n%s" % (
                    group_playlist, start, rep, end)
            rounds = group.get('rep', 1)
            playlist = "%s\n%s" % (playlist, "\n".join(
                [group_playlist for i in range(rounds)]))
        playlist = "%s\n#EXT-X-ENDLIST" % (playlist)
        return Response({'status': True, "playlist": playlist})


class ExcerciseView(APIView):
    def modify_value(self, v):
        return {
            "name": v.get('name', ''),
            "thumbnail": v.get('thumbnail', ''),
            "file": v.get('rep', {}).get('file', ''),
            "offset": v.get('offset', ''),
            "start_offset": v.get('start', {}).get('offset', 0)
        }

    def get(self, request):
        data = {k: self.modify_value(v) for k, v in excercise_data.items()}
        return Response({"status": True, "exc_data": data, "exc_list": excercise_list})

    def post(self, request):
        return Response({"status": False})
