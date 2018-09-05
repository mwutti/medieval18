import csv
from datetime import datetime


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


def get_datetime_from_utc_string(string):
    filteredString = string.split('+')[0].replace('T', ' ')
    if filteredString.find('.') == -1:
        return datetime.strptime(filteredString, "%Y-%m-%d %H:%M:%S")
    else:
        return datetime.strptime(filteredString, "%Y-%m-%d %H:%M:%S.%f")


# returns the row in metadata where the match with nr matchnr starts for player with id playerId
def get_match_begin_in_player_stream(matchnr, metadata, player_id):
    for entry in metadata:
        if entry[3] == 'match' and entry[4] == str(matchnr) and entry[5] == 'P' + str(player_id):
            return entry
