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


with open('data/metadata.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')

    videoSequences = []
    line = 0
    for row in reader:
        if line > 0:
            sequence = VideoSequence(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
            videoSequences.append(sequence)
        else:
            line = line + 1
    print("unique sequence types: ")
    print({seq.type for seq in videoSequences})
