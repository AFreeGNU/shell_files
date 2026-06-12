#!/usr/bin/env python3

import argparse
from datetime import datetime

def give_weekday(day, month, year):
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    date = datetime(year, month, day)
    print(f"The {day}.{month}.{year} is a {weekdays[date.weekday()]}.")

def main():
    parser = argparse.ArgumentParser(
        description="Get the weekday for any date."
    )

    parser.add_argument(
        "-d", "--day",
        type=int,
        required=True,
        help="day of the date",
    )

    parser.add_argument(
        "-m", "--month",
        type=int,
        required=True,
        help="month of the date",
    )

    parser.add_argument(
        "-y", "--year",
        type=int,
        required=True,
        help="year of the date",
    )

    args = parser.parse_args()

    give_weekday(args.day, args.month, args.year)

if __name__ == "__main__":
    main()
