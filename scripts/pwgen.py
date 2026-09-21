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
    "dice-en": Path("/home/hiesl/linux/python_scripts/input_files/dice_en.txt").expanduser(),
    "dice-de": Path("/home/hiesl/linux/python_scripts/input_files/dice_de.txt").expanduser(),
}

def load_wordlist(path):
    return path.read_text().splitlines()

def entropy(n_symbols, length):
    return length * math.log2(n_symbols)

def generate_password(length, alphabet, group=None):
    chars = [secrets.choice(alphabet) for _ in range(length)]
    if group is not None:
        return "-".join("".join(chars[i:i+group]) for i in range(0, len(chars), group))
    return "".join(chars)

def generate_passphrase(n_words, words):
    return "-".join(secrets.choice(words) for _ in range(n_words))

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "length",
        type=int,
        nargs="?",
        default=24,
        help="Password length (default: 24)",
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
        default=4,
        help="Insert dashes every N characters",
    )

    parser.add_argument(
        "--no-group",
        action="store_true",
        help="Disable grouping of the password",
    )

    parser.add_argument(
        "--bits",
        action="store_true",
        help="Print entropy estimate",
    )

    return parser.parse_args()

def main(args):
    charset = args.charset
    if charset in WORDLISTS:
        words = load_wordlist(WORDLISTS[charset])
        password = generate_passphrase(args.length, words)
        bits = entropy(len(words), args.length)
    else:
        alphabet = CHARSETS[charset]
        group = None if args.no_group else args.group
        password = generate_password(args.length, alphabet, group)
        bits = entropy(len(alphabet), args.length)

    print(password)

    if args.bits:
        print(f"Entropy: {bits:.1f} bits")

if __name__ == "__main__":
    args = parse_args()
    main(args)
