#!/usr/bin/env python3

import random as rd

def print_rgb(input, r, g, b):
    print(f"\033[48;2;{r};{g};{b}m"+f"{input}"+"\033[0m")

def format_input(inp):
    sliced = inp.split()
    return [int(string) for string in sliced]

def ask_rgb():
    numbers = [i for i in range(256)]
    i = 1
    while i > 0:
        r = rd.choice(numbers)
        g = rd.choice(numbers)
        b = rd.choice(numbers)
        print("What is this color in rgb?")
        print_rgb("       ", r, g, b)
        print_rgb("       ", r, g, b)
        print_rgb("       ", r, g, b)
        inp = input()
        if len(inp) == 0:
            break
        try:
            inp = format_input(str(inp))
        except: return help()
        print("")
        print("This is your guess:")
        print_rgb("       ", inp[0], inp[1], inp[2])
        print_rgb("       ", inp[0], inp[1], inp[2])
        print_rgb("       ", inp[0], inp[1], inp[2])
        print("The correct values are: ", r, g, b)
        print("Compared to your values:", inp[0], inp[1], inp[2], "\n")

def help():
    print("""Arguments must be passed in the order as shown:    [red] [green] [blue]
             - [red] in int, [0, 255] (no default).
             - [green] in int, [0, 255] (no default).
             - [blue] in int, [0, 255] (no default).""")

if __name__ == "__main__":
    ask_rgb()
