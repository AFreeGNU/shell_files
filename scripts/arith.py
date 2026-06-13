#!/usr/bin/env python3

import argparse
import random as rd
import datetime as dt
import math

def calculate(a, b, operation):
    if operation == "mul": return a * b
    if operation == "add": return a + b
    if operation == "sub": return a - b
    if operation == "pow": return a**b

def calculation(operation, decimals_1, decimals_2, max_attempts):
    operation_dict = {"add" : "+", "sub" : "-", "mul" : "*", "pow" : "^"}
    i = 1
    times = []
    print("Push ENTER to start the timer!")
    inp = input()
    if len(inp) == 0:
        start_global = dt.datetime.now()
        count = 0
        global_count = 0
        while i > 0:
            number_1 = rd.randint(10**(decimals_1 - 1), 10**decimals_1 - 1)
            number_2 = rd.randint(10**(decimals_2 - 1), 10**decimals_2 - 1)
            if operation == "pow":
                number_2 = decimals_2
            print(number_1, operation_dict[operation], number_2)
            result = calculate(number_1, number_2, operation)
            start = dt.datetime.now()
            inp = input()
            try:
                int(inp)
            except:
                return print(f"Attempt abortet! The correct answer would have been: {result}.")
            if len(inp) == 0:
                break
            stop = dt.datetime.now()
            seconds = round((stop - start).total_seconds(), 2)
            if int(inp) == result:
                times.append(seconds)
                count += 1
                global_count += 1
                print(f"Correct! You took {seconds} seconds.\n")
            else:
                times.append("DNF")
                global_count += 1
                print(f"Wrong! Answer: {result}. You took {seconds} seconds.\n")
            if  global_count == max_attempts:
                break
        stop_global = dt.datetime.now()
        global_time = stop_global - start_global
        print(f"\nYou got {count} of {global_count} correct in {global_time}.")
        if count != 0:
            print("Ratio:", round(global_time.total_seconds() / count, 2))
            print(f"Average of {len(times)} is {average(times)}.")
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
    if len(values) < 2:
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
        description="Practice arithmetic."
    )

    parser.add_argument(
        "-n", "--attempts",
        type=int,
        default=5,
        help="number of questions (default: %(default)s)",
    )

    parser.add_argument(
        "--decimals1",
        type=int,
        default=2,
        help="number of digits in the first operand (default: %(default)s)",
    )

    parser.add_argument(
        "--decimals2",
        type=int,
        default=1,
        help="number of digits in the second operand (default: %(default)s)",
    )

    parser.add_argument(
        "-o", "--operation",
        choices=["add", "sub", "mul", "pow"],
        default="mul",
        help="operation to practice (default: %(default)s)",
    )

    args = parser.parse_args()

    calculation(args.operation, args.decimals1, args.decimals2, args.attempts)

if __name__ == "__main__":
    main()
