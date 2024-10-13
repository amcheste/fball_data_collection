import argparse
import json
import time
from datetime import datetime
import pandas as pd
import requests

def process_args():
    parser = argparse.ArgumentParser(
        prog='nfl_data.py',
        description='What the program does',
        epilog='Text at the bottom of help'
    )

    # TODO: Fill out help etc
    parser.add_argument('command', type=str)
    parser.add_argument('--type')
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--filename', type=str)
    parser.add_argument('--task_id', type=str)
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
    valid_commands = ['discover','collect', 'export', 'status']
    if args.command.lower() not in valid_commands:
        raise ValueError('Command must be "collect" or "export"')
    # TODO constants
    if args.type is not None:
        data_types = ['all', 'positions', 'teams', 'players', 'games']
        if args.type.lower() not in data_types:
            raise ValueError(f"Type must be one of {data_types}")

    if args.start is not None and args.end is not None:
        # TODO magic number
        if args.start < 1920:
            raise ValueError('Start must be at least 1920')

        current_year = datetime.now().year
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

def discover(args):
    data = {}
    urls = []
    if args.type.lower() == 'positions':
        urls.append("http://127.0.0.1:8000/nfl_data/v1/positions/")

    elif args.type.lower() == 'teams':
        urls.append("http://127.0.0.1:8000/nfl_data/v1/teams/")
        data = {
            'start': args.start,
            'end': args.end
        }
    elif args.type.lower() == 'players':
        urls.append("http://127.0.0.1:8000/nfl_data/v1/players/")
    elif args.type.lower() == 'all':
        urls = [
            "http://127.0.0.1:8000/nfl_data/v1/positions/",
            "http://127.0.0.1:8000/nfl_data/v1/teams/",
            "http://127.0.0.1:8000/nfl_data/v1/players/"
        ]
        data = {
            'start': args.start,
            'end': args.end
        }
    else:
        raise ValueError(f"Invalid type to discover: {args.type}")

    task_ids = []
    for url in urls:
        response = requests.post(url, data=json.dumps(data))
        if response.status_code != 201:
            raise RuntimeError(f"Failed to start discovery of {args.type}")
        task_ids.append(response.json()['id'])
        print_task(response.json())
        print("")

    if args.wait:
        found = False
        for i in range(0,5000):
            complete = True # TODO could we do coroutines here?
            for id in task_ids:
                url = f"http://127.0.0.1:8000/nfl_data/v1/tasks/{id}"
                response = requests.get(url)
                if response.status_code != 200:
                    # Exception
                    pass

                if response.json()['status'] != 'COMPLETED':
                    complete = False
            if complete:
                print("Discovery task(s) completed")
                found = True
                break
            time.sleep(1)
        if not found:
            raise RuntimeError(f"Failed to wait for discovery tasks to complete")

def collect(args):
    url = "http://127.0.0.1:8000/nfl_data/v1/tasks/"
    tasks = []

    if args.type.lower() == 'positions':
        tasks.append({
            "command": "collect",
            "data_type": "positions"
        })
    elif args.type.lower() == 'teams':
        tasks.append({
            "command": "collect",
            "data_type": "teams"
        })
    elif args.type.lower() == 'players':
        tasks.append({
            'command': 'collect',
            'data_type': 'players'
        })
    elif args.type.lower() == 'all':
        tasks = [
            {
                "command": "collect",
                "data_type": "positions"
            },
            {
                "command": "collect",
                "data_type": "teams"
            },
            {
                "command": "collect",
                "data_type": "players"
            }
        ]
    else:
        raise ValueError(f"Invalid type to collect: {args.type}")
    task_ids = []
    for task in tasks:
        response = requests.post(url, data=json.dumps(task))
        if response.status_code != 201:
            raise RuntimeError(f"Failed to start discovery of {args.type}")
        task_ids.append(response.json()['id'])
        print_task(response.json())
        print("")

    if args.wait:
        found = False
        for i in range(0,6400):
            complete = True
            for id in task_ids:
                url = f"http://127.0.0.1:8000/nfl_data/v1/tasks/{id}"
                response = requests.get(url)
                if response.status_code != 200:
                    # Exception
                    pass

                if response.json()['status'] != 'COMPLETED':
                    complete = False
            if complete:
                print("Discovery task(s) completed")
                found = True
                break
            time.sleep(1)
        if not found:
            raise RuntimeError(f"Failed to wait for collect tasks to complete")


def main():
    args = process_args()

    if args.command.lower() == 'discover':
        discover(args)
    elif args.command.lower() == 'collect':
        collect(args)
    elif args.command.lower() == 'status':
        #TODO get task status
        url = f"http://127.0.0.1:8000/nfl_data/v1/tasks/{args.task_id}"
        response = requests.get(url)
        print_task(response.json())
            #TODO: add verbose mode
    elif args.command.lower() == 'export':
        if args.type.lower() == 'positions':
            url = "http://127.0.0.1:8000/nfl_data/v1/positions/"
        elif args.type.lower() == 'teams':
            url = "http://127.0.0.1:8000/nfl_data/v1/teams/"
        elif args.type.lower() == 'players':
            url = "http://127.0.0.1:8000/nfl_data/v1/players/"
        else:
            raise ValueError("Invalid type")

        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to export {args.type} data")

        data = response.json()
        df = pd.DataFrame(data)
        df = df.set_index("id")
        df.to_csv(args.filename)

    else:
        pass


if __name__ == '__main__':
    main()