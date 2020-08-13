BASE_DIR_curefit = "https://storage.googleapis.com/kp_videos/media/curefit"

excercise_list = [
    {"key": "exc_001", "name": "Mountain Climbers"},
    {"key": "exc_002", "name": "Squats"},
    {"key": "exc_003", "name": "Quad Rockers"},
    {"key": "exc_004", "name": "Skipping"},
    {"key": "exc_005", "name": "Squat Knee to Chest"},
    {"key": "exc_006", "name": "Butt Kick"},
    {"key": "exc_007", "name": "Twist"}
]

excercise_data = {
    "exc_001": {
        "name": "Mountain Climbers",
        "thumbnail": "%s/exc_001/thumb_001.png" % (BASE_DIR_curefit),
        "offset": 4,
        "start": {
            "playlist": "#EXTINF:5.600000,\n%s/exc_001/exc_001_sta_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_001/exc_001_sta_720p.m3u8" % (BASE_DIR_curefit),
            "time": 5.6,
            "offset": 2
        },
        "rep": {
            "playlist": "#EXTINF:1.680000,\n%s/exc_001/exc_001_rep_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_001/exc_001_rep_720p.m3u8" % (BASE_DIR_curefit),
            "time": 1.68,
            "offset": 0
        },
        "end": {
            "playlist": "#EXTINF:4.520000,\n%s/exc_001/exc_001_end_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_001/exc_001_end_720p.m3u8" % (BASE_DIR_curefit),
            "time": 4.52,
            "offset": -2
        }
    },
    "exc_002": {
        "name": "Squats",
        "thumbnail": "%s/exc_002/thumb_002.png" % (BASE_DIR_curefit),
        "offset": 0,
        "start": {},
        "rep": {
            "playlist": "#EXTINF:2.520000,\n%s/exc_002/exc_002_rep_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_002/exc_002_rep_720p.m3u8" % (BASE_DIR_curefit),
            "time": 2.52,
            "offset": 0
        },
        "end": {}
    },
    "exc_003": {
        "name": "Quad Rockers",
        "thumbnail": "%s/exc_003/thumb_003.png" % (BASE_DIR_curefit),
        "offset": 4,
        "start": {
            "playlist": "#EXTINF:6.960000,\n%s/exc_003/exc_003_sta_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_003/exc_003_sta_720p.m3u8" % (BASE_DIR_curefit),
            "time": 6.96,
            "offset": 2
        },
        "rep": {
            "playlist": "#EXTINF:2.280000,\n%s/exc_003/exc_003_rep_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_003/exc_003_rep_720p.m3u8" % (BASE_DIR_curefit),
            "time": 2.28,
            "offset": 0
        },
        "end": {
            "playlist": "#EXTINF:5.360000,\n%s/exc_003/exc_003_end_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_003/exc_003_end_720p.m3u8" % (BASE_DIR_curefit),
            "time": 5.36,
            "offset": -2
        }
    },
    "exc_004": {
        "name": "Skipping",
        "thumbnail": "%s/exc_004/thumb_004.png" % (BASE_DIR_curefit),
        "offset": 0,
        "start": {
            "playlist": "#EXTINF:1.480000,\n%s/exc_004/exc_004_sta_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_004/exc_004_sta_720p.m3u8" % (BASE_DIR_curefit),
            "time": 1.48,
            "offset": 0
        },
        "rep": {
            "playlist": "#EXTINF:0.480000,\n%s/exc_004/exc_004_rep_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_004/exc_004_rep_720p.m3u8" % (BASE_DIR_curefit),
            "time": 0.48,
            "offset": 0
        },
        "end": {
            "playlist": "#EXTINF:1.800000,\n%s/exc_004/exc_004_end_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_004/exc_004_end_720p.m3u8" % (BASE_DIR_curefit),
            "time": 1.8,
            "offset": 0
        }
    },
    "exc_005": {
        "name": "Squat Knee to Chest",
        "thumbnail": "%s/exc_005/thumb_005.png" % (BASE_DIR_curefit),
        "offset": 1,
        "start": {
            "playlist": "#EXTINF:2.760000,\n%s/exc_005/exc_005_sta_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_005/exc_005_sta_720p.m3u8" % (BASE_DIR_curefit),
            "time": 2.76,
            "offset": 0
        },
        "rep": {
            "playlist": "#EXTINF:2.120000,\n%s/exc_005/exc_005_rep_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_005/exc_005_rep_720p.m3u8" % (BASE_DIR_curefit),
            "time": 2.12,
            "offset": 0
        },
        "end": {
            "playlist": "#EXTINF:3.840000,\n%s/exc_005/exc_005_end_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_005/exc_005_end_720p.m3u8" % (BASE_DIR_curefit),
            "time": 3.84,
            "offset": -1
        }
    },
    "exc_006": {
        "name": "Butt Kick",
        "thumbnail": "%s/exc_006/thumb_006.png" % (BASE_DIR_curefit),
        "offset": 0,
        "start": {
            "playlist": "#EXTINF:2.720000,\n%s/exc_006/exc_006_sta_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_006/exc_006_sta_720p.m3u8" % (BASE_DIR_curefit),
            "time": 2.72,
            "offset": 0
        },
        "rep": {
            "playlist": "#EXTINF:1.680000,\n%s/exc_006/exc_006_rep_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_006/exc_006_rep_720p.m3u8" % (BASE_DIR_curefit),
            "time": 1.68,
            "offset": 0
        },
        "end": {
            "playlist": "#EXTINF:3.480000,\n%s/exc_006/exc_006_end_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_006/exc_006_end_720p.m3u8" % (BASE_DIR_curefit),
            "time": 3.48,
            "offset": 0
        }
    },
    "exc_007": {
        "name": "Twist",
        "thumbnail": "%s/exc_007/thumb_007.png" % (BASE_DIR_curefit),
        "offset": 0,
        "start": {
            "playlist": "#EXTINF:1.200000,\n%s/exc_007/exc_007_sta_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_007/exc_007_sta_720p.m3u8" % (BASE_DIR_curefit),
            "time": 1.2,
            "offset": 0
        },
        "rep": {
            "playlist": "#EXTINF:1.000000,\n%s/exc_007/exc_007_rep_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_007/exc_007_rep_720p.m3u8" % (BASE_DIR_curefit),
            "time": 1.0,
            "offset": 0
        },
        "end": {
            "playlist": "#EXTINF:0.800000,\n%s/exc_007/exc_007_end_720p_0000.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit),
            "file": "%s/exc_007/exc_007_end_720p.m3u8" % (BASE_DIR_curefit),
            "time": 0.8,
            "offset": 0
        }
    },
    "rest": {
        "name": "Rest",
        "start": {},
        "offset": 0,
        "rep": {
            "playlist": "#EXTINF:10.000000,\n%s/rest/rest_720p_0000.ts\n#EXTINF:7.200000,\n%s/rest/rest_720p_0001.ts\n#EXT-X-DISCONTINUITY" % (BASE_DIR_curefit, BASE_DIR_curefit),
            "file": "%s/rest/rest_720p.m3u8" % (BASE_DIR_curefit),
            "time": 17.2,
            "offset": 0
        },
        "end": {}
    }
}
