import os
import util.detection_utils as util
import json


metadata_file_dict = {'shows': []}
show_start_offset = 45
show_end_offset = 7

first_show_max_duration = 10
show_max_duration = 25


def extract_shows(metadata, src_video_path, dest_video_path):
    if not os.path.exists(dest_video_path):
        os.makedirs(dest_video_path)

    #show start sec, show_duration_sec, video_name, show_start_utc
    shows = [[entry[1], entry[2], entry[6], entry[8]] for entry in metadata if entry[3] == 'show']

    if not os.path.exists(dest_video_path + '/metadata.json'):
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

            metadata_file_dict['shows'].append({'show_start_sec': show_start, 'show_duration': show_duration, 'src_file': os.path.join(src_video_path, show[2]),
                                                'target_file': os.path.join(dest_video_path, filename)})

            i += 1

        with open(dest_video_path + '/metadata.json', 'w') as fp:
            json.dump(metadata_file_dict, fp)
