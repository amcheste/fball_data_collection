def get_active_players():
    url = "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes?limit=1000&active=true"
    players = []

    response = requests.get(f"{url}&page=1")
    if response.status_code != 200:
        print("Failed to get first page of active athletes")
        sys.exit(255)

    for player in response.json().get("items"):
        players.append(player)


    page_count = response.json().get("pageCount")
    page = response.json().get("pageIndex")
    while page < page_count:
        response = requests.get(f"{url}&page={page+1}")
        if response.status_code != 200:
            print(f"Failed to get page number {page} of active athletes")
            sys.exit(255)
        for player in response.json().get("items"):
            players.append(player)
        page = page + 1

    return players

    #players = get_active_players()
    #print(len(players))
    #print(players[0]['$ref'])
    #response = requests.get("http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes/4429202?lang=en&region=us")
    #tmp = response.json()

    #player = {
    #    'id': tmp['id'],
    #    'age': tmp['age'],
    #    'team': tmp['team'], #"$ref": http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/teams/20?lang=en&region=us"
    #    'weight': tmp['weight'],
    #    'height': tmp['height'],
    #    'jersey': tmp['jersey'],
    #    'first_name': tmp['firstName'],
    #    'last_name': tmp['lastName'],
    #    'position': tmp['position']['id'], #9
    #    'experience': tmp['experience']['years'],
    #    'active': tmp['active'],
    #    'statisticslog': tmp['statisticslog'] #"http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/athletes/4429202/statisticslog?lang=en&region=us"
    #}


def get_player(player_url):
    pass