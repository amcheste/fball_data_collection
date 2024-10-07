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
    parser.add_argument('--type', required=True)
    parser.add_argument('--start', type=int)
    parser.add_argument('--end', type=int)
    parser.add_argument('--filename', type=str)
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
    # TODO constant, all/status?
    valid_commands = ['discover','collect', 'export']
    if args.command.lower() not in valid_commands:
        raise ValueError('Command must be "collect" or "export"')
    # TODO constants
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

        print(f"Discovered {response.json()} new {args.type}")

    elif args.command.lower() == 'collect':
        if args.type.lower() == 'positions':
            pending_url = "http://127.0.0.1:8000/nfl_data/v1/positions/pending"
            total_url = "http://127.0.0.1:8000/nfl_data/v1/positions"
        elif args.type.lower() == 'teams':
            pending_url = "http://127.0.0.1:8000/nfl_data/v1/teams/pending"
            total_url = "http://127.0.0.1:8000/nfl_data/v1/teams"
        elif args.type.lower() == 'players':
            pending_url = "http://127.0.0.1:8000/nfl_data/v1/players/pending"
            total_url = "http://127.0.0.1:8000/nfl_data/v1/players"
        else:
            raise ValueError(f"Invalid type to collect: {args.type}")

        response = requests.get(pending_url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to get the number of pending {args.type}")
        pending = response.json()

        response = requests.get(total_url)
        if response.status_code != 200:
            raise RuntimeError(f"Failed to get the toal number of {args.type}")
        total = len(response.json())

        print(f"{total-pending} of {total} {args.type} have been collected")
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