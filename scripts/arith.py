#!/usr/bin/env python3

import argparse
import random as rd
import datetime as dt
import math

RED = "\033[1;31m"
GREEN = "\033[1;32m"
RESET = "\033[0m"

def calculate(a, b, operation):
    if operation == "mul": return a * b
    if operation == "add": return a + b
    if operation == "sub": return a - b
    if operation == "pow": return a**b

def is_trivial(a, b, operation):
    if operation == "mul":
        return a == 1 or b == 1
    if operation == "add":
        return a == 0 or b == 0
    if operation == "sub":
        return b == 0
    if operation == "pow":
        return b in (0, 1) or a in (0, 1)
    return False

def generate_operands(operation, decimals_1, decimals_2):
    while True:
        a = rd.randint(10**(decimals_1 - 1), 10**decimals_1 - 1)
        b = rd.randint(10**(decimals_2 - 1), 10**decimals_2 - 1)

        if operation == "pow":
            b = decimals_2

        if not is_trivial(a, b, operation):
            return a, b

def generate_exhaustive_multiplication():
    """Generate all 1-digit multiplication pairs in random order."""
    pairs = [
        (a, b)
        for a in range(2, 10)
        for b in range(2, 10)
    ]
    rd.shuffle(pairs)
    return pairs

def calculation(operation, decimals_1, decimals_2, max_attempts, exhaustive=False):

    operation_dict = {
        "add": "+",
        "sub": "-",
        "mul": "*",
        "pow": "^"
    }

    # Exhaustive mode is only applicable to 1-digit multiplication.
    exhaustive_mode = (
        exhaustive
        and operation == "mul"
        and decimals_1 == 1
        and decimals_2 == 1
    )

    if exhaustive_mode:
        questions = generate_exhaustive_multiplication()
        max_attempts = min(max_attempts, len(questions))
    else:
        questions = None

    i = 1
    times = []

    print("Push ENTER to start the timer!")
    inp = input()

    if len(inp) == 0:
        start_global = dt.datetime.now()
        count = 0
        global_count = 0

        while i > 0:

            # Get next question
            if exhaustive_mode:
                number_1, number_2 = questions[global_count]
            else:
                number_1, number_2 = generate_operands(
                    operation, decimals_1, decimals_2
                )

            print(number_1, operation_dict[operation], number_2)

            result = calculate(number_1, number_2, operation)

            start = dt.datetime.now()
            inp = input()

            try:
                int(inp)
            except:
                return print(
                    f"Attempt aborted! The correct answer would have been: "
                    f"{result}."
                )

            if len(inp) == 0:
                break

            stop = dt.datetime.now()
            seconds = round((stop - start).total_seconds(), 2)

            if int(inp) == result:
                times.append(seconds)
                count += 1
                global_count += 1
                print(f"{GREEN}Correct!{RESET} You took {seconds} seconds.\n")
            else:
                times.append("DNF")
                global_count += 1
                print(
                    f"{RED}Wrong!{RESET} Answer: {result}. "
                    f"You took {seconds} seconds.\n"
                )

            if global_count == max_attempts:
                break

        stop_global = dt.datetime.now()
        global_time = stop_global - start_global

        print(f"\nYou got {count} of {global_count} correct "
              f"in {global_time}.")

        if count != 0:
            print("Ratio:", round(global_time.total_seconds() / count, 2))
            print(f"Average of {len(times)} is {average(times)}.")

    else:
        print("Attempt aborted!")

def count_list(lst, x):
    count = 0
    for ele in lst:
        if ele == x:
            count += 1
    return count

def average(values):
    length = len(values)
    number = math.ceil(0.05 * length)
    num_dnf = count_list(values, "DNF")

    if num_dnf > number:
        return "DNF"

    if len(values) < 2:
        return "Too short for average."

    num_bad = number - num_dnf

    for _ in range(num_dnf):
        values.remove("DNF")

    values.sort()

    for _ in range(num_bad):
        values.pop(-1)

    for _ in range(number):
        values.pop(0)

    return round(sum(values) / len(values), 2)

def parse_args():
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

    parser.add_argument(
        "--exhaustive",
        action="store_true",
        help="for 1-digit multiplication, use all 81 pairs once "
             "in random order",
    )

    return parser.parse_args()

def main(args):
    calculation(
        args.operation,
        args.decimals1,
        args.decimals2,
        args.attempts,
        args.exhaustive,
    )

if __name__ == "__main__":
    args = parse_args()
    main(args)
