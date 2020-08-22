from activity_ops.models import ActivityOps


video_ids = ['celebs_video_002', 'murti_making_video_003',
             'live_aarti_video_004', 'celebs_video_005']


video_datas = {
    "celebs_video_002": ['shilpa_button', 'sonakshi_button', 'bhai_button', 'nawaz_button'],
    "murti_making_video_003": ['murti_making_01_button', 'murti_making_02_button', 'murti_making_03_button', 'murti_making_04_button'],
    "live_aarti_video_004": ['ballaleshvar_button', 'udhyan_button', 'shiddhivinayak_button', 'khajrana_button'],
    "celebs_video_005": ['celebs_of_bollywood_1_button', 'celebs_of_bollywood_2_button', 'celebs_of_bollywood_3_button', 'celebs_of_bollywood_4_button']
}


for video_id, button_list in video_datas.items():
    video_load = ActivityOps.objects.filter(
        video_id=video_id, activity="load").count()
    video_play = ActivityOps.objects.filter(
        video_id=video_id, activity="play").count()

    print("%s, ++++++, %d, %d" % (video_id, video_play, video_load))
    for button in button_list:
        button_count = ActivityOps.objects.filter(
            video_id=video_id, activity="click", button_id=button).count()
        print("++++++, %s, %d, ------" % (button, button_count))
