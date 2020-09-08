from activity_ops.models import ActivityOps, SessionDuration
from datetime import datetime
import pytz

import numpy as np
import pandas as pd
from datetime import datetime
import json


video_exclude = ['oximeter', 'realme_demo',
                 'dhoni_tribute_001', 'hotstart', 'shayari_video_001',
                 'ravish_kumar', 'kartik_tyagi', 'quiz_video_001']

video_uuid_mapping = {"content_0829_001": "bd5fdb26-c0ec-4b0f-95f7-c4a1812601ae",
                      "content_0829_002": "4353952c-b97e-4b00-afca-6d1f752acab1",
                      "content_0901_001": "24f2559a-f30b-465d-a245-1ec4feea2f7a",
                      "content_0901_002": "4b214172-fde4-4814-bcd9-ee535fb925b0",
                      "content_0901_003": "8296ff95-9d6c-468b-aeb0-72a3cc2e1e64",
                      "content_0901_004": "52abb724-ba38-4df7-afc4-2713380bb909",
                      "content_0901_005": "f6817cfa-1d7d-47a5-9ebd-4834f639282e",
                      "content_0901_006": "10e4d8db-4904-4f37-a3d4-90cfcad93f96",
                      "content_0903_001": "de676416-c40e-4b79-a6c3-3af5310537cd",
                      "content_0903_002": "0874325b-709b-4506-9208-f19139458bdd",
                      "content_0903_003": "9db9b785-341a-4f33-9984-a42adbc4011f",
                      "content_0903_004": "29ed55a5-cc3e-4318-941b-3028dd92e9c6",
                      "content_0903_005": "5f4bfdce-b65c-4628-89f0-f4167bba35a4",
                      "content_0903_006": "4c99944b-1aa0-4e5c-8018-c0b3672374fd",
                      "content_0903_007": "86e62b55-a88d-4bb6-929b-a77d8955cd7c",
                      "content_0905_001": "eaa758f0-1eb8-4e94-ab4b-920ed5eb71b3",
                      "content_0905_002": "0cc7a7fd-b3a6-4121-b66c-69a3d037e73f",
                      "content_0905_003": "00d4db41-0445-460c-bdb0-b47d5aff0e75",
                      "content_0905_004": "25a99b97-9789-48d0-a55d-2f020e0bd24a",
                      "content_0905_005": "3e0a4055-43e2-4c75-ba23-a57ed69803bd",
                      "content_0905_006": "f419b779-1b22-4666-a271-3df9ddff28ca",
                      "content_0905_007": "7611d8db-82bc-4961-8f22-29bd6073ba5e"}
rev_mapping = {v: k for k, v in video_uuid_mapping.items()}


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

    processed_video_ids = []
    for video_id in video_ids:
        if video_id in video_exclude:
            continue
        if video_id in processed_video_ids:
            continue

        video_id_list = [video_id]
        key = video_id
        if video_id in video_uuid_mapping:
            video_id_list = [video_id, video_uuid_mapping[video_id]]
        elif video_id in rev_mapping:
            video_id_list = [video_id, rev_mapping[video_id]]
            key = rev_mapping[video_id]
        processed_video_ids.extend(video_id_list)
        buttons_out = []
        video_out = {}

        video_load = ActivityOps.objects.filter(
            video_id__in=video_id_list, activity="load", creation_date__gte=start_date).count()
        video_play = ActivityOps.objects.filter(
            video_id=video_id, activity="play", creation_date__gte=start_date).count()

        video_out = {'video_id': key,
                     'load': video_load, 'click/play': video_play}
        button_list = ActivityOps.objects.filter(
            video_id=video_id, activity="click").values_list('button_id', flat=True).distinct()
        for button in button_list:
            button_count = ActivityOps.objects.filter(
                video_id=video_id, activity="click", button_id=button, creation_date__gte=start_date).count()
            buttons_out.append(
                {'video_id': key, 'button_id': button, 'click/play': button_count})
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
