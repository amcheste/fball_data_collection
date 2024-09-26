import psycopg
import json
import requests

from models import Player

class Players():
    def __init__(self):
        self.__players = []

    def get_data(self, start: int, end: int) -> list[Player]:
        self.__players = get_active_players() # TODO active as an arg?

        return self.__players

    def export(self, dest: str):
        pass

def get_active_players():
    url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes?limit=1000&active=true"
    players = []

    response = requests.get(f"{url}&page=1")
    if response.status_code != 200:
        print("Failed to get first page of active athletes")
        # TODO exception

    for item in response.json().get("items"):
        player = get_player(item['$ref'])
        if player is not None:
            players.append(player)
            try:
                player.save()
                print(f"Added player {player.name}")
            except psycopg.errors.UniqueViolation:
                continue


    page_count = response.json().get("pageCount")
    page = response.json().get("pageIndex")
    while page < page_count:
        response = requests.get(f"{url}&page={page+1}")
        if response.status_code != 200:
            print(f"Failed to get page number {page} of active athletes")
            # TODO exception
        for item in response.json().get("items"):
            player = get_player(item['$ref'])
            if player is not None:
                players.append(player)
                try:
                    player.save()
                    print(f"Added player {player.name}")
                except psycopg.errors.UniqueViolation:
                    continue
        page = page + 1

    return players

def get_player(player_url) -> Player | None:
    response = requests.get(player_url)
    if response.status_code != 200:
        print(f"Failed to get position {player_url}")
        # TODO: Exception
    data = response.json()

    #TODO Const
    FANTASY_POSITIONS = {"1": "QB",
     "2": "RB",
     "3": "WR",
     "4": "TE",
     "5": "K",
     "16": "DST"}
    if data['position']['id'] not in FANTASY_POSITIONS:
        #TODO Debug print("Skipping non fantasy position")
        return None

    tmp = {
        'id': data['id'],
        'name': data['displayName'],
        'height': data['height'],
        'weight': data['weight'],
        'experience': data['experience']['years'],
        'position': data['position']['id'], #ID
        'active': data['active'],
        'status': data['status']['abbreviation'],
    }
    if 'age' in data:
        tmp['age'] = data['age']

    #if 'team' in data:
    #    tmp['team_id'] = data['team'] TODO

    if 'statistics' in data:
        tmp['statistics'] = data['statistics']

    if 'statisticslog' in data:
        tmp['stats_url'] = data['statisticslog']['$ref']

    player = Player(**tmp)

    return player

#{
#    "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes/4429202/statisticslog?lang=en&region=us",
#    "entries": [
#        {
#            "season": {
#                "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024?lang=en&region=us"
#            },
#            "statistics": [
#                {
#                    "type": "total",
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/types/1/athletes/4429202/statistics/0?lang=en&region=us"
#                    }
#                },
#                {
#                    "type": "team",
#                    "team": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/teams/20?lang=en&region=us"
#                    },
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/types/1/teams/20/athletes/4429202/statistics?lang=en&region=us"
#                    }
#                }
#            ]
#        },
#        {
#            "season": {
#                "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023?lang=en&region=us"
#            },
#            "statistics": [
#                {
#                    "type": "total",
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/athletes/4429202/statistics/0?lang=en&region=us"
#                    }
#                },
#                {
#                    "type": "team",
#                    "team": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/teams/20?lang=en&region=us"
#                    },
#                    "statistics": {
#                        "$ref": "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/teams/20/athletes/4429202/statistics?lang=en&region=us"
#                    }
#                }
#            ]
#        }
#    ]
#}



