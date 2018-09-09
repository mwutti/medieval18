import TimelineReader
import json
import logging as logger
import kill_detector
import round_detector
import show_extractor
import os
import util.detection_utils as util

# debug = True
debug = False

logger.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logger.DEBUG)
src_video_path = 'D:/gamestory18-data/train_set'
killstreak_dest_video_path = 'D:/gamestory18-data/killstreaks'
last_round_dest_video_path = 'D:/gamestory18-data/last_round'
shows_dest_video_path = 'D:/gamestory18-data/shows'
first_match_utc = ''
search_round_offset_sec = 40
search_kill_offset_sec = 1
clipping_offset_before_sec = 5
clipping_offset_after_sec = 12
max_killstreak_length = 20
killstreaks = {'killstreaks': {5: {}, 4: {}, 3: {}}}

def add_killstreak_to_list(nrOfKills, dest_video_name, killstreak_duration_sec, round_idx, round_begin,
                           killstreak_begin, estimated_begin, estimated_end):
    target_killstreak_list = killstreaks['killstreaks'][nrOfKills]

    target_killstreak_list[dest_video_name] = {}
    target_killstreak_list[dest_video_name][
        'duration'] = killstreak_duration_sec + clipping_offset_before_sec + clipping_offset_after_sec
    target_killstreak_list[dest_video_name]['match'] = str(i)
    target_killstreak_list[dest_video_name]['round'] = str(round_idx)
    target_killstreak_list[dest_video_name]['round_begin'] = round_begin
    target_killstreak_list[dest_video_name]['killstreak_begin'] = killstreak_begin
    target_killstreak_list[dest_video_name]['killstreak_begin_sec'] = util.timestamp_to_sec(killstreak_begin)
    target_killstreak_list[dest_video_name]['estimated_begin'] = estimated_begin
    target_killstreak_list[dest_video_name]['estimated_end'] = estimated_end


def log_killstreak_to_file(nrOfKills):
    if not os.path.exists(killstreak_dest_video_path + '/' + str(nrOfKills) + '/metadata.json'):
        with open(killstreak_dest_video_path + '/' + str(nrOfKills) + '/metadata.json', 'w') as fp:
            json.dump(killstreaks, fp)


def determine_kills(killstreak, all_rounds_data):
    result = 1
    roundIdx = killstreak[0]['roundIdx']
    killstreak_begin_utc_timestamp = killstreak[0]['date']
    round_data = all_rounds_data[roundIdx]

    for kill in round_data['kill']:
        timestamp_begin = util.get_datetime_from_utc_string(killstreak_begin_utc_timestamp)
        timestamp_target = util.get_datetime_from_utc_string(kill['date'])
        if timestamp_target < timestamp_begin:
            result += 1

    return result


def extract_killstreak(killstreak, killstreak_length, nth_kill, stream_begin_row, stream_begin_sec, match_begin_timestamp_utc):
    # Length information needed for searching and clipping
    killstreak_begin_utc_time = util.get_datetime_from_utc_string(killstreak[0]['date'])
    killstreak_end_utc_time = util.get_datetime_from_utc_string(killstreak[killstreak_length - 1]['date'])

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
        logger.info('Looking for ' + str(killstreak_length) + '-Killstreak in match ' + str(
            i) + '. Begin of match at ' + util.sec_to_timestamp(stream_begin_sec))

        start_pos_in_video_sec = stream_begin_sec + util.timestamp_to_sec(
            str(difference_between_match_begin_and_killstreak_begin))

        dest_video_name = 'killstreak_' + str(killstreak_length) + '_round_' + str(
            round_idx) + '_begin_' + util.sec_to_timestamp(
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
            # try to swap the round numbers
            round_begin_sec = round_detector.get_round_begin(start_pos_in_video_sec - search_round_offset_sec,
                                                             end_pos_in_video_sec + search_round_offset_sec,
                                                             video_full_name,
                                                             target_round_T, target_round_CT)
            if round_begin_sec is None:
                logger.warning('Unable to detect round begin, skip this killstreak')
                return

        # Detect the start time in seconds of the first kill of the killstreak
        killstreak_begin_sec = kill_detector.get_nth_kill_sec(round_begin_sec + search_kill_offset_sec,
                                                              end_pos_in_video_sec + search_round_offset_sec,
                                                              video_full_name, nth_kill)

        if killstreak_begin_sec is None:
            logger.warning('Unable to detect killstreak begin, skip this killstreak')
        else:
            # Log Killstreak to file
            add_killstreak_to_list(killstreak_length, dest_video_name, killstreak_duration_sec, round_idx,
                                   util.sec_to_timestamp(round_begin_sec), util.sec_to_timestamp(killstreak_begin_sec),
                                   util.sec_to_timestamp(start_pos_in_video_sec),
                                   util.sec_to_timestamp(end_pos_in_video_sec))

            # Cut the video and store it
            util.cut_video_within_boundaries(video_full_name, killstreak_begin_sec - clipping_offset_before_sec,
                                        util.timestamp_to_sec(str(killstreak_duration)) + clipping_offset_after_sec,
                                        killstreak_dest_video_path + '/' + str(killstreak_length) + '/' + dest_video_name)
    else:
        logger.info("Killstreak duration in match " + str(i) + ": " + str(
            killstreak_duration_sec) + 'sec is above threshold of ' + str(max_killstreak_length))

def extract_all_killstreaks(all_rounds_data, sorted_kill_streak_list, stream_begin_row,
                            stream_begin_sec, match_begin_timestamp_utc):
    # detect 5-Killstreaks
    if os.path.exists(killstreak_dest_video_path + '/5/metadata.json'):
        logger.info("5-Killstreaks for match " + str(
            i) + " already detected and extracted. Delete " + killstreak_dest_video_path + '/5/metadata.json to redetect killstreaks')
    elif 5 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[5]:
            extract_killstreak(killstreak, 5, 1, stream_begin_row, stream_begin_sec, match_begin_timestamp_utc)

    # detect 4-Killstreaks
    if os.path.exists(killstreak_dest_video_path + '/4/metadata.json'):
        logger.info("4-Killstreaks for match " + str(
            i) + " already detected and extracted. Delete " + killstreak_dest_video_path + '/4/metadata.json to redetect killstreaks')
    elif 4 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[4]:
            # determine how many kills where performed
            nth_kill = determine_kills(killstreak, all_rounds_data)
            extract_killstreak(killstreak, 4, nth_kill, stream_begin_row, stream_begin_sec, match_begin_timestamp_utc)

    # detect 3-Killstreaks
    if os.path.exists(killstreak_dest_video_path + '/3/metadata.json'):
        logger.info("3-Killstreaks for match " + str(
            i) + " already detected and extracted. Delete " + killstreak_dest_video_path + '/3/metadata.json to redetect killstreaks')
    elif 3 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[4]:
            # determine how many kills where performed
            nth_kill = determine_kills(killstreak, all_rounds_data)
            extract_killstreak(killstreak, 3, nth_kill, stream_begin_row, stream_begin_sec, match_begin_timestamp_utc)
#########################################################


# create dest. video folders if not exists
for j in range(3, 6):
    if not os.path.exists(killstreak_dest_video_path + '/' + str(j)):
        os.makedirs(killstreak_dest_video_path + '/' + str(j))

if not os.path.exists(last_round_dest_video_path):
    os.makedirs(last_round_dest_video_path)

logger.info("Starting Killstreak-Clipper")
print(kill_detector.skull)

metadata_csv = util.read_metadata_csv()

detect_killstreaks = False
if detect_killstreaks:
    round_detector = round_detector.RoundDetector()
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

            # extract all 5, 4, 3 killstreaks
            extract_all_killstreaks(all_rounds_data, sorted_kill_streak_list, stream_begin_row,
                                    stream_begin_sec, match_begin_timestamp_utc)

            # extract all last rounds of match sequences

    [log_killstreak_to_file(i) for i in range(3, 6)]

extract_shows = True
if extract_shows:
    logger.info('Etracting shows')
    show_extractor.extract_shows(metadata_csv, src_video_path, shows_dest_video_path)

