import os
import util.detection_utils as util


show_start_offset = 45
show_end_offset = 0

first_show_max_duration = 10
show_max_duration = 25


def extract_shows(metadata, src_video_path, dest_video_path):
    if not os.path.exists(dest_video_path):
        os.makedirs(dest_video_path)

    #show start sec, show_duration_sec, video_name, show_start_utc
    shows = [[entry[1], entry[2], entry[6], entry[8]] for entry in metadata if entry[3] == 'show']

    i = 0
    for show in shows:
        filename = 'show_begin_' + show[0] + show[2]
        show_start = int(show[0]) - show_start_offset

        if i == 0:
            show_duration = min(int(show[1]) + show_end_offset, first_show_max_duration)
        else:
            show_duration = min(int(show[1]) + show_end_offset, show_max_duration)

        util.cut_video_within_boundaries(os.path.join(src_video_path, show[2]), show_start, show_duration,
                                         os.path.join(dest_video_path, filename))

        i += 1
