import argparse
import asyncio
import datetime
import json
from halo import Halo

import pandas as pd
import requests


def process_args():
    parser = argparse.ArgumentParser(
        prog='nfl_data.py',
        description='What the program does',
        epilog='Text at the bottom of help'
    )

    # TODO: Fill out help etc
    parser.add_argument('command', type=str, choices=['all', 'discover', 'collect', 'export', 'status'])
    parser.add_argument('--data_type', type=str, required=True, choices=['all','positions','teams','games','players'])
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--dest', type=str)
    #parser.add_argument('--task_id', type=str)
    parser.add_argument("--wait",action='store_true' )
    args = parser.parse_args()

    try:
        validate_args(args)
    except ValueError as e:
        print(e)
        parser.print_help()
        raise ValueError

    return args

def validate_args(args):
    print(args)
    if args.start is not None and args.end is not None:
        # TODO magic number
        if args.start < 1920:
            raise ValueError('Start must be at least 1920')

        current_year = datetime.datetime.now().year
        if args.end > current_year:
            raise ValueError('End must be less than current year')

        if args.start > args.end:
            raise ValueError('Start date must be before end date')

def print_task(task: dict):
    print(f"\t        Task ID: {task['id']}")
    print(f"\t    Task Status: {task['status']}")
    print(f"\t      Task Type: {task['command']}")
    print(f"\t      Data Type: {task['data_type']}")
    print(f"\t   Time Created: {task['time_created']}")
    print(f"\t  Time Modified: {task['time_modified']}")
    if 'open_steps' in task and 'total_steps' in task and task['total_steps'] > 0:
        print(f"\tRemaining Steps: {task['open_steps']} of {task['total_steps']}")

def create_task(command: str, data_type: str):
    url = "http://127.0.0.1:8000/nfl_data/v1/tasks/"
    task = {
        "command": command,
        "data_type": data_type,
    }
    response = requests.post(url, data=json.dumps(task))
    if response.status_code != 201:
        raise RuntimeError(f"Failed to start discovery of {data_type}")

    return response.json()['id']

async def wait_on_task(id: str):
    found = False
    for i in range(0, 6400):
        url = f"http://127.0.0.1:8000/nfl_data/v1/tasks/{id}"
        response = requests.get(url)
        # if response.status_code != 200:
        # # Exception
        #                    pass
        if response.json()['status'] == 'COMPLETED':
            found = True
            break
        await asyncio.sleep(1)

    if not found:
        raise RuntimeError(f"Failed to wait for collect tasks to complete")

async def discover(type: str, start=None, end=None, wait=False):
    data = {}
    if type == 'positions':
        url = "http://127.0.0.1:8000/nfl_data/v1/positions/"
    elif type == 'teams':
        url = "http://127.0.0.1:8000/nfl_data/v1/teams/"
        data = {
            'start': start,
            'end': end
        }
    elif type == 'games':
        url = "http://127.0.0.1:8000/nfl_data/v1/games/"
        data = {
            'start': start,
            'end': end
        }
    elif type == 'players':
        url = "http://127.0.0.1:8000/nfl_data/v1/players/"
    else:
        raise ValueError(f"Invalid type to discover: {type}")

    response = requests.post(url, data=json.dumps(data))
    if response.status_code != 201:
        raise RuntimeError(f"Failed to start discovery of {type}")
    #print_task(response.json())
    #print("")

    id = response.json()['id']
    if wait:
        await wait_on_task(id)

async def collect(data_type:str, wait=False):
    id = create_task(command='collect', data_type=data_type)

    if wait:
        await wait_on_task(id)

async def export(data_type: str, dest: str):
    base_url = 'http://127.0.0.1:8000/nfl_data/v1'

    response = requests.get(f"{base_url}/{data_type}/")
    if response.status_code != 200:
        raise RuntimeError(f"Failed to export {data_type} data")#

    data = response.json()
    df = pd.DataFrame(data)
    df = df.set_index("id")
    df.to_csv(f'{dest}/{data_type}.csv')

    if data_type == 'teams' or data_type == 'all':
        response = requests.get(f"{base_url}/team_stats/")
        if response.status_code != 200:
            raise RuntimeError(f"Failed to export player stat data")
        data = response.json()
        df = pd.DataFrame(data)
        df = df.set_index("id")
        df.to_csv(f'{dest}/team_stats.csv')

    if data_type == 'games' or data_type == 'all':
        response = requests.get(f"{base_url}/game_stats/")
        if response.status_code != 200:
            raise RuntimeError(f"Failed to export game stat data")
        data = response.json()
        df = pd.DataFrame(data)
        df = df.set_index("id")
        df.to_csv(f'{dest}/game_stats.csv')

    if data_type == 'players' or data_type == 'all':
        response = requests.get(f"{base_url}/player_stats/")
        if response.status_code != 200:
            raise RuntimeError(f"Failed to export player stast data")

        data = response.json()
        df = pd.DataFrame(data)
        df = df.set_index("id")
        df.to_csv(f'{dest}/player_stats.csv')


# TODO simplify?
async def positions(command:str, dest = None, wait=False):
    if command == 'discover' or command == 'all':
        spinner = Halo(f"\nDiscovering positions")
        spinner.start(f"\rDiscovering positions")
        await discover(type='positions', wait=wait)
        spinner.succeed("\nDiscovered positions")

    if command == 'collect' or command == 'all':
        spinner = Halo(f"\nCollecting position data")
        spinner.start(f"\rCollecting position data")
        await collect(data_type='positions', wait=wait)
        spinner.succeed("\nCollected position data")

    if command == 'export' or command == 'all':
        spinner = Halo(f"\nExporting position data")
        spinner.start(f"\rExporting position data")
        await export(data_type='positions', dest=dest)
        spinner.succeed("\nExported position data")

async def teams(command:str, start: str, end: str, dest=None, wait=False):
    if command == 'discover' or command == 'all':
        spinner = Halo(f"\nDiscovering teams")
        spinner.start(f"\rDiscovering teams")
        await discover(type='teams', start=start, end=end, wait=wait)
        spinner.succeed("\nDiscovered teams")

    if command == 'collect' or command == 'all':
        spinner = Halo(f"\nCollecting team data")
        spinner.start(f"\rCollecting team data")
        await collect(data_type='teams', wait=wait)
        spinner.succeed("\nCollected team data")

    if command == 'export' or command == 'all':
        spinner = Halo(f"\nExporting team data")
        spinner.start(f"\rExporting team data")
        await export(data_type='teams', dest=dest)
        spinner.succeed("\nExported team data")

async def games(command:str, start: str, end: str, dest=None, wait=False):
    if command == 'discover' or command == 'all':
        spinner = Halo(f"\nDiscovering games")
        spinner.start(f"\rDiscovering games")
        await discover(type='games', start=start, end=end, wait=wait)
        spinner.succeed("\nDiscovered games")

    if command == 'collect' or command == 'all':
        spinner = Halo(f"\nCollecting game data")
        spinner.start(f"\rCollecting game data")
        await collect(data_type='games', wait=wait)
        spinner.succeed("\nCollected game data")

    if command == 'export' or command == 'all':
        spinner = Halo(f"\nExporting game data")
        spinner.start(f"\rExporting game data")
        await export(data_type='games', dest=dest)
        spinner.succeed("\nExported game data")

async def players(command:str, dest=None, wait=False):
    if command == 'discover' or command == 'all':
        spinner = Halo(f"\nDiscovering players")
        spinner.start(f"\rDiscovering players")
        await discover(type='players', wait=wait)
        spinner.succeed("Discovered players\n")

    if command == 'collect' or command == 'all':
        spinner = Halo(f"\nCollecting player data")
        spinner.start(f"\rCollecting player data")
        await collect(data_type='players', wait=wait)
        spinner.succeed("\nCollected player data")

    if command == 'export' or command == 'all':
        spinner = Halo(f"\nExporting player data")
        spinner.start(f"\rExporting player data")
        await export(data_type='players', dest=dest)
        spinner.succeed("\nExported player data")


async def main():
    args = process_args()

    if args.data_type.lower() == 'positions':
        await positions(command=args.command, dest=args.dest, wait=args.wait)
    elif args.data_type.lower() == 'teams':
        await teams(command=args.command, start=args.start, end=args.end, dest=args.dest, wait=args.wait)
    elif args.data_type.lower() == 'games':
        await games(command=args.command, start=args.start, end=args.end, dest=args.dest, wait=args.wait)
    elif args.data_type.lower() == 'players':
        await players(command=args.command, dest=args.dest, wait=args.wait)
    elif args.data_type.lower() == 'all':
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                positions(command=args.command, dest=args.dest, wait=args.wait)
            )
            tg.create_task(
                teams(command=args.command, start=args.start, end=args.end, dest=args.dest, wait=args.wait)
            )
            tg.create_task(
                games(command=args.command, start=args.start, end=args.end, dest=args.dest, wait=args.wait)
            )
            tg.create_task(
                players(command=args.command, dest=args.dest, wait=args.wait)
            )
    else:
        pass



if __name__ == '__main__':
    asyncio.run(main())