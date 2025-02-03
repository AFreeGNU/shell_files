from datetime import datetime as dt
import random as rd
import math
import sys
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

def ask_pao(all_pairs, save_file):
    if not prompt_start():
        return print("Attempt aborted!")
    start_global = dt.now()
    total_pairs, dnf_count, times, incorrect = process_pairs(all_pairs)
    stop_global = dt.now()
    total_time = stop_global - start_global
    print_stats(total_pairs, dnf_count, times, total_time)
    save_list_to_txt(incorrect, save_file)

def prompt_start():
    print("Push ENTER to start the timer!")
    inp = input()
    return len(inp) == 0

def process_pairs(all_pairs):
    total_pairs, dnf_count = 0, 0
    times, incorrect = [], []
    for letterpair in all_pairs:
        total_pairs += 1
        result = process_single_pair(letterpair)
        if result is None:
            break
        dnf_count += result['dnf']
        times.append(result['time'])
        if result['incorrect']:
            incorrect.append(letterpair)
    return total_pairs, dnf_count, times, incorrect

def process_single_pair(letterpair):
    print(letterpair)
    start = dt.now()
    inp = input()
    stop = dt.now()
    if inp and inp != "o":
        print_table(letterpair, WHITE)
        return None
    time = round(get_seconds(stop - start), 2)
    return evaluate_pair(letterpair, time, inp)

def evaluate_pair(letterpair, time, inp):
    if inp == "o" or time >= 5.0:
        print_table(letterpair, RED)
        return {"time": "DNF", "dnf": 1, "incorrect": True}
    elif time >= 3.0:
        print_table(letterpair, YELLOW)
        return {"time": time, "dnf": 0, "incorrect": False}
    else:
        print_table(letterpair, GREEN)
        return {"time": time, "dnf": 0, "incorrect": False}

def print_table(letterpair, color):
    content_line = pair_dict[letterpair]
    print(f"\033[{color}m" + str(content_line) + "\033[0m") # ]]
    print("")

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

def save_list_to_txt(input_list, save_file):
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
    print("""Arguments must be passed in the order as shown: [pao] [letter_1] [letter_2] [column/row]
             - [pao] is a char in {p, a, o} (default=p).
             - [letter_1] is a char in BLD (default=A).
             - [letter_2] is a char in BLD (default=Z).
             - [column/row] is a char in {c, r} (default=c).""")

if __name__ == "__main__":
    if(len(sys.argv) == 5 and sys.argv[1] in ["p", "a", "o"] and sys.argv[2] in BLD and sys.argv[3] in BLD and sys.argv[4] in ["c", "r"]):

        if sys.argv[1] == "p":
            input_file = "/home/hiesl/shell_files/input_files/pao_person.csv"
            save_file = "/home/hiesl/shell_files/input_files/inc_person.txt"
        elif sys.argv[1] == "a":
            input_file = "/home/hiesl/shell_files/input_files/pao_action.csv"
            save_file = "/home/hiesl/shell_files/input_files/inc_action.txt"
        else:
            input_file = "/home/hiesl/shell_files/input_files/pao_object.csv"
            save_file = "/home/hiesl/shell_files/input_files/inc_object.txt"

        if sys.argv[4] == "r":
            all_pairs = get_rows(sys.argv[2], sys.argv[3])
        else:
            all_pairs = get_columns(sys.argv[2], sys.argv[3])

        with open(input_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            pair_dict = {row[0]: row[1] for row in reader}

        ask_pao(all_pairs, save_file)
    else:
        help()
