import json

# Preprocessing of json data
def preprocess(data):
    result = {}
    for event in data:
        round_id = event['roundIdx']
        if round_id not in result:
            result[round_id] = {}

        event_type = event['type']
        if event_type not in result[round_id]:
            result[round_id][event_type] = []

        result[round_id][event_type].append(event)
    return result


# return a KillStreamList
def get_kill_streak_list(all_rounds_data):
    result = {}
    for round in all_rounds_data:
        result[round] = {}
        for kill in all_rounds_data[round]['kill']:
            player_id = kill['data']['actor']['playerId']
            if player_id not in result[round]:
                result[round][player_id] = []
            result[round][player_id].append(kill)
    return result

def get_score_map(all_rounds_data):
    result = {}

    result[1] = [0, 0] # counter terrorists vs terrorists
    for round in all_rounds_data:
        result[round + 1] = [i for i in result[round]]

        winning_team = all_rounds_data[round]['round_end'][0]['data']['ingameTeam']
        if winning_team == 'CT':
            result[round + 1][0] = result[round + 1][0] + 1
        else:
            result[round + 1][1] = result[round + 1][1] + 1

    return result

def sort_kill_streaks(kill_streak_list):
    result = {}
    for round in kill_streak_list:
        for player_id in kill_streak_list[round]:
            kill_streak_length = len(kill_streak_list[round][player_id])
            if kill_streak_length not in result:
                result[kill_streak_length] = []
            result[kill_streak_length].append(kill_streak_list[round][player_id])
    return result


for i in range(1, 12):
    json_file = open('timelines/' + str(i) + '.json')
    all_rounds_data = preprocess(json.load(json_file))
    kill_streak_list = get_kill_streak_list(all_rounds_data)

    # Sorted by highest KillStreakLength desc
    sorted_kill_streak_list = sort_kill_streaks(kill_streak_list)

    # write json file
    with open('data/killstreaks/killstreaks_' + str(i) + '.json', 'w') as file:
        json.dump(sorted_kill_streak_list, file)
