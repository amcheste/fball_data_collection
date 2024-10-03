import argparse
from datetime import datetime
import pika
import requests

from app.utils import database
from app.lib.positions import collect_all_positions, collect_positions
from app.lib.teams import collect_teams
from app.lib.players import collect_players

def process_args():
    parser = argparse.ArgumentParser(
        prog='nfl_data_collector.py',
        description='What the program does',
        epilog='Text at the bottom of help'
    )
    parser.add_argument('--type', required=True)
    parser.add_argument('--mode', required=True)
    parser.add_argument('--num', type=int)


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

    # TODO constants
    data_types = ['positions', 'teams', 'players', 'games']
    if args.type.lower() not in data_types:
        raise ValueError(f"Type must be one of {data_types}")


    mode_types = ['all', 'partial', 'daemon']
    if args.mode.lower() not in mode_types:
        pass

    if args.num and args.mode.lower() != 'partial':
        pass

def main():
    args = process_args()

    if args.type.lower() == 'positions':
        #collect_all_positions()
        collect_positions()
    elif args.type.lower() == 'teams':
        collect_teams()
    elif args.type.lower() == 'players':
        collect_players()









if __name__ == '__main__':
    #try:
    #    main()
    #except ValueError as e:
    #    sys.exit(255) # TODO magic number
    #except Exception as e:
    #    print(e)
    #    sys.exit(255)
    main()