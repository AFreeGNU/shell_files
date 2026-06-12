#!/usr/bin/env python3

import argparse
import numpy as np
import datetime as dt
from pathlib import Path

PI_PATH = "/home/hiesl/linux/shell_files/input_files/pi.txt"

def load_pi():
    return Path(PI_PATH).read_text().strip()

def give_pao(table, n1, n2, place):
    return str(table[int(n1)+3*int(n1)+1+place, int(n2)])

def learn_pi(pi, table, skip, pao, max_digit):
    i = 1
    pos = skip
    total = 0
    print(f"Push ENTER to start at digit {skip}!")
    enter = input()
    if len(enter) == 0:
        start = dt.datetime.now()
    else: return print("Attempt aborted!")
    while i > 0 and not pos >= max_digit:
        number = f"{pi[pos]}{pi[pos+1]} {pi[pos+2]}{pi[pos+3]} {pi[pos+4]}{pi[pos+5]}"
        pao_pair  = give_pao(table, pi[pos],   pi[pos+1], 0) + " "
        pao_pair += give_pao(table, pi[pos+2], pi[pos+3], 1) + " "
        pao_pair += give_pao(table, pi[pos+4], pi[pos+5], 2)
        print(number)
        if pao:
            print(pao_pair)
        total += 1
        pos += 6
        x = input()
        i = len(x)
        if i != 0:
            break
        else: i = 1
    stop = dt.datetime.now()
    print("You learned: ", 6 * total, " digits of pi.")
    print("You took: ", stop - start)

def main():
    parser = argparse.ArgumentParser(
        description="Practice the Doomsday algorithm."
    )

    parser.add_argument(
        "-s", "--skip",
        type=int,
        default=0,
        help="skip digits (default: %(default)s)",
    )

    parser.add_argument(
        "--max-digit",
        type=int,
        default=10000,
        help="maximum digit (default: %(default)s)",
    )

    parser.add_argument(
        "--pao",
        action="store_true",
        help="show pao pairs (default: %(default)s)",
    )

    args = parser.parse_args()

    pi_digits = load_pi()
    table =  np.genfromtxt("/home/hiesl/linux/shell_files/input_files/pao0099.csv", delimiter=',', dtype= str)[:,1:]
    learn_pi(pi_digits, table, args.skip, args.max_digit, args.pao)

if __name__ == "__main__":
    main()
