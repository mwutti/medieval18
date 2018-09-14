import util.detection_utils as util
from killstreak_clipper import kill_detector

video_full_name = 'D:/gamestory18-data/train_set/2018-03-04_P11.mp4'

sec = kill_detector.get_nth_kill_sec(util.timestamp_to_sec('7:10:5'), util.timestamp_to_sec('7:10:24'),
                                     video_full_name, nth_kill=4, player_stream='P11')

print(sec)
