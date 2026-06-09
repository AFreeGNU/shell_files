#!/usr/bin/env python3

import argparse
import math
import secrets
import string
from pathlib import Path

CHARSETS = {
    "ascii": string.ascii_letters + string.digits + string.punctuation,
    "num_cs": string.ascii_letters + string.digits,
    "num_ci": string.ascii_lowercase + string.digits,
    "cs": string.ascii_letters,
    "ci": string.ascii_lowercase,
    "num": string.digits,
    "bin": "01",
    "pao": "abdefghijklmnopqrstuvwx",
}

WORDLISTS = {
    "dice-en": Path("/home/hiesl/linux/shell_files/input_files/dice_en.txt").expanduser(),
    "dice-de": Path("/home/hiesl/linux/shell_files/input_files/dice_de.txt").expanduser(),
}

def load_wordlist(path):
    return Path(path).read_text().splitlines()

def entropy(n_symbols, length):
    return length * math.log2(n_symbols)

def generate_password(length, alphabet, group=None):
    chars = [secrets.choice(alphabet) for _ in range(length)]
    if group is not None:
        return "-".join("".join(chars[i:i+group]) for i in range(0, len(chars), group))
    return "".join(chars)

def generate_passphrase(n_words, words):
    return "-".join(secrets.choice(words) for _ in range(n_words))

parser = argparse.ArgumentParser()

parser.add_argument(
    "length",
    type=int,
    nargs="?",
    default=25,
    help="Password length (default: 25)",
)

parser.add_argument(
    "--charset",
    choices=list(CHARSETS) + list(WORDLISTS),
    default="num_cs",
    help="Select character set",
)

parser.add_argument(
    "--group",
    type=int,
    help="Insert dashes every N characters",
)

parser.add_argument(
    "--bits",
    action="store_true",
    help="Print entropy estimate",
)

args = parser.parse_args()

def main():

    charset = args.charset

    if charset in WORDLISTS:
        words = WORDLISTS[charset].read_text().splitlines()
        password = generate_passphrase(args.length, words)
        H = entropy(len(words), args.length)
    else:
        alphabet = CHARSETS[charset]
        password = generate_password(args.length, alphabet, args.group)
        H = entropy(len(alphabet), args.length)

    print(password)

    if args.bits:
        print(f"Entropy: {H:.1f} bits")

if __name__ == "__main__":
    main()
