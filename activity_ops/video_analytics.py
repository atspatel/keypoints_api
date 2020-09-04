from activity_ops.models import ActivityOps, SessionDuration
from datetime import datetime
import pytz

import numpy as np
import pandas as pd
from datetime import datetime
import json


video_exclude = ['oximeter', 'realme_demo',
                 'dhoni_tribute_001', 'hotstart', 'shayari_video_001']


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)


def get_data():
    tz = pytz.timezone("Asia/Kolkata")
    start_date = tz.localize(datetime(2020, 8, 22, 12, 00))

    video_ids = ActivityOps.objects.values_list(
        'video_id', flat=True).distinct()

    output = []
    video_cols = ['video_id', 'button_id', 'load', 'click/play',
                  '#sessions', '#nonzero', 'min', '10', '20', '50', '80', '90', 'max',
                  'average', 'average_nz', 'average_10_90', 'array_20_80', 'average_1', 'average_nz_1']

    for video_id in video_ids:
        if video_id in video_exclude:
            continue
        buttons_out = []
        video_out = {}

        video_load = ActivityOps.objects.filter(
            video_id=video_id, activity="load", creation_date__gte=start_date).count()
        video_play = ActivityOps.objects.filter(
            video_id=video_id, activity="play", creation_date__gte=start_date).count()

        video_out = {'video_id': video_id,
                     'load': video_load, 'click/play': video_play}
        button_list = ActivityOps.objects.filter(
            video_id=video_id, activity="click").values_list('button_id', flat=True).distinct()
        for button in button_list:
            button_count = ActivityOps.objects.filter(
                video_id=video_id, activity="click", button_id=button, creation_date__gte=start_date).count()
            buttons_out.append(
                {'video_id': video_id, 'button_id': button, 'click/play': button_count})
        video_sessions = SessionDuration.objects.filter(
            video_id=video_id).values_list("duration", flat=True)
        np_sessions = np.sort(np.array(video_sessions))
        n = len(np_sessions)
        if n > 0:
            nz_count = np.count_nonzero(np_sessions)
            array_10_90 = np_sessions[int(0.1*n): int(0.9*n)]
            array_20_80 = np_sessions[int(0.2*n): int(0.8*n)]

            video_out["#sessions"] = n
            video_out['#nonzero'] = nz_count
            video_out['min'] = np.round(np.min(np_sessions), 2)
            video_out["10"] = np.round(np.percentile(np_sessions, 10), 2)
            video_out["20"] = np.round(np.percentile(np_sessions, 20), 2)
            video_out["50"] = np.round(np.percentile(np_sessions, 50), 2)
            video_out["80"] = np.round(np.percentile(np_sessions, 80), 2)
            video_out["90"] = np.round(np.percentile(np_sessions, 90), 2)
            video_out['max'] = np.round(np.max(np_sessions), 2)
            video_out["average"] = np.round(np.average(np_sessions), 2)
            video_out["average_nz"] = np.round(np.sum(
                np_sessions)/nz_count if nz_count else 0, 2)
            video_out["average_10_90"] = np.round(np.average(
                array_10_90), 2) if np.count_nonzero(array_10_90) else 0
            video_out["array_20_80"] = np.round(np.average(
                array_10_90), 2) if np.count_nonzero(array_20_80) else 0

        video_sessions = SessionDuration.objects.filter(
            video_id=video_id).values_list("duration_1", flat=True)
        np_sessions = np.sort(np.array(video_sessions))
        n = len(np_sessions)
        if n > 0:
            nz_count = np.count_nonzero(np_sessions)
            video_out["average_1"] = np.round(np.average(np_sessions), 2)
            video_out["average_nz_1"] = np.round(np.sum(
                np_sessions)/nz_count if nz_count else 0, 2)
        # video_out["buttons"] = buttons_out
        out = []
        for k in video_cols:
            out.append(video_out.get(k, ''))
        output.append(out)

        for button in buttons_out:
            out = []
            for k in video_cols:
                out.append(button.get(k, ''))
            output.append(out)
    return json.dumps(output, cls=NpEncoder)
