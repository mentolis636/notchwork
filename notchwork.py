#!/usr/bin/env python3
"""
notchwork.py - Notchwork, a six-rotor cipher machine with a notch key.

The machine encodes letters A-Z and digits 0-9 (36 symbols). Lowercase input
is converted to uppercase. Spaces and punctuation pass through unchanged.

Two settings make up the key. Sender and receiver must enter the same values,
or the message will not decode:

  NOTCHES          6 symbols, one per rotor (e.g. L-I-G-W-M-C or 7-K-2-W-M-9).
                   Each symbol is the notch of that rotor: the position at
                   which the rotor pushes its left-hand neighbour one step
                   forward. Agree on these in advance and change them regularly.

  START POSITION   6 symbols, one per rotor (e.g. S-S-S-S-S-S). The window
                   setting each rotor begins from. Enter it fresh for every
                   message.

Both groups read left to right: rotor 1 on the left, rotor 6 (the fast one)
on the right. Symbols can be separated by dashes, commas or spaces.

The machine is reciprocal, so encoding and decoding are the same operation.

Usage:
  python notchwork.py "MEET AT 21:30" --notches LIGWMC --start SSSSSS
  python notchwork.py "<ciphertext>" --notches LIGWMC --start SSSSSS
  python notchwork.py --interactive

Educational project. Do not use it to protect real secrets.
"""

import argparse
import re
import string
import sys

MACHINE_NAME = "Notchwork"  # change this to rename the machine

ALPHABET = string.ascii_uppercase + string.digits  # 36 symbols
SIZE = len(ALPHABET)
NUM_ROTORS = 6

# Eight original rotor wirings over the 36 symbols. Choose six with --rotors
# (default: 1-6).
ROTOR_WIRINGS = {
    "1": "D5QELP7A8CI3JT0FVZ2W6YOUB94S1RNXGKHM",
    "2": "YSWFX5O17RZAPBDH0VI2GM4U9JKNEC8Q36LT",
    "3": "1CBF850ZKYLAUXMJ2WNDOIGQ6HRSTE3V94P7",
    "4": "GX4O965SAHIEN10UPZ7RKBYQL2J8FMWC3DTV",
    "5": "KZDF508LWV12GJQSOCH469IM3R7AYEUBXPNT",
    "6": "2KGE348IQWUDTBZFXAPCVOLHN6S90RJ7Y5M1",
    "7": "Z3FY6K4SEG2J5TUWLA8O7Q1CIBVXD0MRN9HP",
    "8": "DMBLQK5YTZSP76CU08AEW9G24RVO3JHX1IFN",
}
# Pairs symbols off so that none maps to itself and the mapping is its own
# inverse. That property makes encoding and decoding identical.
REFLECTOR = "YV7ZJ210SE5W9ON46TIR8BL3ADHGFXPKQCUM"


def to_index(symbol: str) -> int:
    return ALPHABET.index(symbol)


def parse_symbols(value: str, label: str) -> str:
    """Accept 'LIGWMC', 'L-I-G-W-M-C' or 'L I G W M C'; return 'LIGWMC'."""
    cleaned = re.sub(r"[\s\-,]", "", value).upper()
    if len(cleaned) != NUM_ROTORS or not all(c in ALPHABET for c in cleaned):
        raise ValueError(f"{label} must be exactly {NUM_ROTORS} symbols, each a "
                         f"letter A-Z or a digit 0-9 (example: {'-'.join('LIGWMC')}).")
    return cleaned


class Rotor:
    def __init__(self, name: str, notch: str, position: str):
        wiring = ROTOR_WIRINGS[name]
        self.name = name
        self.forward = [to_index(c) for c in wiring]
        self.backward = [0] * SIZE
        for i, out in enumerate(self.forward):
            self.backward[out] = i
        self.notch = to_index(notch)
        self.position = to_index(position)

    def at_notch(self) -> bool:
        return self.position == self.notch

    def step(self) -> None:
        self.position = (self.position + 1) % SIZE

    def encode_forward(self, index: int) -> int:
        return (self.forward[(index + self.position) % SIZE] - self.position) % SIZE

    def encode_backward(self, index: int) -> int:
        return (self.backward[(index + self.position) % SIZE] - self.position) % SIZE


class RotorMachine:
    def __init__(self, notches: str, start: str, rotors=None):
        notches = parse_symbols(notches, "Notches")
        start = parse_symbols(start, "Start position")
        rotors = [str(r) for r in (rotors or ["1", "2", "3", "4", "5", "6"])]

        if len(rotors) != NUM_ROTORS or len(set(rotors)) != NUM_ROTORS:
            raise ValueError(f"Choose {NUM_ROTORS} different rotors from 1-8.")
        for name in rotors:
            if name not in ROTOR_WIRINGS:
                raise ValueError(f"Unknown rotor '{name}'. Pick from 1-8.")

        # Users read left to right; index 0 here is the fast, rightmost rotor.
        self.rotors = [
            Rotor(name, notch, pos)
            for name, notch, pos in zip(reversed(rotors), reversed(notches), reversed(start))
        ]
        self.reflector = [to_index(c) for c in REFLECTOR]

    def _step_rotors(self) -> None:
        """Odometer stepping: the fast rotor always moves, and each other rotor
        moves when the rotor on its right sits on its notch."""
        at_notch = [r.at_notch() for r in self.rotors]
        for i, rotor in enumerate(self.rotors):
            if i == 0 or at_notch[i - 1]:
                rotor.step()

    def encode_symbol(self, symbol: str) -> str:
        self._step_rotors()
        i = to_index(symbol)
        for rotor in self.rotors:
            i = rotor.encode_forward(i)
        i = self.reflector[i]
        for rotor in reversed(self.rotors):
            i = rotor.encode_backward(i)
        return ALPHABET[i]

    def process(self, text: str, keep_other: bool = True) -> str:
        out = []
        for ch in text.upper():
            if ch in ALPHABET:
                out.append(self.encode_symbol(ch))
            elif keep_other:
                out.append(ch)
        return "".join(out)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=f"{MACHINE_NAME}: six rotors, notch key.")
    p.add_argument("text", nargs="?", help="message to encode or decode")
    p.add_argument("--notches", help="6-symbol notch setting, e.g. LIGWMC or L-I-G-W-M-C")
    p.add_argument("--start", help="6-symbol start position, e.g. SSSSSS")
    p.add_argument("--rotors", nargs=NUM_ROTORS, metavar="R",
                   help="six rotors from 1-8, left to right (default: 1 2 3 4 5 6)")
    p.add_argument("--strip", action="store_true",
                   help="drop spaces and punctuation, output letters and digits only")
    p.add_argument("--interactive", action="store_true", help="prompt for every setting")
    return p


def prompt_symbols(label: str, hint: str) -> str:
    while True:
        raw = input(f"{label} (6 letters or digits, e.g. {hint}): ")
        try:
            return parse_symbols(raw, label)
        except ValueError as err:
            print(f"  {err}")


def main() -> int:
    args = build_parser().parse_args()

    if args.interactive or not (args.notches and args.start and args.text):
        print(f"{MACHINE_NAME}. Both sides must enter the same notches\n"
              "and the same start position, or decoding fails.\n")
        if not args.notches or args.interactive:
            args.notches = prompt_symbols("Notches","L-I-G-W-M-C")
        if not args.start or args.interactive:
            args.start = prompt_symbols("Start position", "S-S-S-S-S-S")
        if not args.text or args.interactive:
            args.text = input("Message: ")

    try:
        machine = RotorMachine(args.notches, args.start, args.rotors)
    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    print(machine.process(args.text, keep_other=not args.strip))
    return 0


if __name__ == "__main__":
    sys.exit(main())
