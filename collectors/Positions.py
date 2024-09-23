import psycopg
import requests
from models import Position

def get_positions():
    url = "http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/positions"
    positions = []
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to get first page of positions")
        # TODO exception

    for item in response.json().get("items"):
        position = get_position(item['$ref'])
        if position is not None:
            positions.append(position)
            try:
                position.save()
                print(f"Added position {position.name}")
            except psycopg.errors.UniqueViolation:
                continue


    page_count = response.json().get("pageCount")
    page = response.json().get("pageIndex")
    while page < page_count:
        response = requests.get(f"{url}?page={page+1}")
        if response.status_code != 200:
            print(f"Failed to get page number {page} of positions") #TODO logger?
            #TODO: Exception

        for item in response.json().get("items"):

            position = get_position(item['$ref'])
            if position is not None:

                positions.append(position)
                try:
                    position.save()
                    print(f"Added position {position.name}")
                except psycopg.errors.UniqueViolation:
                    continue
        page = page + 1

    return positions

def get_position(position_url: str) -> Position | None:
    response = requests.get(position_url)

    if response.status_code != 200:
        print(f"Failed to get position {position_url}")
        # TODO: Exception
    data = response.json()
    if data['leaf']:
        return Position(id=data['id'], name=data['name'], abbreviation=data['abbreviation'])
    else:
        return None

