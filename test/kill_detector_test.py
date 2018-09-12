import util.detection_utils as util
from killstreak_clipper import kill_detector

video_full_name = 'D:/gamestory18-data/train_set/2018-03-04_P11.mp4'

sec = kill_detector.get_nth_kill_sec(util.timestamp_to_sec('8:10:17'), util.timestamp_to_sec('8:11:46'),
                                     video_full_name, 4)

print(sec)
