
import util.detection_utils as util
from killstreak_clipper import round_detector

search_round_offset_sec = 0
search_kill_offset_sec = 1
clipping_offset_before_sec = 5
clipping_offset_after_sec = 12
max_killstreak_length = 20


def test_1():
    start_pos = util.timestamp_to_sec('8:57:41') - search_round_offset_sec
    end_pos = util.timestamp_to_sec('8:59:07') + search_round_offset_sec
    video_full_name = 'D:/gamestory18-data/train_set/2018-03-04_P3.mp4'

    round_begin_sec = round_detector.get_round_begin(start_pos,
                                                     end_pos,
                                                     video_full_name,
                                                     13, 10, player_stream=True)
    if round_begin_sec is None:
        raise ValueError("test_1 failed")


def test_1_P11():
    start_pos = util.timestamp_to_sec('8:5:4') - search_round_offset_sec
    end_pos = util.timestamp_to_sec('8:6:42') + search_round_offset_sec
    video_full_name = 'D:/gamestory18-data/train_set/2018-03-04_P11.mp4'

    round_begin_sec = round_detector.get_round_begin(start_pos,
                                                     end_pos,
                                                     video_full_name,
                                                     15, 15, player_stream='P11')
    if round_begin_sec is None:
        raise ValueError("test_2 failed")


def test_2_P11():
    start_pos = util.timestamp_to_sec('7:20:08') - search_round_offset_sec
    end_pos = util.timestamp_to_sec('7:21:42') + search_round_offset_sec
    video_full_name = 'D:/gamestory18-data/train_set/2018-03-04_P11.mp4'

    round_begin_sec = round_detector.get_round_begin(start_pos,
                                                     end_pos,
                                                     video_full_name,
                                                     3, 6, player_stream='P11', pos_at_one_round_detected=True)
    if round_begin_sec is None:
        raise ValueError("test_2 failed")


test_2_P11()
