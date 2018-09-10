import os
import util.detection_utils as util
import json

metadata_file_dict = {'highlights': []}
highlight_start_offset = 0
highlight_end_offset = 0


def extract_highlights(metadata, src_video_path, dest_video_path, only_metadata=False):
    if not os.path.exists(dest_video_path):
        os.makedirs(dest_video_path)

    # show start sec, show_duration_sec, video_name, show_start_utc
    highlights = [[entry[1], entry[2], entry[6], entry[8]] for entry in metadata if entry[3] == 'highlight']
    total_duration = 0

    if not os.path.exists(dest_video_path + '/metadata.json'):
        i = 0
        for highlight in highlights:
            filename = 'highlight_' + highlight[0] + highlight[2]
            player_stream = highlight[2].split('.')[0].split('_')[1]
            highlight_start = int(highlight[0]) - highlight_start_offset
            highlight_date = highlight[2].split('_')[0]

            if i == 0:
                highlight_duration = int(highlight[1]) + highlight_end_offset
            else:
                highlight_duration = int(highlight[1]) + highlight_end_offset

            total_duration += highlight_duration

            if not only_metadata:
                util.cut_video_within_boundaries(os.path.join(src_video_path, highlight[2]), highlight_start,
                                                 highlight_duration,
                                                 os.path.join(dest_video_path, filename))

            metadata_file_dict['highlights'].append({'highlight_start_sec': highlight_start,
                                                     'highlight_duration': highlight_duration,
                                                     'src_file': os.path.join(src_video_path, highlight[2]),
                                                     'target_file': os.path.join(dest_video_path, filename),
                                                     'player_stream': player_stream,
                                                     'highlight_date': highlight_date})

            i += 1

        metadata_file_dict['total_duration'] = util.sec_to_timestamp(total_duration)


        with open(dest_video_path + '/metadata.json', 'w') as fp:
            json.dump(metadata_file_dict, fp)
