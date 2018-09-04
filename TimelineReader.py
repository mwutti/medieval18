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
    # CT vs Terrorists
    ct_at_0 = True # Flag that indicates that CT score is stored at array pos. 0
    result = {1: [0, 0]}

    for round in all_rounds_data:
        result[round + 1] = [i for i in result[round]]

        # every 15 rounds the teams switch roles CT <->Terrorists
        if (round - 1) % 15 == 0 and not round == 1:
            if result[round][0] == 15 and result[round][1] == 15:
                print('Overtime detected at round:' + str(round))
            else:
                print('switching teams at: ' + str(round))
                ct_at_0 = not ct_at_0

        # if all_rounds_data[round]['round_end'] contains more than one entry, the round was repeated-
        # than take the last entry
        round_end_len = len(all_rounds_data[round]['round_end'])
        if round_end_len != 1:
            print('round repeated')
            winning_team = all_rounds_data[round]['round_end'][round_end_len - 1]['data']['ingameTeam']
        else:
            winning_team = all_rounds_data[round]['round_end'][0]['data']['ingameTeam']

        if ct_at_0:
            if winning_team == 'CT':
                result[round + 1][0] = result[round + 1][0] + 1
            else:
                result[round + 1][1] = result[round + 1][1] + 1
        else:
            if winning_team == 'CT':
                result[round + 1][1] = result[round + 1][1] + 1
            else:
                result[round + 1][0] = result[round + 1][0] + 1

    return result


def get_score_map_for_match(all_rounds_data):
    teams = []
    result = []
    for i in all_rounds_data:
        result.append({})

        round_start_len = len(all_rounds_data[i]['round_start'])
        round_end_len = len(all_rounds_data[i]['round_end'])

        teams_for_round = all_rounds_data[i]['round_start'][round_start_len - 1]['data']['teams']

        # first round... initialize context
        if i == 1:
            team_id_a = teams_for_round[0]['id'] #  TODO overtime comment
            teams.append(team_id_a)
            ingame_team_a = teams_for_round[0]['ingameTeam']
            result[i - 1][team_id_a] = {'score': 0, 'ingameTeam': ingame_team_a}

            team_id_b = teams_for_round[1]['id'] #  TODO overtime comment
            teams.append(team_id_b)
            ingame_team_b = teams_for_round[1]['ingameTeam']
            result[i -1][team_id_b] = {'score': 0, 'ingameTeam': ingame_team_b}
        else:   #scores must be copied from last round
            result[i - 1][team_id_a] = {'score': result[i - 2][team_id_a]['score']}
            result[i - 1][team_id_b] = {'score': result[i - 2][team_id_b]['score']}

        # at round end detect the winning team and add the score to the corresponding team
        round_winner_id = all_rounds_data[i]['round_end'][round_end_len - 1]['data']['teamId']
        round_winner_ingame_team = all_rounds_data[i]['round_end'][round_end_len - 1]['data']['ingameTeam']

        result[i - 1][round_winner_id]['score'] += 1
        result[i - 1][round_winner_id]['IngameTeam'] = round_winner_ingame_team
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
