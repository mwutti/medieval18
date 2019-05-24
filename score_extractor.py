import util.detection_utils as util
import round_detector
import TimelineReader
import os
import csv
import json
import inspect

base_dir = os.path.dirname(os.path.abspath(inspect.stack()[0][1]))
output_dir = "scores/"

metadata_csv = util.read_metadata_csv()
round_detector = round_detector.RoundDetector()
print('hello')
with open(output_dir + 'scores.csv', mode='w', newline='') as scores_file:
    scores_writer = csv.writer(scores_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    scores_writer.writerow(['match', 'round', 'ct', 'terrorists'])

    for i in range(1, 12):
        # 10.json is not correct!
        if i != 10:
            json_file = open(base_dir + '/timelines/' + str(i) + '.json')
            all_rounds_data = TimelineReader.preprocess(json.load(json_file))
            score_map = TimelineReader.get_score_map_for_match(all_rounds_data)

            roundNr = 0
            scoreCT, scoreTerrorist = 0, 0

            for score in score_map:
                roundNr += 1
                for entry in score:
                    if score[entry]['ingameTeam'] == 'CT':
                        scoreCT = score[entry]['score']
                    else:
                        scoreTerrorist = score[entry]['score']

                scores_writer.writerow([i, roundNr, scoreCT, scoreTerrorist])
