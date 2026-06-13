#!/usr/bin/env python3

import argparse
from datetime import datetime
import math
import random as rd

def get_anchor(year):
    century = math.floor(year / 100)
    century_anchor = (5 * (century % 4)) % 7 + 2
    decade = year - century * 100
    if decade % 2 != 0: decade += 11
    decade /= 2
    if decade % 2 != 0: decade += 11
    decade_anchor = 7 - (decade % 7)
    return int((decade_anchor + century_anchor) % 7)

def is_leap(year):
    if year % 4 != 0:
        return False
    if year % 100 == 0 and year % 400 != 0:
        return False
    return True

def rd_date(min_year, max_year):
    rd_year = rd.randint(min_year, max_year)
    rd_month = rd.randint(1, 12)
    offset = 0
    if is_leap(rd_year):
        offset = 1
    if rd_month in [1, 3, 5, 7, 8, 10, 12]:
        rd_day = rd.randint(1, 31)
    if rd_month in [4, 6, 9, 11]:
        rd_day = rd.randint(1, 30)
    else:
        rd_day = rd.randint(1, 28 + offset)
    return [rd_day, rd_month, rd_year]

def print_date(date):
    print(f"{date[0]}.{date[1]}.{date[2]}")

def get_weekday(date):
    date = datetime(date[2], date[1], date[0])
    return date.weekday()

def ask_date(max_attempts, min_year, max_year):
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = []
    print("Push ENTER to start the timer!")
    inp = input()
    if len(inp) == 0:
        start_global = datetime.now()
        count = 0
        global_count = 0
        for _ in range(max_attempts):
            date = rd_date(min_year, max_year)
            start = datetime.now()
            print_date(date)
            day = get_weekday(date)
            anchor = get_anchor(date[2])
            inp = input()
            try:
                int(inp)
            except:
                print("Attempt abortet!")
                print(f"The correct weekday would have been {weekdays[day]}. Anchor: {anchor}.")
                break
            if int(inp) > 7 or int(inp) < 0:
                print("Attempt abortet!")
                print(f"The correct weekday would have been {weekdays[day]}. Anchor: {anchor}.")
                break
            stop = datetime.now()
            seconds = round((stop-start).total_seconds(), 2)
            if int(inp) % 7 == (day + 1) % 7:
                count += 1
                global_count += 1
                times.append(seconds)
                print(f"Correct! It is a {weekdays[day]}. You took: {seconds} seconds. Anchor: {anchor}.\n")
            else:
                global_count += 1
                times.append("DNF")
                print(f"Wrong! The correct weekday is: {weekdays[day]}. You took: {seconds} seconds. Anchor: {anchor}.\n")
        stop_global = datetime.now()
        global_time = stop_global - start_global
        print(f"You got {count} of {global_count} correct in {global_time}.")
        if count > 1:
            print(f"Ratio: {round(global_time.total_seconds() / count, 2)} Seconds/Date")
            print(f"Average of {len(times)} is: {average(times)}")
    else: return print("Attempt aborted!")

def count_list(lst, x):
    count = 0
    for ele in lst:
        if ele == x:
            count += 1
    return count

def average(values):
    length = len(values)
    number = math.ceil(0.05*length)
    num_dnf = count_list(values, "DNF")
    if num_dnf > number:
        return "DNF"
    if len(values) <= 2:
        return "To short for average."
    num_bad = number - num_dnf
    for _ in range(num_dnf):
        values.remove("DNF")
    values.sort()
    for _ in range(num_bad):
        values.pop(-1)
    for _ in range(number):
        values.pop(0)
    return round(sum(values)/len(values),2)

def main():
    parser = argparse.ArgumentParser(
        description="Practice the Doomsday algorithm."
    )

    parser.add_argument(
        "-n", "--attempts",
        type=int,
        default=5,
        help="number of questions to ask (default: %(default)s)",
    )

    parser.add_argument(
        "--min-year",
        type=int,
        default=1600,
        help="earliest year to use (default: %(default)s)",
    )

    parser.add_argument(
        "--max-year",
        type=int,
        default=2300,
        help="latest year to use (default: %(default)s)",
    )

    args = parser.parse_args()

    ask_date(args.attempts, args.min_year, args.max_year)

if __name__ == "__main__":
    main()
