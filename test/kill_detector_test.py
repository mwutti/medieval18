import util.detection_utils as util
from killstreak_clipper import kill_detector

video_full_name = 'D:/gamestory18-data/train_set/2018-03-04_P9.mp4'

sec = kill_detector.get_nth_kill_sec(util.timestamp_to_sec('9:10:25'), util.timestamp_to_sec('9:13:15'),
                                     video_full_name, nth_kill=1, player_stream='P9')

print(sec)
