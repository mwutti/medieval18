import util.detection_utils as util
import round_detector
import TimelineReader
import os
import csv
import json
import inspect

# Comment/uncomment lines to switch between training and test set
base_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
# src_video_path = 'D:/gamestory18-data/train_set'
src_video_path = 'D:/gamestory18-data/test_set'
# output_dir = "synch-points/"
output_dir = "synch-points/test-set/"
# timelines_dir = base_dir + '/timelines/'
timelines_dir = base_dir + '/timelines/test/'

player_stream = 'P1'
match_start = 1
# match_start = 3
# match_end = 3
match_end = 4

# metadata_csv = util.read_metadata_csv()
metadata_csv = util.read_metadata_test_set_csv()
round_detector = round_detector.RoundDetector()


def prepare_testset_csv():
    metadata_columns = ["id", "start_time", "duration", "type", "match_id", "perspective", "stream_file",
                        "stream_timestamp", "UTC_timestamp"]
    metadata = []
    match_id = 0

    for i in range(1, 5):
        json_file = open(base_dir + '/timelines/test/' + str(i) + '.json')
        all_rounds_data = TimelineReader.preprocess(json.load(json_file))
        match_start_utc = all_rounds_data[1]['round_start'][0]['date']
        match_end_utc = match_start_utc

        for round in all_rounds_data:
            match_end_utc = all_rounds_data[round]['round_end'][0]['date']
        match_start_datetime = util.get_datetime_from_utc_string(match_start_utc)
        match_end_datetime = util.get_datetime_from_utc_string(match_end_utc)
        match_duration_datetime = match_end_datetime - match_start_datetime

        # match_duration_sec = util.timestamp_to_sec(match_duration_datetime)

        for P in range(1, 12):
            metadata.append(
                {"id": str(match_id), "start_time": "NONE", "duration": str(match_duration_datetime), "type": "match",
                 "match_id": str(i), "perspective": "P" + str(P), "stream_file": "2018-03-03_P" + str(P) + ".mp4",
                 "stream_timestamp": "NONE", "UTC_timestamp": str(match_start_utc)})
            match_id = match_id + 1

    try:
        with open('test-metadata.csv', mode='w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=metadata_columns)
            writer.writeheader()
            for data in metadata:
                writer.writerow(data)
    except IOError:
        print("I/O error")

    print("finished")


# prepare_testset_csv()

for match in range(match_start, match_end + 1):
    # 10.json is not correct!
    if match != 10:
        with open(output_dir + 'sync_match_' + str(match) + '_' + player_stream + '.csv', 'w', newline='') as file:
            writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['match', 'round', 'round_begin', 'frame_nr'])

        json_file = open(timelines_dir + str(match) + '.json')
        all_rounds_data = TimelineReader.preprocess(json.load(json_file))
        score_map = TimelineReader.get_score_map_for_match(all_rounds_data)

        roundNr = 1
        scoreCT, scoreTerrorist = 0, 0

        for j in range(1, len(score_map) + 1):
            round_start_utc_string = all_rounds_data[roundNr]['round_start'][-1]['date']
            round_start_utc_time = util.get_datetime_from_utc_string(round_start_utc_string)

            stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv,
                                                                     int(player_stream.replace('P', '')))
            match_start_utc_time = util.get_datetime_from_utc_string(stream_begin_row[8])

            stream_begin_timestamp = stream_begin_row[7]
            stream_begin_sec = util.timestamp_to_sec(stream_begin_timestamp)

            difference_between_match_begin_and_round_start = round_start_utc_time - match_start_utc_time

            # print('difference between match begin and round begin: ' + str(
            #     difference_between_match_begin_and_round_start))

            start_pos_in_video_sec = stream_begin_sec + util.timestamp_to_sec(
                str(difference_between_match_begin_and_round_start))

            # print('Start pos in video second' + str(util.sec_to_timestamp(start_pos_in_video_sec)))
            search_round_offset_sec = 60
            end_pos_in_video_sec = start_pos_in_video_sec + 30

            stream_begin_row = util.get_match_begin_in_player_stream(match, metadata_csv,
                                                                     int(player_stream.replace('P', '')))

            video_full_name = src_video_path + '/' + stream_begin_row[6]

            round_begin_sec, fps = round_detector.get_round_sync_point(start_pos_in_video_sec - search_round_offset_sec,
                                                                       end_pos_in_video_sec + search_round_offset_sec,
                                                                       video_full_name, scoreCT, scoreTerrorist,
                                                                       roundNr,
                                                                       player_stream=player_stream)
            if round_begin_sec is None:
                # Switch score numbers
                round_begin_sec, fps = round_detector.get_round_sync_point(
                    start_pos_in_video_sec - search_round_offset_sec,
                    end_pos_in_video_sec + search_round_offset_sec,
                    video_full_name,
                    scoreTerrorist, scoreCT, roundNr, player_stream=player_stream)

            if round_begin_sec is None:
                with open(output_dir + 'sync_match_' + str(match) + '_' + player_stream + '.csv', 'a',
                          newline='') as file:
                    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([match, j, 'None', 'None', 'None'])

            else:
                print('!!!! Found round start of round ' + str(roundNr) + ' at' + str(
                    util.sec_to_timestamp(round_begin_sec)))
                with open(output_dir + 'sync_match_' + str(match) + '_' + player_stream + '.csv', 'a',
                          newline='') as file:
                    writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer.writerow([match, j, str(util.sec_to_timestamp(round_begin_sec)), int(round_begin_sec * fps)])

            roundNr += 1

            for entry in score_map[roundNr - 2]:
                if score_map[roundNr - 2][entry]['ingameTeam'] == 'CT':
                    scoreCT = score_map[roundNr - 2][entry]['score']
                else:
                    scoreTerrorist = score_map[roundNr - 2][entry]['score']
