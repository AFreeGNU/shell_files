#!/usr/bin/env python3

import argparse
from datetime import datetime as dt
import random as rd
import math
import csv

BLD = ['A', 'B', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'Z']

WHITE = 37
RED = 31
GREEN = 32
YELLOW = 33

def get_rows(letter1, letter2):
    rows = []
    all_letters = BLD[BLD.index(letter1):BLD.index(letter2)+1]
    for letter in all_letters:
        for i in range(23):
            rows.append(str(letter)+BLD[i])
    rd.shuffle(rows)
    return rows

def get_columns(letter1, letter2):
    columns = []
    all_letters = BLD[BLD.index(letter1):BLD.index(letter2)+1]
    for letter in all_letters:
        for i in range(23):
            columns.append(BLD[i]+str(letter))
    rd.shuffle(columns)
    return columns

def ask_pao(all_pairs, input_file, save_file):
    with open(input_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        pair_dict = {row[0]: row[1] for row in reader}

    if not prompt_start():
        return print("Attempt aborted!")
    start_global = dt.now()
    total_pairs, dnf_count, times, incorrect = process_pairs(all_pairs, pair_dict)
    stop_global = dt.now()
    total_time = stop_global - start_global
    print_stats(total_pairs, dnf_count, times, total_time)
    save_list_to_txt(incorrect, save_file)

def prompt_start():
    print("Push ENTER to start the timer!")
    inp = input()
    return len(inp) == 0

def process_pairs(all_pairs, pair_dict):
    total_pairs, dnf_count = 0, 0
    times, incorrect = [], []
    for letterpair in all_pairs:
        total_pairs += 1
        result = process_single_pair(letterpair, pair_dict)
        if result is None:
            break
        dnf_count += result['dnf']
        times.append(result['time'])
        if result['incorrect']:
            incorrect.append(letterpair)
    return total_pairs, dnf_count, times, incorrect

def process_single_pair(letterpair, pair_dict):
    print(letterpair)
    start = dt.now()
    inp = input()
    stop = dt.now()
    if inp and inp != "o":
        print_table(pair_dict[letterpair], WHITE)
        return None
    time = round((stop - start).total_seconds(), 2)
    return evaluate_pair(pair_dict[letterpair], time, inp)

def evaluate_pair(content_line, time, inp):
    if inp == "o" or time >= 5.0:
        print_table(content_line, RED)
        return {"time": "DNF", "dnf": 1, "incorrect": True}
    elif time >= 3.0:
        print_table(content_line, YELLOW)
        return {"time": time, "dnf": 0, "incorrect": False}
    else:
        print_table(content_line, GREEN)
        return {"time": time, "dnf": 0, "incorrect": False}

def print_table(content_line, color):
    print(f"\033[{color}m" + str(content_line) + "\033[0m") # ]]
    print("")

def print_stats(total_pairs, dnf_count, times, total_time):
    accuracy = get_accuracy(total_pairs, dnf_count)
    print(f"You got {total_pairs-dnf_count}/{total_pairs} pairs correct ({accuracy}%).")
    print(f"You took {format_time(total_time.total_seconds())}.")
    avg = average(times)
    if avg == "DNF":
        print("The average is a DNF!")
    elif avg == "Too short for average.":
        print("Too short for average.")
    else:
        print("Average of", total_pairs, "is", avg, "seconds.")

def get_accuracy(total_pairs, dnf_count):
    accuracy = (total_pairs-dnf_count)/total_pairs
    return round(100*accuracy, 1)

def save_list_to_txt(input_list, save_file):
    with open(save_file, 'a') as file:
        rd.shuffle(input_list)
        for item in input_list:
            file.write(str(item) + '\n')

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02}:{int(minutes):02}:{seconds:05.2f}"

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
        return "Too short for average."
    num_bad = number - num_dnf
    for _ in range(num_dnf):
        values.remove("DNF")
    values.sort()
    for _ in range(num_bad):
        values.pop(-1)
    for _ in range(number):
        values.pop(0)
    return round(sum(values)/len(values), 2)

def main():
    parser = argparse.ArgumentParser(
        description="Program for learing a PAO system."
    )

    parser.add_argument(
        "--pao",
        choices=["p", "a", "o"],
        default="p",
        help="person (p), action (a), or object (o) (default: %(default)s)",
    )

    parser.add_argument(
        "--upper",
        choices=BLD,
        default="A",
        help="upper bound letter",
    )

    parser.add_argument(
        "--lower",
        choices=BLD,
        default="Z",
        help="lower bound letter",
    )

    parser.add_argument(
        "--row",
        action="store_true",
        help="use rows instead of columns",
    )

    args = parser.parse_args()
    if args.pao == "p":
        input_file = "/home/hiesl/linux/shell_files/input_files/pao_person.csv"
        save_file = "/home/hiesl/linux/shell_files/input_files/inc_person.txt"
    elif args.pao == "a":
        input_file = "/home/hiesl/linux/shell_files/input_files/pao_action.csv"
        save_file = "/home/hiesl/linux/shell_files/input_files/inc_action.txt"
    else:
        input_file = "/home/hiesl/linux/shell_files/input_files/pao_object.csv"
        save_file = "/home/hiesl/linux/shell_files/input_files/inc_object.txt"

    if args.row:
        all_pairs = get_rows(args.upper, args.lower)
    else:
        all_pairs = get_columns(args.upper, args.lower)

    ask_pao(all_pairs, input_file, save_file)

if __name__ == "__main__":
    main()
