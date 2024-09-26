import sys
import argparse
from datetime import datetime

from collectors import Positions, Teams
from collectors.players import Players


def process_args():
    parser = argparse.ArgumentParser(
        prog='nfl_data.py',
        description='What the program does',
        epilog='Text at the bottom of help'
    )

    # TODO: Fill out help etc
    parser.add_argument('command')
    parser.add_argument('--type', required=True)
    parser.add_argument('--start', required=True, type=int)
    parser.add_argument('--end', required=True, type=int)
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
    # TODO constant
    valid_commands = ['collect', 'export']
    if args.command.lower() not in valid_commands:
        raise ValueError('Command must be "collect" or "export"')
    # TODO constants
    data_types = ['all', 'positions', 'teams', 'players', 'games']
    if args.type.lower() not in data_types:
        raise ValueError(f"Type must be one of {data_types}")

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

    if args.type == 'positions':
        position_collector = Positions()
        positions = position_collector.get_data()
        print(f"Total positions {len(positions)}")
    elif args.type == 'teams':
        team_collector = Teams()
        teams = team_collector.get_data(start=args.start, end=args.end)
        print(f"Total teams {len(teams)}")
    elif args.type == 'games':
        pass
    elif args.type == 'players':
        players_collector = Players()
        players = players_collector.get_data(start=args.start, end=args.end)
        #print(players)
        print(f"Total players {len(players)}")
    elif args.type == 'all':
        pass
    else:
        pass




if __name__ == '__main__':
    #try:
    #    main()
    #except ValueError as e:
    #    sys.exit(255) # TODO magic number
    #except Exception as e:
    #    print(e)
    #    sys.exit(255)
    main()