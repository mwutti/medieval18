import csv


class VideoSequence:
    def __init__(self, id, start_time, duration, type, match_id, perspective, stream_file, stream_timestamp,
                 utc_timestamp):
        self.id = id
        self.start_time = start_time
        self.duration = duration
        self.type = type
        self.match_id = match_id
        self.perspective = perspective
        self.stream_file = stream_file
        self.stream_timestamp = stream_timestamp
        self.utc_timestamp = utc_timestamp


def timestamp_to_sec(timestamp):
    split_timestamp = timestamp.split(':')
    stream_timestamp_sec = int(split_timestamp[0]) * 3600 + int(split_timestamp[1]) * 60 + int(split_timestamp[2])
    return stream_timestamp_sec


def sec_to_timestamp(sec):
    seconds = sec % 60
    minutes = sec // 60
    hours = 0
    if minutes > 60:
        hours = minutes // 60
        minutes = minutes % 60
    return str(hours) + ':' + str(minutes) + ':' + str(seconds)


header_row = {}
matches = {}

with open('data/metadata.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    # separate between different different matches
    line = 0
    for row in reader:
        if line > 0:
            # sequence = VideoSequence(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            # videoSequences.append(sequence)
            stream_file = row[6].split('_')[0]
            if stream_file not in matches:
                matches[stream_file] = []

            matches[stream_file].append(row)
        else:
            line = line + 1
            header_row = row

# At this point there is a list of rows for each match in matches

# lowest timestamp in stream file
lowest_timestamp_sec = 360000
highest_timestamp_sec = 0
lowest_timestamp_row = ''
highest_timestamp_row = ''
for match in matches:
    for row in matches[match]:
        # find lowest timestamp in p11 stream
        if row[5] == 'P11':
            stream_timestamp_sec = timestamp_to_sec(row[7])

            if stream_timestamp_sec < lowest_timestamp_sec:
                lowest_timestamp_sec = stream_timestamp_sec
                lowest_timestamp_row = row

            if stream_timestamp_sec > highest_timestamp_sec:
                highest_timestamp_sec = stream_timestamp_sec
                highest_timestamp_row = row

            # find match start
            if row[3] == 'match_start':
                match_start = row[7]
                print('start for match ' + match + " @" + match_start)
    print('lowest timestampt for match ' + match + ' ' + str(lowest_timestamp_sec) + ", " + sec_to_timestamp(lowest_timestamp_sec))
    print(lowest_timestamp_row)
    print("---")
    print('highest timestampt for match ' + match + ' ' + str(highest_timestamp_sec) + ", " + sec_to_timestamp(highest_timestamp_sec))
    print(highest_timestamp_row)
    print("---match end---")
    lowest_timestamp_sec = 360000
    highest_timestamp_sec = 0

#TODO search for trophies in lowest_timestamp - 20min ; highest_timestamp + 20min in matches
