import TimelineReader
import json
# import round_detector
# import kill_detector
from datetime import datetime
import csv
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def timestamp_to_sec(timestamp):
    split_timestamp = timestamp.split(':')
    stream_timestamp_sec = int(split_timestamp[0]) * 3600 + int(split_timestamp[1]) * 60 + int(
        split_timestamp[2].split('.')[0])
    return stream_timestamp_sec


def sec_to_timestamp(sec):
    seconds = sec % 60
    minutes = sec // 60
    hours = 0
    if minutes > 60:
        hours = minutes // 60
        minutes = minutes % 60
    return str(hours) + ':' + str(minutes) + ':' + str(seconds)


def read_metadata_csv():
    metadata = []
    with open('data/metadata.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        line = 0
        for row in reader:
            if line > 0:
                metadata.append(row)
            else:
                line = line + 1
    return metadata


# returns the row in metadata where the match with nr matchnr starts for player with id playerId
def get_match_begin_in_player_stream(matchnr, metadata, playerId):
    for entry in metadata:
        if entry[3] == 'match' and entry[4] == str(matchnr) and entry[5] == 'P' + str(playerId):
            return entry


def get_datetime_from_utc_string(string):
    filteredString = string.split('+')[0].replace('T', ' ')
    if filteredString.find('.') == -1:
        return datetime.strptime(filteredString, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.strptime(filteredString, "%Y-%m-%d %H:%M:%S.%f")

def cut_video_within_boundaries(src_path_to_video, begin_sec, end_sec, dest_video_name):
    ffmpeg_extract_subclip(src_path_to_video, begin_sec, end_sec, targetname=dest_video_name)


src_video_path = 'D:/gamestory18-data/train_set'
dest_video_path = 'D:/gamestory18-data/killstreaks'
metadata_csv = read_metadata_csv()
first_match_utc = ''
search_round_offset_sec = 50
search_kill_offset_sec = 2
clipping_offset_sec = 5
max_killstreak_length = 300
metadata = {'killstreaks': {5: {}, 4: {}, 3: {}, 2: {}}}

# iterate over all 11 matches from 1.json - 11.json
for i in range(3, 4):
    # create dest. video folder if not exists
    if not os.path.exists(dest_video_path):
        os.makedirs(dest_video_path)

    json_file = open('timelines/' + str(i) + '.json')
    all_rounds_data = TimelineReader.preprocess(json.load(json_file))
    # keeps track of the total score for each round
    score_map = TimelineReader.get_score_map_for_match(all_rounds_data)
    kill_streak_list = TimelineReader.get_kill_streak_list(all_rounds_data)

    stream_begin_row = get_match_begin_in_player_stream(i, metadata_csv, 11)

    stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
    stream_begin_sec = timestamp_to_sec(stream_begin_timestamp)  # start position in video in seconds
    match_begin_timestamp_utc = get_datetime_from_utc_string(stream_begin_row[8])  # start of match

    # Sorted by highest KillStreakLength desc
    sorted_kill_streak_list = TimelineReader.sort_kill_streaks(kill_streak_list)
    if 5 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[5]:
            print(score_map)
            print('Looking for 5Killstreak in match ' + str(i) + '. Begin of match at ' + sec_to_timestamp(stream_begin_sec))
            # Length information needed for searching and clipping
            killstreak_begin_utc_time = get_datetime_from_utc_string(killstreak[0]['date'])
            killstreak_end_utc_time = get_datetime_from_utc_string(killstreak[4]['date'])

            print("match begin utc: " + str(match_begin_timestamp_utc))
            print("killstreak begin utc: " + str(killstreak_begin_utc_time))
            difference_between_match_begin_and_killstreak_begin = killstreak_begin_utc_time - match_begin_timestamp_utc

            print('differnece between match begin and killstreak begin: ' + str(difference_between_match_begin_and_killstreak_begin))
            killstreak_duration = killstreak_end_utc_time - killstreak_begin_utc_time
            killstreak_duration_sec = timestamp_to_sec(str(killstreak_duration))
            round_idx = killstreak[0]['roundIdx']
            video_full_name = src_video_path + '/' + stream_begin_row[6]

            # Only killstreak which are shorter than max_killstreak_length are considered
            if timestamp_to_sec(str(killstreak_duration)) < max_killstreak_length:
                start_pos_in_video_sec = stream_begin_sec + timestamp_to_sec(str(difference_between_match_begin_and_killstreak_begin))
                dest_video_name = 'killstreak_5_round_' + str(round_idx) + '_begin_' + sec_to_timestamp(
                    start_pos_in_video_sec - 5).replace(':', '_') + '_' + stream_begin_row[6]
                end_pos_in_video_sec = start_pos_in_video_sec + killstreak_duration_sec

                # Detect the start time in seconds of the round where the killstreak is performed
                # round_begin_sec = round_detector.get_round_begin(start_pos_in_video_sec - search_round_offset_sec,
                #                                                  end_pos_in_video_sec + search_round_offset_sec, video_full_name,
                #                                                  score_map[round_idx][0], score_map[round_idx][1])
                #
                # # Detect the start time in seconds of the first kill of the killstreak
                # killstreak_begin_sec = kill_detector.get_first_kill_sec(round_begin_sec + search_kill_offset_sec,
                #                                                         end_pos_in_video_sec + search_round_offset_sec,
                #                                                         video_full_name,
                #                                                         killstreak[0]['data']['actor']['ingameTeam'])
                # # Collect meta-information which is stored in a json file in dest folder
                #
                # metadata['killstreaks'][5][dest_video_name] = {}
                # metadata['killstreaks'][5][dest_video_name]['duration'] = killstreak_duration_sec + 2 * clipping_offset_sec
                # metadata['killstreaks'][5][dest_video_name]['match'] = str(i)
                # metadata['killstreaks'][5][dest_video_name]['round'] = str(round_idx)
                #
                # with open(dest_video_path + '/metadata.json', 'w') as fp:
                #     json.dump(metadata, fp)
                #
                # # Cut the video and store it
                # cut_video_within_boundaries(video_full_name, killstreak_begin_sec - clipping_offset_sec,
                #                             killstreak_begin_sec + timestamp_to_sec(str(killstreak_duration)) + clipping_offset_sec,
                #                             dest_video_path + '/' + dest_video_name)
