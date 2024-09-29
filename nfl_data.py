import argparse
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
    #parser.add_argument('--start', required=True, type=int)
    #parser.add_argument('--end', required=True, type=int)
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

    # TODO magic number
    #if args.start < 1920:
    #    raise ValueError('Start must be at least 1920')

    #current_year = datetime.now().year
    #if args.end > current_year:
    #    raise ValueError('End must be less than current year')

    #if args.start > args.end:
        #raise ValueError('Start date must be before end date')


def main():
    args = process_args()

    if args.command.lower() == 'discover':

        #curl - X
        #'POST' \
        #'http://127.0.0.1:8000/nfl_data/v1/positions/' \
        #- H
        #'accept: application/json' \
        #- d
        #''
        url = "http://127.0.0.1:8000/nfl_data/v1/positions/"
        response = requests.post(url)
        print(response.status_code)
        print(response.json())
        return True
    elif args.command.lower() == 'collect':
        url = "http://127.0.0.1:8000/nfl_data/v1/positions/empty"
        response = requests.get(url)
        empty = response.json()

        url = "http://127.0.0.1:8000/nfl_data/v1/positions"
        response = requests.get(url)
        total = len(response.json())

        print(f"{total-empty} of {total} positions have been collected")
    elif args.command.lower() == 'export':
        if args.type.lower() == 'positions':
            url = "http://127.0.0.1:8000/nfl_data/v1/positions/"
        elif args.type.lower() == 'teams':
            url = "http://127.0.0.1:8000/nfl_data/v1/teams/"

        response = requests.get(url)

        data = response.json()
        df = pd.DataFrame(data)
        df = df.set_index("id")
        df.to_csv(args.filename)

    else:
        pass



if __name__ == '__main__':

    main()