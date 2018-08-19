import TimelineReader
import json
from datetime import datetime
# 9 5-Killstreaks total
# 17 4-Killstreaks total

nr5killz = 0
nr4killz = 0

for i in range(1, 12):
    json_file = open('timelines/' + str(i) + '.json')
    all_rounds_data = TimelineReader.preprocess(json.load(json_file))
    kill_streak_list = TimelineReader.get_kill_streak_list(all_rounds_data)

    # Sorted by highest KillStreakLength desc
    sorted_kill_streak_list = TimelineReader.sort_kill_streaks(kill_streak_list)
    if 5 in sorted_kill_streak_list:
        nr5killz += len(sorted_kill_streak_list[5])
        print('5-killStreaks for match ' + str(i))
        for killstreak in sorted_kill_streak_list[5]:
            #Killlstreak begin in UTC .... get rid of +00:00 UTC timezone and T-Letter
            begin_utc_string = killstreak[0]['date'].split('+')[0].replace('T', ' ')
            end_utc_string = killstreak[4]['date'].split('+')[0].replace('T', ' ')

            begin_utc_time = datetime.strptime(begin_utc_string, "%Y-%m-%d %H:%M:%S.%f")
            end_utc_time = datetime.strptime(end_utc_string, "%Y-%m-%d %H:%M:%S.%f")

            print('Killstreak from ' + begin_utc_string + ' util ' + end_utc_string)
            print('killstreak time:' + str(end_utc_time - begin_utc_time))


    if 4 in sorted_kill_streak_list:
        nr4killz += len(sorted_kill_streak_list[4])

print(nr5killz)
print(nr4killz)

