import TimelineReader
import json
import logging
import kill_detector
import round_detector
import os
import util.detection_utils as util

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

# debug = True
debug = False
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
src_video_path = 'D:/gamestory18-data/train_set'
dest_video_path = 'D:/gamestory18-data/killstreaks'
metadata_csv = util.read_metadata_csv()
first_match_utc = ''
search_round_offset_sec = 50
search_kill_offset_sec = 2
clipping_offset_sec = 5
max_killstreak_length = 40
round_detector = round_detector.RoundDetector()

killstreaks = {'killstreaks': {5: {}, 4: {}, 3: {}}}


def cut_video_within_boundaries(src_path_to_video, begin_sec, end_sec, dest_video_name):
    ffmpeg_extract_subclip(src_path_to_video, begin_sec, end_sec, targetname=dest_video_name)


def add_killstreak_to_list(nrOfKills, dest_video_name, killstreak_duration_sec, round_idx):
    target_killstreak_list = killstreaks['killstreaks'][nrOfKills]

    target_killstreak_list[dest_video_name] = {}
    target_killstreak_list[dest_video_name]['duration'] = killstreak_duration_sec + 2 * clipping_offset_sec
    target_killstreak_list[dest_video_name]['match'] = str(i)
    target_killstreak_list[dest_video_name]['round'] = str(round_idx)


def log_killstreak_to_file(nrOfKills):
    with open(dest_video_path + '/' + str(nrOfKills) + '/metadata.json', 'w') as fp:
        json.dump(killstreaks, fp)


def extract_4_killstreaks(killstreak):
    # Length information needed for searching and clipping
    killstreak_begin_utc_time = util.get_datetime_from_utc_string(killstreak[0]['date'])
    killstreak_end_utc_time = util.get_datetime_from_utc_string(killstreak[3]['date'])

    if debug:
        print("match begin utc: " + str(match_begin_timestamp_utc))
        print("killstreak begin utc: " + str(killstreak_begin_utc_time))
    difference_between_match_begin_and_killstreak_begin = killstreak_begin_utc_time - match_begin_timestamp_utc

    if debug:
        print('difference between match begin and killstreak begin: ' + str(
            difference_between_match_begin_and_killstreak_begin))
    killstreak_duration = killstreak_end_utc_time - killstreak_begin_utc_time
    killstreak_duration_sec = util.timestamp_to_sec(str(killstreak_duration))
    round_idx = killstreak[0]['roundIdx']
    video_full_name = src_video_path + '/' + stream_begin_row[6]

    start_pos_in_video_sec = stream_begin_sec + util.timestamp_to_sec(
        str(difference_between_match_begin_and_killstreak_begin))

    dest_video_name = 'killstreak_4_round_' + str(round_idx) + '_begin_' + util.sec_to_timestamp(
        start_pos_in_video_sec - 5).replace(':', '_') + '_' + stream_begin_row[6]

    # Only killstreak which are shorter than max_killstreak_length are considered
    if util.timestamp_to_sec(str(killstreak_duration)) < max_killstreak_length:
        logging.info('Looking for 4-Killstreak in match ' + str(i) + '. Begin of match at ' + util.sec_to_timestamp(
            stream_begin_sec))

        start_pos_in_video_sec = stream_begin_sec + util.timestamp_to_sec(
            str(difference_between_match_begin_and_killstreak_begin))

        dest_video_name = 'killstreak_4_round_' + str(round_idx) + '_begin_' + util.sec_to_timestamp(
            start_pos_in_video_sec - 5).replace(':', '_') + '_' + stream_begin_row[6]

        end_pos_in_video_sec = start_pos_in_video_sec + killstreak_duration_sec

        # Detect the start time in seconds of the round where the killstreak is performed
        target_round_CT = 0
        target_round_T = 0
        # get target round numbers from score_map
        if round_idx > 1:
            for teamID in score_map[round_idx - 2]:
                if score_map[round_idx - 2][teamID]['ingameTeam'] == 'CT':
                    target_round_CT = score_map[round_idx - 2][teamID]['score']
                else:
                    target_round_T = score_map[round_idx - 2][teamID]['score']

        round_begin_sec = round_detector.get_round_begin(start_pos_in_video_sec - search_round_offset_sec,
                                                         end_pos_in_video_sec + search_round_offset_sec,
                                                         video_full_name,
                                                         target_round_CT, target_round_T)
        if round_begin_sec is None:
            logging.warning('Unable to detect round begin, skip this killstreak')
        else:
            # Detect the start time in seconds of the first kill of the killstreak
            killstreak_begin_sec = kill_detector.get_first_kill_sec(round_begin_sec + search_kill_offset_sec,
                                                                    end_pos_in_video_sec + search_round_offset_sec,
                                                                    video_full_name,
                                                                    killstreak[0]['data']['actor']['ingameTeam'])
            if killstreak_begin_sec is None:
                logging.warning('Unable to detect killstreak begin, skip this killstreak')
            else:
                # Log Killstreak to file
                add_killstreak_to_list(4, dest_video_name, killstreak_duration_sec, round_idx)

                # Cut the video and store it
                cut_video_within_boundaries(video_full_name, killstreak_begin_sec - clipping_offset_sec,
                                            killstreak_begin_sec + util.timestamp_to_sec(
                                                str(killstreak_duration)) + clipping_offset_sec,
                                            dest_video_path + '/4/' + dest_video_name)
    else:
        logging.info("4-Killstreak duration in match " + str(i) + ": " + str(
            killstreak_duration_sec) + 'sec is above threshold of ' + str(max_killstreak_length))


def extract_5_killstreaks(killstreak):
    # Length information needed for searching and clipping
    killstreak_begin_utc_time = util.get_datetime_from_utc_string(killstreak[0]['date'])
    killstreak_end_utc_time = util.get_datetime_from_utc_string(killstreak[4]['date'])

    if debug:
        print("match begin utc: " + str(match_begin_timestamp_utc))
        print("killstreak begin utc: " + str(killstreak_begin_utc_time))
    difference_between_match_begin_and_killstreak_begin = killstreak_begin_utc_time - match_begin_timestamp_utc

    if debug:
        print('difference between match begin and killstreak begin: ' + str(
            difference_between_match_begin_and_killstreak_begin))
    killstreak_duration = killstreak_end_utc_time - killstreak_begin_utc_time
    killstreak_duration_sec = util.timestamp_to_sec(str(killstreak_duration))
    round_idx = killstreak[0]['roundIdx']
    video_full_name = src_video_path + '/' + stream_begin_row[6]

    # Only killstreak which are shorter than max_killstreak_length are considered
    if util.timestamp_to_sec(str(killstreak_duration)) < max_killstreak_length:
        logging.info('Looking for 5-Killstreak in match ' + str(i) + '. Begin of match at ' + util.sec_to_timestamp(
            stream_begin_sec))

        start_pos_in_video_sec = stream_begin_sec + util.timestamp_to_sec(
            str(difference_between_match_begin_and_killstreak_begin))

        dest_video_name = 'killstreak_5_round_' + str(round_idx) + '_begin_' + util.sec_to_timestamp(
            start_pos_in_video_sec - 5).replace(':', '_') + '_' + stream_begin_row[6]

        end_pos_in_video_sec = start_pos_in_video_sec + killstreak_duration_sec

        # Detect the start time in seconds of the round where the killstreak is performed
        target_round_CT = 0
        target_round_T = 0
        # get target round numbers from score_map
        if round_idx > 1:
            for teamID in score_map[round_idx - 2]:
                if score_map[round_idx - 2][teamID]['ingameTeam'] == 'CT':
                    target_round_CT = score_map[round_idx - 2][teamID]['score']
                else:
                    target_round_T = score_map[round_idx - 2][teamID]['score']

        round_begin_sec = round_detector.get_round_begin(start_pos_in_video_sec - search_round_offset_sec,
                                                         end_pos_in_video_sec + search_round_offset_sec,
                                                         video_full_name,
                                                         target_round_CT, target_round_T)

        # Detect the start time in seconds of the first kill of the killstreak
        killstreak_begin_sec = kill_detector.get_first_kill_sec(round_begin_sec + search_kill_offset_sec,
                                                                end_pos_in_video_sec + search_round_offset_sec,
                                                                video_full_name,
                                                                killstreak[0]['data']['actor']['ingameTeam'])
        # Log Killstreak to file
        add_killstreak_to_list(5, dest_video_name, killstreak_duration_sec, round_idx)

        # Cut the video and store it
        cut_video_within_boundaries(video_full_name, killstreak_begin_sec - clipping_offset_sec,
                                    killstreak_begin_sec + util.timestamp_to_sec(
                                        str(killstreak_duration)) + clipping_offset_sec,
                                    dest_video_path + '/5/' + dest_video_name)
    else:
        logging.info("5-Killstreak duration in match " + str(i) + ": " + str(
            killstreak_duration_sec) + 'sec is above threshold of ' + str(max_killstreak_length))


# create dest. video folders if not exists
for j in range(3, 6):
    if not os.path.exists(dest_video_path + '/' + str(j)):
        os.makedirs(dest_video_path + '/' + str(j))

# iterate over all 11 matches from 1.json - 11.json
for i in range(1, 12):
    # 10.json is not correct!
    if i != 10:
        json_file = open('timelines/' + str(i) + '.json')
        all_rounds_data = TimelineReader.preprocess(json.load(json_file))

        score_map = TimelineReader.get_score_map_for_match(
            all_rounds_data)  # keeps track of the total score for each round

        kill_streak_list = TimelineReader.get_kill_streak_list(all_rounds_data)
        sorted_kill_streak_list = TimelineReader.sort_kill_streaks(
            kill_streak_list)  # Sorted by highest KillStreakLength desc

        stream_begin_row = util.get_match_begin_in_player_stream(i, metadata_csv, 11)
        stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
        stream_begin_sec = util.timestamp_to_sec(stream_begin_timestamp)  # start position in video in seconds
        match_begin_timestamp_utc = util.get_datetime_from_utc_string(stream_begin_row[8])  # start of match

        # # detect 5-Killstreaks
        # if os.path.exists(dest_video_path + '/5/metadata.json'):
        #     logging.info("5-Killstreaks for match " + str(
        #         i) + " already detected and extracted. Delete " + dest_video_path + '/5/metadata.json to redetect killstreaks')
        # elif 5 in sorted_kill_streak_list:
        #     for killstreak in sorted_kill_streak_list[5]:
        #         extract_5_killstreaks(killstreak)

        # detect 4-Killstreaks
        if os.path.exists(dest_video_path + '/4/metadata.json'):
            logging.info("4-Killstreaks for match " + str(
                i) + " already detected and extracted. Delete " + dest_video_path + '/4/metadata.json to redetect killstreaks')
        elif 4 in sorted_kill_streak_list:
            for killstreak in sorted_kill_streak_list[4]:
                extract_4_killstreaks(killstreak)

log_killstreak_to_file(5)
log_killstreak_to_file(4)
