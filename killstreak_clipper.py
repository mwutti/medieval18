import TimelineReader
import json
import logging as logger
import kill_detector
import round_detector
import show_extractor
import highlight_extractor
import os
import inspect
import util.detection_utils as util
import collage

# debug = True
debug = False

logger.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logger.DEBUG)
base_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
src_video_path = 'D:/gamestory18-data/train_set'
killstreak_dest_video_path = 'D:/gamestory18-data/killstreaks'
last_round_dest_video_path = 'D:/gamestory18-data/last_round'
shows_dest_video_path = 'D:/gamestory18-data/shows'
highlight_dest_video_path = 'D:/gamestory18-data/highlights'
first_match_utc = ''
search_round_offset_sec = 40
search_kill_offset_sec_before = 1
search_kill_offset_sec_after = 10
clipping_offset_before_sec = 5
clipping_offset_after_sec = {3: 12, 4: 12, 5: 20}
max_killstreak_length = 20
max_killstreak_length_5 = 61

detect_killstreaks = True
extract_shows = False
extract_last_rounds = True
extract_highlights = False
extract_videos = True
summarize_video = True

killstreaks = {'killstreaks': {5: {}, 4: {}, 3: {}}, 'last_round': {}}

player_id_to_name_map_match_11 = {'GuardiaN': '1',
                                  'olofmeister': '2',
                                  'NiKo': '3',
                                  'karrigan': '4',
                                  'rain': '5',
                                  'Golden': '6',
                                  'Lekr0': '7',
                                  'JW': '8',
                                  'flusha': '9',
                                  'KRIMZ': '10'}


def add_killstreak_to_list(nrOfKills, dest_video_name, killstreak_duration_sec, round_idx, round_begin,
                           killstreak_begin, estimated_begin, estimated_end, actor_name, actor_stream_nr):
    target_killstreak_list = killstreaks['killstreaks'][nrOfKills]

    target_killstreak_list[dest_video_name] = {}
    target_killstreak_list[dest_video_name][
        'duration'] = killstreak_duration_sec + clipping_offset_before_sec + clipping_offset_after_sec[nrOfKills]
    target_killstreak_list[dest_video_name]['match'] = str(i)
    target_killstreak_list[dest_video_name]['round'] = str(round_idx)
    target_killstreak_list[dest_video_name]['round_begin'] = round_begin
    target_killstreak_list[dest_video_name]['killstreak_begin'] = killstreak_begin
    target_killstreak_list[dest_video_name]['killstreak_begin_sec'] = util.timestamp_to_float_sec(killstreak_begin)
    target_killstreak_list[dest_video_name]['estimated_begin'] = estimated_begin
    target_killstreak_list[dest_video_name]['estimated_end'] = estimated_end
    target_killstreak_list[dest_video_name]['actor_name'] = actor_name
    target_killstreak_list[dest_video_name]['actor_stream_nr'] = actor_stream_nr


def add_lastround_to_list(match, dest_video_name, duration_sec, round_idx, begin_sec, actor_name, actor_stream):
    killstreaks['last_round'][dest_video_name] = {}
    target = killstreaks['last_round'][dest_video_name]

    target['match'] = match
    target['duration_sec'] = duration_sec
    target['round_idx'] = round_idx
    target['begin_sec'] = begin_sec
    target['actor_name'] = actor_name
    target['actor_stream'] = actor_stream

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


def extract_killstreak(killstreak, killstreak_length, nth_kill, stream_begin_row, stream_begin_sec,
                       match_begin_timestamp_utc, player_stream='P11'):
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
    if util.timestamp_to_sec(str(killstreak_duration)) < max_killstreak_length or ( killstreak_length == 5 and (util.timestamp_to_sec(str(killstreak_duration)) <= max_killstreak_length_5)):
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
                                                         target_round_CT, target_round_T, player_stream=player_stream)
        if round_begin_sec is None:
            # try to swap the round numbers
            round_begin_sec = round_detector.get_round_begin(start_pos_in_video_sec - search_round_offset_sec,
                                                             end_pos_in_video_sec + search_round_offset_sec,
                                                             video_full_name,
                                                             target_round_T, target_round_CT,
                                                             player_stream=player_stream)
            if round_begin_sec is None:
                # try to detect just one round
                logger.warning('Trying to detect just one round')
                round_begin_sec = round_detector.get_round_begin(start_pos_in_video_sec - search_round_offset_sec,
                                                                 end_pos_in_video_sec + search_round_offset_sec,
                                                                 video_full_name,
                                                                 target_round_CT, target_round_T,
                                                                 player_stream=player_stream,
                                                                 pos_at_one_round_detected=True)

                if round_begin_sec is None:
                    # swap the round numbers one last time
                    logger.warning('Swapping the round numbers one last time')
                    round_begin_sec = round_detector.get_round_begin(start_pos_in_video_sec - search_round_offset_sec,
                                                                     end_pos_in_video_sec + search_round_offset_sec,
                                                                     video_full_name,
                                                                     target_round_T, target_round_CT,
                                                                     player_stream=player_stream,
                                                                     pos_at_one_round_detected=True)
                    if round_begin_sec is None:
                        logger.error("Unable to detect round")
                        return
        # Todo BrainFuck
        # Detect the start time in seconds of the first kill of the killstreak
        killstreak_begin_sec = kill_detector.get_nth_kill_sec(round_begin_sec + search_kill_offset_sec_before,
                                                              end_pos_in_video_sec + search_round_offset_sec + search_kill_offset_sec_after,
                                                              video_full_name, nth_kill, player_stream=player_stream)

        if killstreak_begin_sec is None:
            logger.error('Unable to detect killstreak begin, skip this killstreak')
        else:
            player_name = killstreak[0]['data']['actor']['playerId']
            # Log Killstreak to file
            add_killstreak_to_list(killstreak_length, dest_video_name, killstreak_duration_sec, round_idx,
                                   util.sec_to_timestamp(round_begin_sec), util.sec_to_timestamp(killstreak_begin_sec),
                                   util.sec_to_timestamp(start_pos_in_video_sec),
                                   util.sec_to_timestamp(end_pos_in_video_sec), player_name,
                                   player_id_to_name_map_match_11[player_name])

            # Cut the video and store it
            if extract_videos:
                start_sec = killstreak_begin_sec - clipping_offset_before_sec

                util.cut_video_within_boundaries(video_full_name, start_sec,
                                                 util.timestamp_to_sec(
                                                     str(killstreak_duration)) + clipping_offset_after_sec[
                                                     killstreak_length],
                                                 killstreak_dest_video_path + '/' + str(
                                                     killstreak_length) + '/' + player_stream + '/' + dest_video_name)

    else:
        logger.info("Killstreak duration in match " + str(i) + ": " + str(
            killstreak_duration_sec) + 'sec is above threshold of ' + str(max_killstreak_length))


def extract_all_killstreaks(all_rounds_data, sorted_kill_streak_list, match=1, player_stream=False):
    # detect 5-Killstreaks
    if os.path.exists(killstreak_dest_video_path + '/5/metadata.json'):
        if debug:
            logger.info("5-Killstreaks for match " + str(
                i) + " already detected and extracted. Delete " + killstreak_dest_video_path + '/5/metadata.json to redetect killstreaks')
    elif 5 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[5]:
            # determine how many kills where performed
            nth_kill = determine_kills(killstreak, all_rounds_data)
            if not player_stream:
                # if player_stream == False extract only P11
                stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv, 11)
                stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
                stream_begin_sec = util.timestamp_to_sec(stream_begin_timestamp)  # start position in video in seconds
                match_begin_timestamp_utc = util.get_datetime_from_utc_string(stream_begin_row[8])  # start of match

                extract_killstreak(killstreak, 5, nth_kill, stream_begin_row, stream_begin_sec,
                                   match_begin_timestamp_utc,
                                   'P11')
            else:
                player_id = killstreak[0]['data']['actor']['playerId']
                if player_id in player_id_to_name_map_match_11:
                    player_number = player_id_to_name_map_match_11[player_id]
                    stream_name = 'P' + player_number

                    stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv, player_number)
                    stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
                    stream_begin_sec = util.timestamp_to_sec(
                        stream_begin_timestamp)  # start position in video in seconds
                    match_begin_timestamp_utc = util.get_datetime_from_utc_string(stream_begin_row[8])  # start of match

                    extract_killstreak(killstreak, 5, nth_kill, stream_begin_row, stream_begin_sec,
                                       match_begin_timestamp_utc,
                                       stream_name)

    # detect 4-Killstreaks
    if os.path.exists(killstreak_dest_video_path + '/4/metadata.json'):
        if debug:
            logger.info("4-Killstreaks for match " + str(
                i) + " already detected and extracted. Delete " + killstreak_dest_video_path + '/4/metadata.json to redetect killstreaks')
    elif 4 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[4]:
            # determine how many kills where performed
            nth_kill = determine_kills(killstreak, all_rounds_data)
            if not player_stream:
                # if player_stream == False extract only P11
                stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv, 11)
                stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
                stream_begin_sec = util.timestamp_to_sec(stream_begin_timestamp)  # start position in video in seconds
                match_begin_timestamp_utc = util.get_datetime_from_utc_string(stream_begin_row[8])  # start of match

                extract_killstreak(killstreak, 4, nth_kill, stream_begin_row, stream_begin_sec,
                                   match_begin_timestamp_utc, 'P11')
            else:
                player_id = killstreak[0]['data']['actor']['playerId']
                if player_id in player_id_to_name_map_match_11:
                    player_number = player_id_to_name_map_match_11[player_id]
                    stream_name = 'P' + player_number

                    stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv, player_number)
                    stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
                    stream_begin_sec = util.timestamp_to_sec(
                        stream_begin_timestamp)  # start position in video in seconds
                    match_begin_timestamp_utc = util.get_datetime_from_utc_string(stream_begin_row[8])  # start of match

                    extract_killstreak(killstreak, 4, nth_kill, stream_begin_row, stream_begin_sec,
                                       match_begin_timestamp_utc,
                                       stream_name)

    # detect 3-Killstreaks
    if os.path.exists(killstreak_dest_video_path + '/3/metadata.json'):
        if debug:
            logger.info("3-Killstreaks for match " + str(
                i) + " already detected and extracted. Delete " + killstreak_dest_video_path + '/3/metadata.json to redetect killstreaks')
    elif 3 in sorted_kill_streak_list:
        for killstreak in sorted_kill_streak_list[3]:
            # determine how many kills where performed
            nth_kill = determine_kills(killstreak, all_rounds_data)
            if not player_stream:
                # if player_stream == False extract only P11
                stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv, 11)
                stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
                stream_begin_sec = util.timestamp_to_sec(stream_begin_timestamp)  # start position in video in seconds
                match_begin_timestamp_utc = util.get_datetime_from_utc_string(stream_begin_row[8])  # start of match

                extract_killstreak(killstreak, 3, nth_kill, stream_begin_row, stream_begin_sec,
                                   match_begin_timestamp_utc, 'P11')
            else:
                player_id = killstreak[0]['data']['actor']['playerId']
                if player_id in player_id_to_name_map_match_11:
                    player_number = player_id_to_name_map_match_11[player_id]
                    stream_name = 'P' + player_number

                    stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv, player_number)
                    stream_begin_timestamp = stream_begin_row[7]  # string timestamp for match_begin
                    stream_begin_sec = util.timestamp_to_sec(
                        stream_begin_timestamp)  # start position in video in seconds
                    match_begin_timestamp_utc = util.get_datetime_from_utc_string(stream_begin_row[8])  # start of match

                    extract_killstreak(killstreak, 3, nth_kill, stream_begin_row, stream_begin_sec,
                                       match_begin_timestamp_utc,
                                       stream_name)


def extract_last_round(score_map, all_rounds_data, match, player_stream):
    last_score_list = [score_map[len(score_map) - 2][entry]['score'] for entry in score_map[len(score_map) - 2]]
    target_round_data = all_rounds_data[len(score_map)]
    target_round_actor = target_round_data['kill'][-1]['data']['actor']['playerId']

    stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv, int(player_stream.replace('P', '')))
    match_begin_sec = int(stream_begin_row[1])
    round_potential_begin_sec = match_begin_sec + int(stream_begin_row[2]) - 1500
    round_potential_end_sec = match_begin_sec + int(stream_begin_row[2])

    video_full_name = src_video_path + '/' + stream_begin_row[6]

    round_begin_sec = round_detector.get_round_begin(round_potential_begin_sec,
                                                     round_potential_end_sec,
                                                     video_full_name,
                                                     last_score_list[0], last_score_list[1], player_stream=player_stream)
    nth_kill = len(target_round_data['kill']) - 1

    last_kill_second = kill_detector.get_nth_kill_sec(round_begin_sec + search_kill_offset_sec_before,
                                                    round_begin_sec + 200,
                                                    video_full_name, nth_kill, player_stream=player_stream)

    dest_video_name = last_round_dest_video_path + '/last_round_match_' + str(match) + '_' + player_stream + '.mp4'
    duration = 50
    start_sec = last_kill_second - 30

    add_lastround_to_list(match, dest_video_name, duration, '', start_sec, target_round_actor, player_stream)

    util.cut_video_within_boundaries(video_full_name, start_sec, duration,
                                     dest_video_name)


#########################################################
# create dest. video folders if not exists
for j in range(3, 6):
    for k in range(1, 12):
        if not os.path.exists(killstreak_dest_video_path + '/' + str(j) + '/P' + str(k)):
            os.makedirs(killstreak_dest_video_path + '/' + str(j) + '/P' + str(k))

if not os.path.exists(last_round_dest_video_path):
    os.makedirs(last_round_dest_video_path)

print(kill_detector.skully)
#
metadata_csv = util.read_metadata_csv()

if detect_killstreaks:
    round_detector = round_detector.RoundDetector()
    logger.info('Start extracting killstreaks')
    # iterate over all 11 matches from 1.json - 11.json
    for i in range(11, 12):
        # 10.json is not correct!
        if i != 10:
            json_file = open(base_dir + '/timelines/' + str(i) + '.json')
            all_rounds_data = TimelineReader.preprocess(json.load(json_file))

            score_map = TimelineReader.get_score_map_for_match(
                all_rounds_data)  # keeps track of the total score for each round

            kill_streak_list = TimelineReader.get_kill_streak_list(all_rounds_data)
            sorted_kill_streak_list = TimelineReader.sort_kill_streaks(
                kill_streak_list)  # Sorted by highest KillStreakLength desc

            # extract all 5, 4, 3 killstreaks
            extract_all_killstreaks(all_rounds_data, sorted_kill_streak_list, match=i)  # from P11-Stream
            extract_all_killstreaks(all_rounds_data, sorted_kill_streak_list, match=i,
                                    player_stream=True)  # from Player-Streams

    # extract last rounds of match
    if extract_last_rounds:
        json_file = open(base_dir + '/timelines/11.json')
        all_rounds_data = TimelineReader.preprocess(json.load(json_file))
        score_map = TimelineReader.get_score_map_for_match(all_rounds_data)

        # for event stream
        extract_last_round(score_map, all_rounds_data, 11, 'P11')

        #and player stream
        target_player_stream = 'P' + player_id_to_name_map_match_11[all_rounds_data[len(score_map)]['kill'][-1]['data']['actor']['playerId']]
        extract_last_round(score_map, all_rounds_data, 11, target_player_stream)

    [log_killstreak_to_file(i) for i in range(3, 6)]

if extract_shows:
    logger.info('Start extracting shows')
    show_extractor.extract_shows(metadata_csv, src_video_path, shows_dest_video_path)

if extract_highlights:
    logger.info('Start extracting highlights')
    highlight_extractor.extract_highlights(metadata_csv, src_video_path, highlight_dest_video_path)

if summarize_video:
    collage.summarize_all()
