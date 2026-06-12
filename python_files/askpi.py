#!/usr/bin/env python3

import argparse
import datetime as dt
from pathlib import Path

PI_PATH = "/home/hiesl/linux/shell_files/input_files/pi.txt"

def load_pi():
    return Path(PI_PATH).read_text().strip()

def pao(pi, start, w_pos):
    if w_pos % 6 == 0:
        w_pos -= 1
    block = start + (w_pos // 6) * 6
    return pi[block:block + 6]

def in_inp(inp, i, offset):
    if (i + offset + 1) % 6 == 0:
        i -= 1
    skip = ((i + offset) // 6) * 6 - offset
    return inp[skip:skip + 6]

def check_pattern(inp, pi, i, start, offset, lengths):
    """Check if inp[i:i+len(lengths)] matches pi shifted by each candidate offset."""
    for shift in lengths:
        try:
            if all(inp[i + k] == pi[i + start + offset + shift + k] for k in range(3)):
                return shift
        except IndexError:
            continue
    return None

def analyze_mistakes(inp, pi, start, mistake_limit):
    mistake_count = 0
    offset = 0
    reported_first = False

    i = 0
    while i < len(inp):
        if inp[i] == pi[i + start + offset]:
            i += 1
            continue

        if not reported_first and mistake_count + offset == 0:
            print(f"Only the first {i} digits of pi were correct.")
            reported_first = True

        pos = i + offset + 1

        # 1 digit missed
        if check_pattern(inp, pi, i, start, offset, [1]) is not None:
            missed = pi[i + start + offset]
            print(f"You missed digit {pos}, which is: {missed} (PAO: {pao(pi, start, pos)}) in: {in_inp(inp, i, offset)}")
            offset += 1
            mistake_count += 1

        # 2 digits missed
        elif check_pattern(inp, pi, i, start, offset, [2]) is not None:
            missed = pi[i+start+offset:i+start+offset+2]
            print(f"You missed two digits {pos} and {pos+1}, which are: {missed} (PAO: {pao(pi, start, pos)})")
            offset += 2
            mistake_count += 1

        # 6 digits missed
        elif check_pattern(inp, pi, i, start, offset, [6]) is not None:
            missed = pi[i+start+offset:i+start+offset+6]
            print(f"You missed six digits between {pos} and {pos+5}, which are: {missed}")
            offset += 6
            mistake_count += 1

        # extra digit inserted
        elif i + 3 < len(inp) and all(inp[i+1+k] == pi[i+start+offset+k] for k in range(3)):
            print(f"You added a digit between {pos-1} and {pos} (PAO: {pao(pi, start, pos)}) in: {in_inp(inp, i, offset)}")
            offset -= 1
            mistake_count += 1

        # simple substitution error
        else:
            expected = pi[i + start + offset]
            print(f"You got position {pos} wrong: {inp[i]} should be {expected} (PAO: {pao(pi, start, pos)}) in: {in_inp(inp, i, offset)}")
            mistake_count += 1

        if mistake_count >= mistake_limit:
            print("Too many mistakes!")
            return mistake_count, offset, True

        i += 1

    return mistake_count, offset, False


def ask_pi(pi, start_digit=0, mistake_limit=20):
    print("Push ENTER to start the timer!")
    if input() != "":
        print("Attempt aborted!")
        return

    print(f"Start from digit {start_digit}!")
    start_time = dt.datetime.now()
    inp = input()
    stop_time = dt.datetime.now()

    if inp == pi[start_digit:start_digit + len(inp)]:
        print("\nEverything is correct!")
        print(f"You learned: {len(inp)} digits of pi.")
    else:
        print("\nIncorrect!")
        mistakes, offset, aborted = analyze_mistakes(inp, pi, start_digit, mistake_limit)
        if not aborted:
            total = len(inp) + offset
            print(f"You got a total of {len(inp) - mistakes} digits of {total} correct!")
        else:
            print("You took:", stop_time - start_time)
            return

    print("You took:", stop_time - start_time)

def main():
    parser = argparse.ArgumentParser(
        description="Practice the Doomsday algorithm."
    )

    parser.add_argument(
        "-s", "--start",
        type=int,
        default=0,
        help="start digit (default: %(default)s)",
    )

    parser.add_argument(
        "--mistake-limit",
        type=int,
        default=20,
        help="mistake limit (default: %(default)s)",
    )

    args = parser.parse_args()

    pi_digits = load_pi()
    ask_pi(pi_digits, args.start, args.mistake_limit)

if __name__ == "__main__":
    main()
