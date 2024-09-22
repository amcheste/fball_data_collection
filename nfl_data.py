import sys
import argparse

from collectors import get_positions


def process_args():
    parser = argparse.ArgumentParser(
        prog='nfl_data.py',
        description='What the program does',
        epilog='Text at the bottom of help'
    )

    parser.add_argument('command')
    args = parser.parse_args()
    #TODO Validate args
    print(args)




def main():
    args = process_args()



    positions = get_positions()
    print(f"Total positions {len(positions)}")




if __name__ == '__main__':
    main()