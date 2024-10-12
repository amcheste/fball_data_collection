import argparse
import json
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


def main():
    args = process_args()

    if args.command.lower() == 'discover':
        # TODO: Functions
        if args.type.lower() == 'positions':
            url = "http://127.0.0.1:8000/nfl_data/v1/positions/"
            data = {}
        elif args.type.lower() == 'teams':
            url = "http://127.0.0.1:8000/nfl_data/v1/teams/"
            data = {
                'start': args.start,
                'end': args.end
            }
        elif args.type.lower() == 'players':
            url = "http://127.0.0.1:8000/nfl_data/v1/players/"
            data = {
                'start': args.start,
                'end': args.end
            }
        else:
            raise ValueError(f"Invalid type to discover: {args.type}")

        response = requests.post(url, data=json.dumps(data))
        if response.status_code != 201:
            print(response.status_code)
            print(response.json())
            raise RuntimeError(f"Failed to start discovery of {args.type}")

        print(f"\t       Task ID: {response.json()['id']}")
        print(f"\t   Task Status: {response.json()['status']}")
        print(f"\t  Time Created: {response.json()['time_created']}")

    elif args.command.lower() == 'collect':
        url = "http://127.0.0.1:8000/nfl_data/v1/tasks/"
        if args.type.lower() == 'positions':
            data = {
                "command": "collect",
                "data_type": "positions"
            }
        elif args.type.lower() == 'teams':
            data = {
                "command": "collect",
                "data_type": "teams"
            }
        elif args.type.lower() == 'players':
            pending_url = "http://127.0.0.1:8000/nfl_data/v1/players/pending"
            total_url = "http://127.0.0.1:8000/nfl_data/v1/players"
        else:
            raise ValueError(f"Invalid type to collect: {args.type}")

        response = requests.post(url, data=json.dumps(data))
        if response.status_code != 201:
            print(response.status_code)
            print(response.json())
            raise RuntimeError(f"Failed to start discovery of {args.type}")

        print(f"\t       Task ID: {response.json()['id']}")
        print(f"\t   Task Status: {response.json()['status']}")
        print(f"\t  Time Created: {response.json()['time_created']}")

    elif args.command.lower() == 'status':
        #TODO get task status
        url = f"http://127.0.0.1:8000/nfl_data/v1/tasks/{args.task_id}"
        response = requests.get(url)

        print(f"\t        Task ID: {response.json()['id']}")
        print(f"\t    Task Status: {response.json()['status']}")
        print(f"\t   Time Created: {response.json()['time_created']}")
        print(f"\t  Time Modified: {response.json()['time_modified']}")
        if 'open_steps' in response.json() and 'total_steps' in response.json():
            print(f"\tRemaining Steps: {response.json()['open_steps']} of {response.json()['total_steps']}")
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