import psycopg
import requests

from models import Team
from utils.database import connect
# TODO factory
class Teams():
    def __init__(self):
        self.__teams = []

    def get_data(self, start: int, end: int) -> list[Team]:
        self.__teams = get_teams(start, end)

        return self.__teams

    def export(self, dest: str):
        #TODO
        pass

def get_team(team_url: str) -> Team:
    response = requests.get(team_url)
    if response.status_code != 200:
        print(f"Failed to get position {team_url}")
        # TODO: Exception
    data = response.json()

    team = Team(
        id=data['id'],
        name=data['displayName'],
        location=data['location'],
        abbreviation=data['abbreviation']
    )

    return team

def get_teams(start: int, end: int) -> list[Team]:
    teams = {}
    year = start
    # TODO: Can we check if exists before trying to get / write?
    while year < end:
        url = f"http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/{year}/teams/"
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to get first page of positions")
            # TODO exception

        for item in response.json().get("items"):
            team = get_team(item['$ref'])
            teams[team.id] = team
            try:
                team.save()
                print(f"Saved team {team.name}")
            except psycopg.errors.UniqueViolation:
                continue


        page_count = response.json().get("pageCount")
        page = response.json().get("pageIndex")

        while page < page_count:
            response = requests.get(f"{url}?page={page + 1}")
            if response.status_code != 200:
                print(f"Failed to get page number {page} of positions")  # TODO logger?
                # TODO: Exception

            for item in response.json().get("items"):
                team = get_team(item['$ref'])
                teams[team.id] = team
                try:
                    team.save()
                    print(f"Saved team {team.name}")
                except psycopg.errors.UniqueViolation:
                    continue
            page = page + 1

        year = year+1

    return teams



