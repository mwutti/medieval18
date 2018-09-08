import json
import logging as logger
logger.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logger.DEBUG)
import os
import util.detection_utils as util
from operator import itemgetter

killstreak_path = 'D:/gamestory18-data/killstreaks'
dest_path = 'D:/gamestory18-data/final'
killstreak_5_path = os.path.join(killstreak_path, '5')
killstreak_4_path = os.path.join(killstreak_path, '4')
total_duration = 0

def get_map_sorted_by_match():
    result = {}
    temp = {}
    with open(os.path.join(killstreak_5_path, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
        killstreaks = metadata['killstreaks']
        for nr_killstreaks in killstreaks:
            # ignore 3-Killstreaks for now
            if nr_killstreaks != '3':
                for video_name in killstreaks[nr_killstreaks]:
                    streak = killstreaks[nr_killstreaks][video_name]
                    matchNr = streak['match']
                    if int(matchNr) not in temp:
                        temp[int(matchNr)] = []

                    streak['killstreak_nr'] = nr_killstreaks
                    streak['file_name'] = video_name
                    temp[int(matchNr)].append(streak)

    for match_nr in sorted(temp):
        result[match_nr] = sorted(temp[int(match_nr)], key=itemgetter('killstreak_begin_sec'))

    return result


#total duration
if os.path.exists(os.path.join(killstreak_path, '5')):
    with open(os.path.join(killstreak_5_path, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
        for video in metadata['killstreaks']['5']:
            duration = metadata['killstreaks']['5'][video]['duration']
            total_duration += int(duration)

    with open(os.path.join(killstreak_4_path, 'metadata.json'), 'r') as f:
        metadata = json.load(f)
        for video in metadata['killstreaks']['4']:
            duration = metadata['killstreaks']['4'][video]['duration']
            total_duration += int(duration)
    logger.info('total duration: ' + util.sec_to_timestamp(total_duration))

    sorted_by_match_map = get_map_sorted_by_match()

    filenames = []
    print("start")
    for match in sorted_by_match_map:
        for killstreak in sorted_by_match_map[match]:
            filenames.append(os.path.join(killstreak_path, os.path.join(killstreak['killstreak_nr'], killstreak['file_name'])))

    with open(os.path.join(dest_path, "files.txt"), 'w') as file:
        [file.write("file " + "'" + line + "'\n") for line in filenames]
else:
    logger.error("Killstreak path does not exist")





