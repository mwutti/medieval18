import TimelineReader
import json
import round_detector
from datetime import datetime
import csv
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


# 9 5-Killstreaks total
# 17 4-Killstreaks total

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


video_path = 'D:/gamestory18-data/train_set'
metadata = read_metadata_csv()
first_match_utc = ''
offest_sec = 50

# iterate over all 11 matches from 1.json - 11.json
for i in range(1, 7):
    json_file = open('timelines/' + str(i) + '.json')
    all_rounds_data = TimelineReader.preprocess(json.load(json_file))
    kill_streak_list = TimelineReader.get_kill_streak_list(all_rounds_data)

    #  search in p11 stream at match 7 there is a new stream
    if i == 1:
        stream_begin_row = get_match_begin_in_player_stream(i, metadata, 11)

    stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
    stream_begin_sec = timestamp_to_sec(stream_begin_timestamp)  # start position in video in seconds
    match_begin_timestamp_utc = get_datetime_from_utc_string(stream_begin_row[8])  # start of match

    # Sorted by highest KillStreakLength desc
    sorted_kill_streak_list = TimelineReader.sort_kill_streaks(kill_streak_list)
    if 5 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[5]:
            killstreak_begin_utc_time = get_datetime_from_utc_string(killstreak[0]['date'])
            killstreak_end_utc_time = get_datetime_from_utc_string(killstreak[4]['date'])
            difference_between_match_begin_and_killstreak_begin = killstreak_begin_utc_time - match_begin_timestamp_utc
            killstreak_duration = killstreak_end_utc_time - killstreak_begin_utc_time
            print('killstreak duration: ' + str(killstreak_duration))

            if timestamp_to_sec(str(killstreak_duration)) < 40:
                start_pos_in_video_sec = stream_begin_sec + timestamp_to_sec(str(difference_between_match_begin_and_killstreak_begin))
                end_pos_in_video_sec = start_pos_in_video_sec + timestamp_to_sec(str(killstreak_duration))

                video_full_name = video_path + '/' + stream_begin_row[6]
                begin_round = round_detector.get_round_begin(start_pos_in_video_sec - offest_sec, end_pos_in_video_sec + offest_sec, video_full_name,
                                                             12, 2)

                cut_video_within_boundaries(video_full_name, start_pos_in_video_sec - offest_sec, end_pos_in_video_sec + offest_sec,
                                            '5_round_' + str(killstreak[0]['roundIdx']) + '.mp4')

