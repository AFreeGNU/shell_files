from datetime import datetime as dt
import random as rd
import math
import sys
import csv

input_file = "/home/hiesl/shell_files/input_files/letterpairs.csv"
save_file = "/home/hiesl/shell_files/input_files/incorrect_letterpairs.txt"

WHITE = 37
RED = 31
GREEN = 32
YELLOW = 33

def read_list_from_txt():
    output_list = []
    with open(save_file, 'r') as file:
        for line in file:
            output_list.append(line.strip())
    return output_list

def clear_txt_file():
    with open(save_file, 'w') as _:
        pass

def ask_letterpairs(all_pairs):
    if not prompt_start():
        return print("Attempt aborted!")
    start_global = dt.now()
    total_pairs, dnf_count, times, incorrect = process_pairs(all_pairs)
    stop_global = dt.now()
    total_time = stop_global - start_global
    print_stats(total_pairs, dnf_count, times, total_time)
    clear_txt_file()
    save_list_to_txt(incorrect)

def prompt_start():
    print("Push ENTER to start the timer!")
    inp = input()
    return len(inp) == 0

def process_pairs(all_pairs):
    total_pairs, dnf_count = 0, 0
    times, incorrect = [], []
    for pair in all_pairs:
        total_pairs += 1
        result = process_single_pair(pair)
        if result is None:
            break
        dnf_count += result['dnf']
        times.append(result['time'])
        if result['incorrect']:
            incorrect.append(pair)
    return total_pairs, dnf_count, times, incorrect

def process_single_pair(pair):
    print(pair)
    start = dt.now()
    inp = input()
    stop = dt.now()
    if inp and inp != "o":
        print_table(pair, WHITE)
        return None
    time = round(get_seconds(stop - start), 2)
    return evaluate_pair(pair, time, inp)

def evaluate_pair(pair, time, inp):
    if inp == "o" or time >= 5.0:
        print_table(pair, RED)
        return {"time": "DNF", "dnf": 1, "incorrect": True}
    elif time >= 3.0:
        print_table(pair, YELLOW)
        return {"time": time, "dnf": 0, "incorrect": False}
    else:
        print_table(pair, GREEN)
        return {"time": time, "dnf": 0, "incorrect": False}

def print_table(pair, color):
    print(f"\033[{color}m" + str(pair_dict[pair]) + "\033[0m\n")

def print_stats(total_pairs, dnf_count, times, total_time):
    accuracy = get_accuracy(total_pairs, dnf_count)
    print(f"You got {total_pairs-dnf_count}/{total_pairs} pairs correct ({accuracy}%).")
    print(f"You took {format_time(get_seconds(total_time))}.")
    avg = average(times)
    if avg == "DNF":
        print("The average is a DNF!")
    elif avg == "To short for average.":
        print("To short for average.")
    else:
        print("Average of", total_pairs, "is", avg, "seconds.")

def get_accuracy(total_pairs, dnf_count):
    accuracy = (total_pairs-dnf_count)/total_pairs
    return round(100*accuracy, 1)

def save_list_to_txt(input_list):
    with open(save_file, 'a') as file:
        rd.shuffle(input_list)
        for item in input_list:
            file.write(str(item) + '\n')

def get_seconds(time):
    digits = [int(c) for c in str(time) if c.isdigit()]
    seconds = (
        digits[0] * 3600 +
        digits[1] * 600 +
        digits[2] * 60 +
        digits[3] * 10 +
        digits[4] +
        digits[5] * 0.1 +
        digits[6] * 0.01
    )
    return seconds

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
        return "To short for average."
    num_bad = number - num_dnf
    for _ in range(num_dnf):
        values.remove("DNF")
    values.sort()
    for _ in range(num_bad):
        values.pop(-1)
    for _ in range(number):
        values.pop(0)
    return round(sum(values)/len(values), 2)

def help():
    print("""No arguments can be passed.
             This command just asks the incorrect letterpairs
             found in ~/.shell_files/input_files/incorrect_letterpairs.txt.""")

if __name__ == "__main__":
    with open(input_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        row = next(reader)
    pair_dict = {}
    for i in range(0, len(row), 2):
        pair_dict[row[i]] = row[i+1]

    if(len(sys.argv) == 1):
        all_pairs = read_list_from_txt()
        if all_pairs:
            ask_letterpairs(all_pairs)
        else:
            print("""Incorrect letterpair list is empty.""")
    else:
        help()
